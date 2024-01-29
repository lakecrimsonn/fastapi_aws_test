from fastapi import FastAPI, File, UploadFile
from mangum import Mangum
from dotenv import load_dotenv
import os
import shutil
import requests
from api.execute import execute

load_dotenv()

app = FastAPI()

handler = Mangum(app=app)

@app.get("/")
async def root():
    return {"message": "hello world"}

@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    # Define the directory where you want to save the image
    # Make sure this directory exists or create it
    directory = "images"
    os.makedirs(directory, exist_ok=True)

    # Define the file path
    file_path = os.path.join(directory, file.filename)

    # Save the uploaded file to the file path
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # await read_item()
    await execute(file_path)

    return {"message": "Image uploaded successfully", "file_path": file_path}

