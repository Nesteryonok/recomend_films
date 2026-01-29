import pandas as pd

# ========== МАППИНГ ЖАНРОВ → ЭМОЦИЙ (КОРРЕКТНЫЙ) ==========
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
    """Преобразует строку жанров в строку эмоций с учётом приоритетов"""
    if not isinstance(genres_str, str) or genres_str == '(no genres listed)':
        return 'нейтральное'
    
    genres = [g.strip() for g in genres_str.split('|')]
    emotions = set()
    
    # ПРАВИЛО 1: Комедия имеет АБСОЛЮТНЫЙ приоритет (удаляет все остальные эмоции)
    if 'Comedy' in genres:
        return 'веселое'
    
    # ПРАВИЛО 2: Хоррор → только "страшное" (без смешения с напряжённым)
    if 'Horror' in genres:
        emotions.add('страшное')
        # Удаляем конфликтующие жанры
        genres = [g for g in genres if g not in ['Thriller', 'Crime']]
    
    # ПРАВИЛО 3: Романтика имеет приоритет над драмой
    if 'Romance' in genres:
        emotions.add('романтическое')
        genres = [g for g in genres if g != 'Drama']
    
    # ПРАВИЛО 4: Обрабатываем остальные жанры
    for genre in genres:
        if genre in genre_to_emotion:
            emotions.add(genre_to_emotion[genre])
    
    # ПРАВИЛО 5: Если есть "страшное", убираем "напряжённое"
    if 'страшное' in emotions and 'напряжённое' in emotions:
        emotions.remove('напряжённое')
    
    return '|'.join(sorted(emotions)) if emotions else 'нейтральное'

# Загружаем продукты
products = pd.read_csv('products1.csv')

# Добавляем колонку эмоций
products['emotions'] = products['genres'].apply(genres_to_emotions)

# Сохраняем обновлённый датасет
products.to_csv('products_with_emotions.csv', index=False, encoding='utf-8-sig')

print(" Эмоциональная разметка добавлена!")
