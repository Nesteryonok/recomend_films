# ========== КРИТИЧЕСКИ ВАЖНО: УСТАНОВКА КОДИРОВКИ UTF-8 ДЛЯ ВЫВОДА ==========
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# ===========================================================================

import pandas as pd
import numpy as np
import os
from pathlib import Path
import sys as sys_module
from sklearn.metrics import mean_squared_error
from math import sqrt
from scipy.sparse.linalg import svds

GENRE_TRANSLATION = {
    'Action': 'Боевик',
    'Adventure': 'Приключения',
    'Animation': 'Мультфильм',
    'Children': 'Детский',
    'Comedy': 'Комедия',
    'Crime': 'Криминал',
    'Documentary': 'Документальный',
    'Drama': 'Драма',
    'Fantasy': 'Фэнтези',
    'Film-Noir': 'Нуар',
    'Horror': 'Ужасы',
    'IMAX': 'IMAX',
    'Musical': 'Мюзикл',
    'Mystery': 'Мистика',
    'Romance': 'Романтика',
    'Sci-Fi': 'Фантастика',
    'Thriller': 'Триллер',
    'War': 'Военный',
    'Western': 'Вестерн',
    '(no genres listed)': 'Неизвестно'
}

def translate_genres(genres_str):
    """Переводит жанры с английского на русский"""
    if not isinstance(genres_str, str) or pd.isna(genres_str):
        return 'Неизвестно'
    
    genres = genres_str.split('|')
    translated = [GENRE_TRANSLATION.get(g.strip(), g.strip()) for g in genres]
    return ' | '.join(translated)
# ========== ПОЛУЧЕНИЕ НАСТРОЕНИЯ ИЗ АРГУМЕНТА КОМАНДНОЙ СТРОКИ ==========
user_mood = sys_module.argv[1] if len(sys_module.argv) > 1 else "веселое"
print(f"[OK] Получено настроение: {user_mood}")


# ========== ПОЛУЧЕНИЕ НАСТРОЕНИЯ ИЗ АРГУМЕНТА КОМАНДНОЙ СТРОКИ ==========
user_mood = sys_module.argv[1] if len(sys_module.argv) > 1 else "веселое"
print(f"[OK] Получено настроение: {user_mood}")

# ========== ЗАГРУЗКА ДАННЫХ ==========
df = pd.read_csv('ratings.csv')

n_users = df['userId'].unique().shape[0]
n_items = df['productId'].unique().shape[0]
print(f'[INFO] Число пользователей: {n_users}')
print(f'[INFO] Число фильмов: {n_items}')

# Создаём user-product матрицу
data_matrix = np.zeros((n_users, n_items))
for line in df.itertuples():
    data_matrix[line[1] - 1, line[2] - 1] = line[3]

# ========== SVD АЛГОРИТМ ==========
u, s, vt = svds(data_matrix, k=8)
s_diag_matrix = np.diag(s)
s_diag_matrix = np.round(s_diag_matrix, 1)

predict_matrix = np.dot(np.dot(u, s_diag_matrix), vt)
predict_matrix = np.round(predict_matrix, 1)

# Функция RMSE
def rmse(prediction, ground_truth):
    prediction = prediction[ground_truth.nonzero()].flatten()
    ground_truth = ground_truth[ground_truth.nonzero()].flatten()
    return sqrt(mean_squared_error(prediction, ground_truth))

print(f'[METRIC] User-based CF RMSE: {rmse(predict_matrix, data_matrix)}')

# ========== РАСЧЁТ ТОП-50 ФИЛЬМОВ (увеличено для лучшей фильтрации) ==========
predict_matrix_T = predict_matrix.T
ind_avg = np.mean(predict_matrix_T, axis=1)

n = len(ind_avg)
indices = list(range(n))
indices.sort(key=lambda i: ind_avg[i], reverse=True)

ind_sort = [i + 1 for i in indices]
R_sort = [round(ind_avg[i], 1) for i in indices]

