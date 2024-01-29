import cv2 as cv
import numpy as np
import os,sys
import matplotlib.pyplot as plt
import openai
import pandas as pd
import requests
import uuid
import time
import json
from glob import glob
import datetime
import json

import api.crop as crop
import api.ocr as ocr
import api.gpt_inference as gpt_inference

async def execute(img):

    img_crop = crop.ImageCrop()
    img_ocr = ocr.OCR()
    gpt_infer = gpt_inference.gpt()

    img_path = img_crop.crop_image(img)
    text = img_ocr.ocr(img_path)
    answer = gpt_infer.classify_text(text)

    url = os.getenv("FIREBASE_FUNCTIONS_URL")
    headers = {"Content-Type": "application/json"}
    print(answer)
    requests.post(url, data=answer, headers=headers)
    return None

execute('./images/test.jpg')




