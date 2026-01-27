#uvicorn main:app                ЗАПУСК ПРИЛОЖЕНИЯ
# main.py
# pip install python-multipart
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import os
import csv
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows requests from your React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 #   "http://localhost:8081"  # адрес фронтенда React Native
 #   "http://localhost:3000"  # React
 #   "http://localhost:5173"   # React +Vit   PWA
 #   "http://localhost:4173"   # React +Vit   PWA
# Construct the file path
CSV_FILE_PATH = os.path.join("data", "result.csv")
@app.get("/")
async def load_txt_from_directory():
    data = []
    try:
        with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as file:
            # Use csv.DictReader to read rows as dictionaries
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                row['id'] = int(row['id'])
                data.append(row)
    except FileNotFoundError:
        return {"error": f"File not found at {CSV_FILE_PATH}"}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}
    print(data)
    return data
        #uvicorn main:app
 #http://127.0.0.1:8000/docs