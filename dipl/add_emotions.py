import pandas as pd

# ========== МАППИНГ ЖАНРОВ → ЭМОЦИЙ ==========
genre_to_emotion = {
    'Comedy': 'веселое',
    'Drama': 'эмоциональное',
    'Romance': 'романтическое',
    'Horror': 'страшное',
    'Thriller': 'напряжённое',
    'Crime': 'напряжённое',
    'Action': 'динамичное',
    'Adventure': 'приключенческое',
    'Western': 'приключенческое',
    'Animation': 'лёгкое',
    'Children': 'семейное',
    'Fantasy': 'волшебное',
    'Sci-Fi': 'футуристическое',
    'Documentary': 'познавательное',
    'War': 'драматичное',
    'Musical': 'музыкальное',
    'Mystery': 'загадочное',
    'Film-Noir': 'мрачное',
    'IMAX': 'зрелищное',
    'Sport': 'динамичное',
    'Biography': 'эмоциональное',
    'History': 'драматичное'
}

def genres_to_emotions(genres_str):
    """Преобразует строку жанров в строку эмоций"""
    if not isinstance(genres_str, str) or genres_str == '(no genres listed)':
        return 'нейтральное'
    
    genres = [g.strip() for g in genres_str.split('|')]
    emotions = set()
    
    # 🔑 КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: заполняем множество эмоций
    for genre in genres:
        if genre in genre_to_emotion:
            emotions.add(genre_to_emotion[genre])
    
    return '|'.join(sorted(emotions)) if emotions else 'нейтральное'

# Загружаем продукты
products = pd.read_csv('products1.csv')

# Добавляем колонку эмоций
products['emotions'] = products['genres'].apply(genres_to_emotions)

# Сохраняем обновлённый датасет
products.to_csv('products_with_emotions.csv', index=False, encoding='utf-8-sig')

print("✅ Эмоциональная разметка добавлена!")