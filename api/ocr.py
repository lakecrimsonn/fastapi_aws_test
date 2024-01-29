import requests
import uuid
import time
import json
import os
from dotenv import load_dotenv

load_dotenv()

class OCR:
    def __init__(self):
        self.api_url = os.getenv('OCR_URL')
        self.secret_key = os.getenv('OCR_API_KEY')

    def ocr(self, img_path) -> str :

        image_file = img_path
        
        request_json = {
            'images': [
                {
                    'format': 'jpg',
                    'name': 'demo'
                }
            ],
            'requestId': str(uuid.uuid4()),
            'version': 'V2',
            'timestamp': int(round(time.time() * 1000))
        }

        payload = {'message': json.dumps(request_json).encode('UTF-8')}
        files = [
        ('file', open(image_file,'rb'))
        ]
        headers = {
        'X-OCR-SECRET': self.secret_key
        }

        response = requests.request("POST", self.api_url, headers=headers, data = payload, files = files)

        # print(response.text.encode('utf8'))

        result = response.json()
        
        text = ''
        for i in result['images'][0]['fields']:
            text += ' '+i['inferText']
        
        return text