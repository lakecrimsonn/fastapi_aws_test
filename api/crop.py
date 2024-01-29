##패키지 설치
import cv2 as cv
import numpy as np
import os,sys
import matplotlib.pyplot as plt
from glob import glob
import datetime
import requests

class ImageCrop:
    def __init__(self):
        if os.path.exists('./saved'):
            pass
        else:
            os.makedirs('saved')

        ##이미지 보관 폴더 생성
        if os.path.exists('./images'):
            pass
        else:
            os.makedirs('images')
            img_url = 'https://t1.daumcdn.net/thumb/R720x0.fpng/?fname=http://t1.daumcdn.net/brunch/service/user/44wc/image/SzYLIUNyxKMzmC62yFvDkXPBQoY.png'
            save_path = './images/{}.jpg'.format(datetime.datetime.now().strftime('%y%m%d_%H%M%S'))

            img = requests.get(img_url)

            with open(save_path, 'wb') as photo:
                photo.write(img.content)

        # self.imgs = os.listdir('./images')
        # self.imgs = [i for i in self.imgs if i.endswith('.jpg')]
        # self.imgs = img_from_fb

    def crop_image(self, img_path) -> None : 

        ##이미지 불러오기
        # img_path = '{your image path}'
        # img_path = os.path.join(os.path.dirname(__file__), '../images')
        # img_path = os.path.join(img_path, self.imgs[0]) ##일단 1장으로 테스트
        # print(img_path)

        img = cv.imread(img_path)
        gray = cv.cvtColor(img, cv.COLOR_RGB2GRAY)

        #히스토그램 평활화
        ASgray_hist = cv.equalizeHist(gray)


        gray_copy = gray.copy()
        img_copy = img.copy()

        ##이미지 이진화

        _, otsu = cv.threshold(gray, -1, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)


        #외곽선 검출
        contours1, hierachy = cv.findContours(otsu, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)


        #최대 크기 외곽선 검출

        max_contours = max(contours1, key= cv.contourArea)


        #최대 크기 외곽선 각 꼭짓점 추출

        rect = cv.boundingRect(max_contours)
        x,y,w,h = rect
        cropped = img[y:y+h, x: x+w].copy()


        #최소의 크기로 외접하는 사각형 

        min_rect = cv.minAreaRect(max_contours)
        box = cv.boxPoints(min_rect)
        box = np.int64(box)
        # cv.drawContours(img, [box], 0, (255,0,0), 3)


        box = box-box.min(axis=0)

        ##현수막이 위치한 마스크
        mask = np.zeros(img.shape, dtype=np.uint8)
        cv.fillPoly(mask, [box], (255,255,255))

        ##배경으로 쓸 마스크
        mask2 = np.zeros(img.shape[:2], dtype=np.uint8)
        cv.fillPoly(mask2, [box], 255)


        ##현수막만 누끼 따기
        mask[mask!=0] = img[mask!=0]

        result = mask.copy()
        result = cv.cvtColor(result, cv.COLOR_BGR2RGBA)
        result[:,:,3] = mask2


        
        suffix = datetime.datetime.now().strftime('%y%m%d_%H%M%S')
        save_path = './saved/' + suffix + '.jpg'


        cv.imwrite(save_path, cv.cvtColor(result, cv.COLOR_BGRA2RGBA))


        return save_path


