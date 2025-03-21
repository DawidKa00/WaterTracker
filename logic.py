import json
import os
from datetime import datetime

DATA_FILE = "water_data.json"


def load_data(days=None):
    """Wczytuje dane z pliku JSON i zwraca określoną liczbę dni."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            try:
                data = json.load(file)
                if not isinstance(data, list):
                    data = []
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    today = datetime.today().strftime('%Y-%m-%d')

    if data and data[-1].get("date") == today:
        latest_entry = data[-1]
    else:
        last_entry = data[-1] if data else {}
        latest_entry = {
            "date": today,
            "intake": 0,
            "goal": last_entry.get("goal", 2000),
            "glass_size": last_entry.get("glass_size", 250)
        }
        data.append(latest_entry)
        save_data(data)

    # Jeśli podano `days`, zwracamy ostatnie X dni
    if days:
        return data[-days:]  # Pobierz ostatnie `days` dni
    return latest_entry  # Zwróć dzisiejszy wpis


def save_data(data):
    """Zapisuje całą listę dni do pliku JSON."""
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


def add_water(data):
    """Dodaje wodę i zapisuje zmiany."""
    data["intake"] += data["glass_size"]
    save_data(update_data_list(data))


def remove_water(data):
    """Usuwa wodę i zapisuje zmiany."""
    data["intake"] = max(0, data["intake"] - data["glass_size"])
    save_data(update_data_list(data))


def update_settings(data, goal, glass_size):
    """Aktualizuje ustawienia i zapisuje zmiany."""
    data["goal"] = goal
    data["glass_size"] = glass_size
    save_data(update_data_list(data))


def update_data_list(updated_entry):
    """Aktualizuje listę dni w pliku JSON, zastępując wpis dla bieżącego dnia."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            try:
                data = json.load(file)
                if not isinstance(data, list):
                    data = []
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    if data and data[-1]["date"] == updated_entry["date"]:
        data[-1] = updated_entry
    else:
        data.append(updated_entry)

    return data
