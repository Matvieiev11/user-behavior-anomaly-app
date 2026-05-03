import pandas as pd

def load_data(file_path):
    try:
        data = pd.read_csv(file_path)
        print("Дані успішно завантажено")
        return data
    except Exception as e:
        print("Помилка завантаження:", e)
        return None