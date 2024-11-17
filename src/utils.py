import json
import os
from config import PATH


def save_json(res, name):
    file_path = os.path.join(PATH, f'{name}.json')
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(res, file, ensure_ascii=False, indent=4)

def read_json():
    data = {}
    for file_name in os.listdir(PATH):
        if file_name.endswith(".json"):
            file_path = os.path.join(PATH, file_name)
            with open(file_path, "r", encoding="utf-8") as file:
                data[file_name[:len(file_name) - 5]] = json.load(file)

    return data['Ноутбуки и компьютеры']
