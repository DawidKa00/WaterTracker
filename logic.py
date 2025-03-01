import json
import os
from datetime import datetime

DATA_FILE = "water_data.json"

def load_data():
    """Wczytuje dane z pliku JSON."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
        if data.get("date") == datetime.today().strftime('%Y-%m-%d'):
            return data
    return {"date": datetime.today().strftime('%Y-%m-%d'), "intake": 0, "goal": 2000, "glass_size": 250}

def save_data(data):
    """Zapisuje dane do pliku JSON."""
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

def update_progress(data):
    """Aktualizuje postęp."""
    return min(100, (data["intake"] / data["goal"]) * 100)

def add_water(data):
    """Dodaje wodę."""
    data["intake"] += data["glass_size"]
    save_data(data)

def remove_water(data):
    """Usuwa wodę."""
    data["intake"] = max(0, data["intake"] - data["glass_size"])
    save_data(data)

def update_settings(data, goal, glass_size):
    """Aktualizuje ustawienia."""
    data["goal"] = goal
    data["glass_size"] = glass_size
    save_data(data)