# Берём топ-50 для надёжной фильтрации по эмоциям
ind_sort_max = ind_sort[:200]
R_sort_max = R_sort[:200]
print(f'\n[INFO] Топ-10 фильмов по среднему рейтингу (первые 10): {ind_sort_max[:10]}')

# ========== ЗАГРУЗКА ФИЛЬМОВ С ЭМОЦИЯМИ ==========
products = pd.read_csv('products_with_emotions.csv')

# Получаем названия, эмоции и ПЕРЕВОДИМ жанры для топ-100 продуктов
top_movies = []
for prod_id in ind_sort_max:
    match = products[products['product_id'] == int(prod_id)]
    if not match.empty:
        title = match['title'].values[0]
        emotions = match['emotions'].values[0]
        genres_en = match['genres'].values[0] if 'genres' in match.columns else '(no genres listed)'
        genres_ru = translate_genres(genres_en)  # ← КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: переводим жанры
        
        top_movies.append({
            'id': int(prod_id),
            'title': title,
            'emotions': emotions,
            'genres': genres_ru  # ← ИСПОЛЬЗУЕМ ПЕРЕВЕДЁННЫЕ ЖАНРЫ
        })
    else:
        top_movies.append({
            'id': int(prod_id),
            'title': f"Unknown (ID {prod_id})",
            'emotions': 'нейтральное',
            'genres': 'Неизвестно'  # ← Уже на русском
        })

# ========== ФИЛЬТРАЦИЯ ПО НАСТРОЕНИЮ (СТРОГАЯ, БЕЗ ДОПОЛНЕНИЯ) ==========
def filter_by_mood(movies, mood):
    """Фильтрует фильмы СТРОГО по запрошенной эмоции (без дополнения другими фильмами)"""
    if mood == "все" or not mood:
        return movies[:10]
    
    # Берём ТОЛЬКО фильмы с запрошенной эмоцией
    filtered = [m for m in movies if mood in m['emotions'].split('|')]
    
    # Возвращаем максимум 10 фильмов
    return filtered[:10]

filtered_movies = filter_by_mood(top_movies, user_mood)

print(f"\n[RECOMMEND] Рекомендации для настроения '{user_mood}':")
if not filtered_movies:
    print(f" Нет фильмов с эмоцией '{user_mood}' в топ-50 по рейтингу")
    # Возвращаем топ-5 без фильтрации как резерв
    filtered_movies = top_movies[:5]
    print("  → Показаны топ-5 фильмов без фильтрации:")

for i, movie in enumerate(filtered_movies, 1):
    print(f"{i}. {movie['title']}")
    print(f"   Жанры: {movie['genres']}")
    print(f"   Эмоции: {movie['emotions']}")

# ========= СОХРАНЕНИЕ В ФОРМАТЕ ДЛЯ СЕРВЕРА =========
TARGET_DIR = Path("D:/123/API/data")
TARGET_DIR.mkdir(parents=True, exist_ok=True)

file_path = TARGET_DIR / "result.csv"
with open(file_path, 'w', encoding='utf-8') as f:
    f.write("id,name,genres,emotions\n")
    for idx, movie in enumerate(filtered_movies, start=1):
        name = movie['title'].replace('"', '""')
        genres = movie['genres'].replace('"', '""')
        emotions = movie['emotions'].replace('"', '""')
        
        # Экранируем поля с запятыми или кавычками
        if ',' in name or ',' in genres or ',' in emotions or '"' in name or '"' in genres or '"' in emotions:
            f.write(f'{idx},"{name}","{genres}","{emotions}"\n')
        else:
            f.write(f"{idx},{name},{genres},{emotions}\n")

print(f"\n[SAVE] Результаты сохранены в: {file_path.resolve()}")
print(f"[SAVE] Сохранено фильмов: {len(filtered_movies)}")
print(f"[SAVE] Настроение: {user_mood}")