import pandas as pd
import numpy as np
import os
from pathlib import Path
from sklearn.metrics import mean_squared_error
from math import sqrt
from scipy.sparse.linalg import svds

# ========== ЗАГРУЗКА ДАННЫХ ==========
# Загружаем датасет из текущей директории (где лежит скрипт)
df = pd.read_csv('ratings.csv')

# Выводим количество пользователей и фильмов
n_users = df['userId'].unique().shape[0]
n_items = df['productId'].unique().shape[0]
print('Число пользователей:', n_users)
print('Число продуктов:', n_items)
print(df)

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

print('User-based CF RMSE:', rmse(predict_matrix, data_matrix))

# ========== РАСЧЁТ ТОП-10 ==========
predict_matrix_T = predict_matrix.T
ind_avg = np.mean(predict_matrix_T, axis=1)

n = len(ind_avg)
indices = list(range(n))
indices.sort(key=lambda i: ind_avg[i], reverse=True)

ind_sort = [i + 1 for i in indices]
R_sort = [round(ind_avg[i], 1) for i in indices]

ind_sort_max = ind_sort[:10]
R_sort_max = R_sort[:10]
print('Наиболее рейтинговые фильмы (ID):', ind_sort_max)
print('Их средние рейтинги:', R_sort_max)

# Загружаем информацию о продуктах
products = pd.read_csv('products1.csv')
print(products)

print('Фильмы с самым высоким рейтингом (ID):', ind_sort_max)
# Получаем названия топ-10
top_products_with_name = []
for prod_id in ind_sort_max:
    match = products[products['product_id'] == int(prod_id)]
    if not match.empty:
        top_products_with_name.append(match['title'].values[0])
    else:
        top_products_with_name.append(f"Unknown (ID {prod_id})")

top_products_with_name = np.array(top_products_with_name)
print("Названия этих фильмов:", top_products_with_name)

# ========= СОХРАНЕНИЕ В НУЖНУЮ ПАПКУ =========
# Абсолютный путь к целевой директории
TARGET_DIR = Path("D:/123/API/API/data")
TARGET_DIR.mkdir(parents=True, exist_ok=True)  # Создаём всю цепочку папок

file_path = TARGET_DIR / "result.csv"
with open(file_path, 'w', encoding='utf-8') as f:
    f.write("id,name\n")  # Заголовок в требуемом формате
    for idx, name in enumerate(top_products_with_name, start=1):
        # Экранируем запятые и кавычки в названиях (защита CSV)
        if ',' in name or '"' in name:
            name = f'"{name.replace('"', '""')}"'
        f.write(f"{idx},{name}\n")

print(f"\nРезультаты успешно сохранены в: {file_path}")
print(f"   Абсолютный путь: {file_path.resolve()}")