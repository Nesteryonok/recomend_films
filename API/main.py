#uvicorn main:app                ЗАПУСК ПРИЛОЖЕНИЯ
# main.py
# pip install python-multipart

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import csv
from pathlib import Path
import subprocess
import sys
import os

app = FastAPI(title="Эмоциональная система рекомендаций фильмов")

# Настройка CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # React (create-react-app)
        "http://localhost:5173",   # React + Vite
        "http://localhost:4173",   # React + Vite (production)
        "http://localhost:8081"    # React Native
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====== КРИТИЧЕСКИ ВАЖНО: ПРАВИЛЬНЫЕ ПУТИ ======
# Путь к рекомендательной системе
RECOM_SCRIPT = Path("D:/123/dipl/Recom_sys_SVD_save_to_file2.py")

# Рабочая директория для запуска (где лежат ratings.csv, products_with_emotions.csv)
RECOM_WORKDIR = RECOM_SCRIPT.parent

# Путь к файлу результатов
RESULT_FILE = Path("D:/123/API/data/result.csv")

# Путь к интерпретатору рекомендательной системы
RECOM_INTERPRETER = Path("D:/123/dipl/venv/Scripts/python.exe")
# ==============================================

@app.get("/moods", summary="Список доступных настроений")
async def get_moods():
    """Возвращает список эмоциональных настроений для кнопок интерфейса"""
    return {
        "moods": [
            {"id": "веселое", "emoji": "😄", "label": "Весёлое"},
            {"id": "эмоциональное", "emoji": "😢", "label": "Эмоциональное"},
            {"id": "романтическое", "emoji": "❤️", "label": "Романтическое"},
            {"id": "страшное", "emoji": "😱", "label": "Страшное"},
            {"id": "динамичное", "emoji": "⚡", "label": "Динамичное"},
            {"id": "лёгкое", "emoji": "😌", "label": "Лёгкое"},
            {"id": "все", "emoji": "🎬", "label": "Все фильмы"}
        ]
    }

@app.get("/recommendations", summary="Рекомендации по настроению")
async def get_recommendations(
    mood: str = Query("веселое", description="Эмоциональное настроение")
):
    """
    Возвращает топ-10 фильмов, соответствующих запрошенному настроению.
    """
    try:
        print(f"\n🔄 Запуск рекомендательной системы для mood='{mood}'")
        print(f"   Скрипт: {RECOM_SCRIPT}")
        print(f"   Рабочая директория: {RECOM_WORKDIR}")
        print(f"   Интерпретатор: {RECOM_INTERPRETER}")
        print(f"   Результат: {RESULT_FILE}")
        
        # Проверяем существование скрипта и интерпретатора
        if not RECOM_SCRIPT.exists():
            return {
                "success": False,
                "error": f"Скрипт не найден: {RECOM_SCRIPT}",
                "hint": "Убедитесь, что путь к рекомендательной системе указан правильно в main.py"
            }
        
        if not RECOM_INTERPRETER.exists():
            return {
                "success": False,
                "error": f"Интерпретатор не найден: {RECOM_INTERPRETER}",
                "hint": "Убедитесь, что виртуальное окружение для рекомендательной системы создано"
            }
        
        # Запускаем рекомендательную систему С ПРАВИЛЬНОЙ РАБОЧЕЙ ДИРЕКТОРИЕЙ
        result = subprocess.run(
            [str(RECOM_INTERPRETER), str(RECOM_SCRIPT), mood],
            cwd=str(RECOM_WORKDIR),  # ← КРИТИЧЕСКИ ВАЖНО: рабочая директория = папка данных
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Логирование
        print(f"\n✅ Стандартный вывод:\n{result.stdout}")
        if result.stderr.strip():
            print(f"\n⚠️  Ошибки:\n{result.stderr}")
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"Ошибка выполнения рекомендательной системы (код {result.returncode})",
                "stderr": result.stderr[:1000]
            }
        
        # Проверяем существование файла результатов
        if not RESULT_FILE.exists():
            return {
                "success": False,
                "error": f"Файл результатов не создан: {RESULT_FILE}",
                "hint": "Проверьте права на запись в папку data/"
            }
        
        # Читаем результат
        recommendations = []
        with open(RESULT_FILE, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
             row['id'] = int(row['id'])
             # Убеждаемся, что есть колонка genres
             row['genres'] = row.get('genres', 'Unknown')
             recommendations.append(row)
        
        return {
            "success": True,
            "mood": mood,
            "count": len(recommendations),
            "recommendations": recommendations[:10]
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Рекомендательная система работает слишком долго (таймаут 30 сек)",
            "mood": mood
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Исключение: {type(e).__name__}: {str(e)}",
            "mood": mood
        }

@app.get("/health", summary="Проверка работоспособности")
async def health_check():
    """Проверяет, доступен ли файл с рекомендациями"""
    return {
        "status": "ok" if RESULT_FILE.exists() else "error",
        "recom_script_exists": RECOM_SCRIPT.exists(),
        "recom_workdir_exists": RECOM_WORKDIR.exists(),
        "recom_interpreter_exists": RECOM_INTERPRETER.exists(),
        "result_file_exists": RESULT_FILE.exists(),
        "recom_script_path": str(RECOM_SCRIPT.resolve()),
        "recom_workdir_path": str(RECOM_WORKDIR.resolve()),
        "recom_interpreter_path": str(RECOM_INTERPRETER.resolve()),
        "result_file_path": str(RESULT_FILE.resolve())
    }