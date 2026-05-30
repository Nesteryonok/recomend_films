from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from deepface import DeepFace
import numpy as np
import io
from PIL import Image

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MOOD_CATEGORIES = {
    "веселое": {"id": "веселое", "emoji": "😄", "label": "Весёлое"},
    "эмоциональное": {"id": "эмоциональное", "emoji": "😢", "label": "Эмоциональное"},
    "романтическое": {"id": "романтическое", "emoji": "❤️", "label": "Романтическое"},
    "страшное": {"id": "страшное", "emoji": "😱", "label": "Страшное"},
    "динамичное": {"id": "динамичное", "emoji": "⚡", "label": "Динамичное"},
    "лёгкое": {"id": "лёгкое", "emoji": "😌", "label": "Лёгкое"},
}

EMOTION_MAP = {
    "happy": "веселое",
    "surprise": "динамичное",
    "fear": "страшное",
    "angry": "эмоциональное",
    "sad": "эмоциональное", 
    "disgust": "эмоциональное",
    "neutral": "лёгкое"       
}

def get_custom_mood(deepface_emotion: str) -> dict:
    """Переводит техническую эмоцию в твою категорию"""
    tech_emotion = deepface_emotion.lower()
    target_id = EMOTION_MAP.get(tech_emotion, "лёгкое") 
    return MOOD_CATEGORIES.get(target_id, MOOD_CATEGORIES["лёгкое"])

@app.post("/analyze")
async def analyze_emotion(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        img_array = np.array(image)
        
        result = DeepFace.analyze(img_array, actions=['emotion'], enforce_detection=False)
        
        if not result:
            return {"error": "Лицо не найдено"}
            
        face_data = result[0]
        emotions = face_data['emotion'] 
        
        dominant_tech = max(emotions, key=emotions.get)
        
        custom_mood = get_custom_mood(dominant_tech)
        
        return {
            "dominant_mood": custom_mood,
            "raw_emotions": emotions,    
            "confidence": round(emotions[dominant_tech] / 100, 2)
        }

    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5555)