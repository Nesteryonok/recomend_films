import sys
import io
import os
import pickle
import numpy as np
import pandas as pd
import scipy.sparse as sparse
from pathlib import Path
from implicit.als import AlternatingLeastSquares

# ========== НАСТРОЙКА КОДИРОВКИ (для Windows) ==========
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ========== КОНФИГУРАЦИЯ ==========
RATINGS_FILE = 'ratings.csv'
PRODUCTS_FILE = 'products_with_emotions.csv'
MODEL_FILE = 'implicit_model.pkl'
TARGET_DIR = Path("C:/work/recomend_films/API/data")

GENRE_TRANSLATION = {
    'Action': 'Боевик', 'Adventure': 'Приключения', 'Animation': 'Мультфильм',
    'Children': 'Детский', 'Comedy': 'Комедия', 'Crime': 'Криминал',
    'Documentary': 'Документальный', 'Drama': 'Драма', 'Fantasy': 'Фэнтези',
    'Film-Noir': 'Нуар', 'Horror': 'Ужасы', 'IMAX': 'IMAX',
    'Musical': 'Мюзикл', 'Mystery': 'Мистика', 'Romance': 'Романтика',
    'Sci-Fi': 'Фантастика', 'Thriller': 'Триллер', 'War': 'Военный',
    'Western': 'Вестерн', '(no genres listed)': 'Неизвестно'
}

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
def translate_genres(genres_str):
    """Переводит жанры с английского на русский"""
    if not isinstance(genres_str, str) or pd.isna(genres_str):
        return 'Неизвестно'
    genres = genres_str.split('|')
    translated = [GENRE_TRANSLATION.get(g.strip(), g.strip()) for g in genres]
    return ' | '.join(translated)

def filter_by_mood(movies, mood, all_movies_df=None, score_dict=None):
    """
    Фильтрует фильмы по эмоции и ГАРАНТИРОВАННО возвращает 10 фильмов
    """
    if mood == "все" or not mood:
        return movies[:10]
    
    # 1. Сначала фильтруем из рекомендаций модели
    filtered = []
    for m in movies:
        emotions_list = m['emotions'].lower().split('|')
        if mood.lower() in emotions_list:
            filtered.append(m)
    
    # 2. Если нашли 10 или больше — возвращаем
    if len(filtered) >= 10:
        return filtered[:10]
    
    # 3. Если меньше 10 — дополняем из полной базы по эмоции
    if all_movies_df is not None and score_dict is not None:
        # Находим все фильмы с нужной эмоцией в полной базе
        emotion_matches = all_movies_df[
            all_movies_df['emotions'].apply(
                lambda x: mood.lower() in str(x).lower().split('|') if pd.notna(x) else False
            )
        ].copy()
        
        # Добавляем score из модели (если есть) или средний score
        emotion_matches['score'] = emotion_matches['product_id'].map(
            lambda x: score_dict.get(x, 0.5)
        )
        
        # Исключаем уже добавленные фильмы
        existing_ids = {m['id'] for m in filtered}
        emotion_matches = emotion_matches[~emotion_matches['product_id'].isin(existing_ids)]
        
        # Сортируем по score и берём недостающее количество
        emotion_matches = emotion_matches.sort_values('score', ascending=False)
        
        needed = 10 - len(filtered)
        for _, row in emotion_matches.head(needed).iterrows():
            genres_en = str(row['genres']) if pd.notna(row['genres']) else '(no genres listed)'
            genres_ru = translate_genres(genres_en)
            
            filtered.append({
                'id': int(row['product_id']),
                'title': row['title'],
                'emotions': str(row['emotions']),
                'genres': genres_ru,
                'score': row['score']
            })
    
    return filtered[:10]

