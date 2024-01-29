# chatGPT 키 입력 후 실행할 때
import openai
import os
import pandas as pd
import json
from dotenv import load_dotenv

load_dotenv()

class gpt:
    def __init__(self):
        if os.path.exists('csv_folder'):
            pass
        else:
            os.makedirs('csv_folder')
        openai.api_key = os.getenv('OPENAI_API_KEY')

# -1:초기화, 0:프레임, 1:공익, 2:정치 3:기타 4: 식별불가
    def classify_text(self, text):
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are responsible for classifying the text of advertising banners near the road or on the street."},

                {"role": "system", "content": "There are a total of three classes of advertising banners to classify."},

                {"role": "system", "content": "The Class 1 is the text of the public service banner installed by the city hall and district office."},
                {"role": "system", "content": "The Class 2 is  the text of a political promotion banner set up by politicians."},
                {"role": "system", "content": "The Class 3 is all banners other than 1 and 2. For example, text such as a hospital, gym, or academy promotional banner."},

                {"role": "system", "content": "The text I deliver is a set of words in the form of a list, and please combine and guess the words to classify the class."},

                {"role": "user", "content": f"The text I want to convey is: {text}."},
                {"role": "assistant", "content": f"Please provide a classification: 1, 2, or 3 based on the content you just shared."}
            ]
            
        )

        responsed_text = response.choices[0].message.content

        categories = {}
        class_list = []
        korean_list = []
        if 'Class 1' in responsed_text:
            class_list.append(1) #공익
            korean_list.append('public')
        elif 'Class 2' in responsed_text:
            class_list.append(2)#정치
            korean_list.append('politic')
        elif 'Class 3' in responsed_text:
            class_list.append(3) #기타
            korean_list.append('etc')
        else:
            class_list.append(4) #식별불가
            korean_list.append('none')

        categories['class'] = class_list

        df = pd.DataFrame.from_dict(categories)

        if not os.path.exists('./csv_folder/result.csv'):
            df.to_csv('./csv_folder/result.csv', index=False, mode='w', encoding='utf-8')
        else:
            df.to_csv('./csv_folder/result.csv', index=False, mode='a', encoding='utf-8', header=False)

        json_object = {
                        "text": text,
                        "answer": korean_list[0],
                        "reason" : responsed_text
                       }
        json_string = json.dumps(json_object)

        return json_string
    
