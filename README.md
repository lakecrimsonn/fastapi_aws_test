# fastapi - aws lambda - github actions cicd

## 깃허브 레포지토리 생성

- 깃허브 데스크탑으로 생성해보았음
- file - new repository → 새로운 이름지어주기 → 로컬 위치 신경써서 정해주기
- publish repository → keep this code private 해제해주기
- view on github 눌러서 원격 레포지토리 생성됐는지 확인하기
- vscode에서 실행하기

## 가상환경 생성

- `python -m venv ./env` 파이썬 3.3 버전 이후부터는 새로운 가상환경을 생성할 수 있다. 현재 디렉터리에 새로운 가상환경 만들기.
- `git init .` 깃 레포지토리 설정해주기. `echo env/ > .gitignore` 깃이그노어 파일 생성하면서 env/ 넣어서 트래킹 제외해주기.

## 가상환경 실행

- 사용하는 os 플랫폼마다 실행하는 방법이 다르다. 사용하는 터미널에 따라서 명령어가 다르다. <venv>는 가상환경 디렉터리를 의미한다. 현재 가상환경 이름은 env. 더 자세한 내용은 다큐멘터리 참고하기. [파이썬 가상환경 다큐멘터리](https://docs.python.org/ko/3/library/venv.html)
    - windows cmd.exe `C:\> <venv>\Scripts\activate.bat`  bash/zsh `$ source <venv>/bin/activate`

## fastapi 실행하고 테스트 해보기

- `pip install fastapi uvicorn pytest requests httpx`
- api\main.py 코드 복사해주기
    
    ```python
    from fastapi import FastAPI
    
    app = FastAPI()
    
    @app.get("/")
    async def root():
        return {"message": "hello world"}
    ```
    
- `uvicorn api.main:app --reload`
    - 로컬에서 잘 돌아가는지 확인하기
- test 디렉토리 만들고 __init__.py, test_core.py 생성하기
- test_core.py
    
    ```python
    from fastapi.testclient import TestClient
    from api.main import app
    
    client = TestClient(app)
    
    def test_root():
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "hello world"}
    ```
    
- 서버 닫고 커멘드 창에 pytest
    - 테스트 코드가 잘 실행이 되는지 확인하기
- `pip freeze > requirements.txt`

## github actions cicd 파이프라인 생성

- 루트 디렉토리에 .github\workflows\main.yaml 파일 생성
- main.yaml
    
    ```yaml
    name: FastAPI CI/CD
    
    on:
      # Trigger the workflow on push
      push:
        branches: 
          # Push events on main branch
          - main 
    
    # The Job defines a series of steps that execute on the same runner.
    jobs:
    
      CI:
        # Define the runner used in the workflow
        runs-on: ubuntu-latest
        steps:   
          # Check out repo so our workflow can access it
          - uses: actions/checkout@v2
          
          # Step-1 Setup Python
          - name: Set up Python
            # This action sets up a Python environment for use in actions
            uses: actions/setup-python@v2
            with:
              python-version: '3.10'
              # optional: architecture: x64 x64 or x86. Defaults to x64 if not specified
    
          # Step-2 Install Python Virtual ENV
          - name: Install Python Virtual ENV
            run: pip3 install virtualenv
    
          # Step-3 Setup Virtual ENV
          # https://docs.github.com/en/actions/guides/caching-dependencies-to-speed-up-workflows
          - name:  Virtual ENV
            uses: actions/cache@v2
            id: cache-venv # name for referring later
            with:
              path: venv # what we cache: the Virtual ENV
              # The cache key depends on requirements.txt
              key: ${{ runner.os }}-venv-${{ hashFiles('**/requirements*.txt') }}
              restore-keys: |
                ${{ runner.os }}-venv-
    
          # Step-4 Build a Virtual ENV, but only if it doesn't already exist
          - name: Activate Virtual ENV
            run: python -m venv venv && source venv/bin/activate && pip3 install -r requirements.txt
            if: steps.cache-venv.outputs.cache-hit != 'true'
    
          - name: Run Tests   
            # Note that you have to activate the virtualenv in every step
            # because GitHub actions doesn't preserve the environment   
            run: . venv/bin/activate && pytest
          - name: Create archive of dependencies
            run: |
              cd ./venv/lib/python3.10/site-packages
              zip -r9 ../../../../api.zip .
          - name: Add API files to Zip file
            run: cd ./api && zip -g ../api.zip -r .
          - name: Upload zip file artifact
            uses: actions/upload-artifact@v2
            with:
              name: api
              path: api.zip
    ```
    
- 깃허브 데스크톱에서 커밋 메세지 입력하고 메인 브랜치로 커밋하기. 오리진으로 푸시하기.
- 원격 레포지토리의 깃허브 액션스 탭을 들어가면 클라우드에서 CI가 실행되고 있음을 알 수 있다.
- artifacts의 api.zip를 다운로드하면 코드가 잘 번들링 된 것을 확인할 수 있다.

## aws 설정

- s3 버킷 생성
- lambda 함수 생성 [deploy fastapi app on aws lambda](https://www.notion.so/deploy-fastapi-app-on-aws-lambda-51d4accfce6a4a1eafa3d5ab217d61e8?pvs=21) 참고하기
- 람다 핸들러 편집 누르고, 핸들러 main.handler로 수정하기
- `pip install mangum` 람다 핸들러 설치하기
- main.py
    
    ```python
    from fastapi import FastAPI
    from mangum import Mangum
    
    app = FastAPI()
    
    @app.get("/")
    async def root():
        return {"message": "hello world"}
    
    handler = Mangum(app=app)
    ```
    
- aws iam 설정에서 엑세스키 발행, 루트 계정으로는 발행하지 않기!
- 깃허브 레포지토리 시크릿에서 새로운 시크릿키 설정하기
    - AWS_SECRET_ACCESS_KEY / asd2131qwdqwd
    - AWS_SECRET_ACCESS_KEY_ID / qe12e12
    - AWS_DEFAULT_REGION / ap-northeast-2
- .github\workflows\main.yaml 업데이트
    
    ```yaml
    name: FastAPI CI/CD
    
    on:
      # Trigger the workflow on push
      push:
        branches: 
          # Push events on main branch
          - main 
    
    # The Job defines a series of steps that execute on the same runner.
    jobs:
    
      CI:
        # Define the runner used in the workflow
        runs-on: ubuntu-latest
        steps:   
          # Check out repo so our workflow can access it
          - uses: actions/checkout@v2
          
          # Step-1 Setup Python
          - name: Set up Python
            # This action sets up a Python environment for use in actions
            uses: actions/setup-python@v2
            with:
              python-version: '3.10'
              # optional: architecture: x64 x64 or x86. Defaults to x64 if not specified
    
          # Step-2 Install Python Virtual ENV
          - name: Install Python Virtual ENV
            run: pip3 install virtualenv
    
          # Step-3 Setup Virtual ENV
          # https://docs.github.com/en/actions/guides/caching-dependencies-to-speed-up-workflows
          - name:  Virtual ENV
            uses: actions/cache@v2
            id: cache-venv # name for referring later
            with:
              path: venv # what we cache: the Virtual ENV
              # The cache key depends on requirements.txt
              key: ${{ runner.os }}-venv-${{ hashFiles('**/requirements*.txt') }}
              restore-keys: |
                ${{ runner.os }}-venv-
    
          # Step-4 Build a Virtual ENV, but only if it doesn't already exist
          - name: Activate Virtual ENV
            run: python -m venv venv && source venv/bin/activate && pip3 install -r requirements.txt
            if: steps.cache-venv.outputs.cache-hit != 'true'
    
          - name: Run Tests   
            # Note that you have to activate the virtualenv in every step
            # because GitHub actions doesn't preserve the environment   
            run: . venv/bin/activate && pytest
          - name: Create archive of dependencies
            run: |
              cd ./venv/lib/python3.10/site-packages
              zip -r9 ../../../../api.zip .
          - name: Add API files to Zip file
            run: cd ./api && zip -g ../api.zip -r .
          - name: Upload zip file artifact
            uses: actions/upload-artifact@v2
            with:
              name: api
              path: api.zip
    
      CD:
        runs-on: ubuntu-latest
        needs: [CI]
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        steps:
          - name: Install AWS CLI
            uses: unfor19/install-aws-cli-action@v1
            with:
              version: 1
            env:
              AWS_ACCESS_KEY_ID: ${{ secrets.AWS_SECRET_ACCESS_KEY_ID }}
              AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
              AWS_DEFAULT_REGION: ${{ secrets.AWS_DEFAULT_REGION }}
          - name: Download Lambda api.zip
            uses: actions/download-artifact@v2
            with:
              name: api
          - name: Upload to S3
            run: aws s3 cp api.zip s3://fastapi-hshlab/api.zip
            env:
              AWS_ACCESS_KEY_ID: ${{ secrets.AWS_SECRET_ACCESS_KEY_ID }}
              AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
              AWS_DEFAULT_REGION: ${{ secrets.AWS_DEFAULT_REGION }}
          - name: Deploy new Lambda
            run: aws lambda update-function-code --function-name fastapi-hshlab --s3-bucket fastapi-hshlab --s3-key api.zip
            env:
              AWS_ACCESS_KEY_ID: ${{ secrets.AWS_SECRET_ACCESS_KEY_ID }}
              AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
              AWS_DEFAULT_REGION: ${{ secrets.AWS_DEFAULT_REGION }}
    ```
    
- aws api gateway 가서 rest api 새로 생성하기
- / 루트 아래 메서드 추가
    - get 방식
    - lambda
    - lambda 프록시 통합 체크
- test 눌러서 정상적으로 작동되는지 확인하기
- api 배포 누르고 url 링크로 확인하기
