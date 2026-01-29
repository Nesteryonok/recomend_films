#LOAD TEXT FILE
# Открываем файл в режиме чтения ('r')
with open('result.txt', 'r', encoding='utf-8') as f:
    read_lines = f.readlines()
print("Прочитанный массив строк:")
print(read_lines)



