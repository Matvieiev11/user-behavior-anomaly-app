def export_to_csv(data, file_path):
    try:
        data.to_csv(file_path, index=False)
        return True
    except Exception as e:
        print("Помилка експорту:", e)
        return False