# ========== ЗАГРУЗКА ИЛИ ОБУЧЕНИЕ МОДЕЛИ ==========
def load_or_train_model():
    """Загружает модель из pickle, если есть, иначе обучает новую"""
    if os.path.exists(MODEL_FILE):
        print(f"[INFO] Загрузка сохраненной модели из {MODEL_FILE}...")
        try:
            with open(MODEL_FILE, 'rb') as f:
                data = pickle.load(f)
                return data['model'], data['user_mapper'], data['movie_inv_mapper']
        except Exception as e:
            print(f"[WARN] Ошибка загрузки модели: {e}. Переобучение...")
    
    print("[INFO] Модель не найдена. Начало обучения ALS...")
    
    ratings_df = pd.read_csv(RATINGS_FILE)
    
    user_mapper = {user_id: idx for idx, user_id in enumerate(sorted(ratings_df['userId'].unique()))}
    movie_mapper = {movie_id: idx for idx, movie_id in enumerate(sorted(ratings_df['productId'].unique()))}
    
    movie_inv_mapper = {idx: movie_id for movie_id, idx in movie_mapper.items()}
    
    user_indices = ratings_df['userId'].map(user_mapper)
    movie_indices = ratings_df['productId'].map(movie_mapper)
    
    confidence = ratings_df['rating']
    
    user_item_matrix = sparse.csr_matrix(
        (confidence, (user_indices, movie_indices)),
        shape=(len(user_mapper), len(movie_mapper))
    )
    
    item_user_matrix = user_item_matrix.T.tocsr()
    
    print(f"[DATA] Загружено: {len(ratings_df)} оценок, {len(user_mapper)} пользователей, {len(movie_mapper)} фильмов")
    
    model = AlternatingLeastSquares(factors=64, regularization=0.05, iterations=50)
    model.fit(item_user_matrix)
    print("[OK] Модель обучена!")
    
    with open(MODEL_FILE, 'wb') as f:
        pickle.dump({
            'model': model,
            'user_mapper': user_mapper,
            'movie_inv_mapper': movie_inv_mapper
        }, f)
    print(f"[SAVE] Модель сохранена в {MODEL_FILE}")
    
    return model, user_mapper, movie_inv_mapper

# ========== ОСНОВНАЯ ЛОГИКА ==========
if __name__ == "__main__":
    user_mood = sys.argv[1] if len(sys.argv) > 1 else "веселое"
    user_id_input = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    
    print(f"[OK] Настроение: {user_mood}")
    print(f"[OK] Пользователь: {user_id_input}")

    model, user_mapper, movie_inv_mapper = load_or_train_model()
    
    if user_id_input not in user_mapper:
        print(f"[WARN] Пользователь {user_id_input} не найден в истории оценок.")
        user_id_input = list(user_mapper.keys())[0]
        print(f"[INFO] Использован ID: {user_id_input}")

    user_idx = user_mapper[user_id_input]
    user_items = None

    # 4. Генерация рекомендаций (УВЕЛИЧИЛИ с 50 до 200)
    N_RECOMMEND = 200
    recommendations, scores = model.recommend(
        userid=user_idx,
        user_items=user_items, 
        N=N_RECOMMEND,
        filter_already_liked_items=False
    )
    
    recommended_product_ids = [movie_inv_mapper[rec_idx] for rec_idx in recommendations]
    score_dict = {pid: score for pid, score in zip(recommended_product_ids, scores)}
    
    products_df = pd.read_csv(PRODUCTS_FILE)
    
    rec_movies_df = products_df[products_df['product_id'].isin(recommended_product_ids)].copy()
    rec_movies_df['score'] = rec_movies_df['product_id'].map(score_dict)
    rec_movies_df = rec_movies_df.sort_values('score', ascending=False)
    
    top_movies = []
    for _, row in rec_movies_df.iterrows():
        genres_en = str(row['genres']) if 'genres' in row and pd.notna(row['genres']) else '(no genres listed)'
        genres_ru = translate_genres(genres_en)
        emotions = str(row['emotions']) if 'emotions' in row and pd.notna(row['emotions']) else 'нейтральное'
        
        top_movies.append({
            'id': int(row['product_id']),
            'title': row['title'],
            'emotions': emotions,
            'genres': genres_ru,
            'score': row['score']
        })
    
    # 8. Фильтрация по настроению (с дополнением из полной базы)
    filtered_movies = filter_by_mood(
        top_movies, 
        user_mood, 
        all_movies_df=products_df,
        score_dict=score_dict
    )
    
    print(f"\n[RECOMMEND] Рекомендации для пользователя {user_id_input} и настроения '{user_mood}':")
    print(f"  Найдено фильмов: {len(filtered_movies)}")

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    file_path = TARGET_DIR / "result.csv"
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("id,name,genres,emotions\n")
        for idx, movie in enumerate(filtered_movies, start=1):
            name = movie['title'].replace('"', '""')
            genres = movie['genres'].replace('"', '""')
            emotions = movie['emotions'].replace('"', '""')
            
            if ',' in name or ',' in genres or ',' in emotions or '"' in name or '"' in genres or '"' in emotions:
                f.write(f'{idx},"{name}","{genres}","{emotions}"\n')
            else:
                f.write(f"{idx},{name},{genres},{emotions}\n")
    
    print(f"\n[SAVE] Результаты сохранены в: {file_path.resolve()}")
    print(f"[SAVE] Сохранено фильмов: {len(filtered_movies)}")