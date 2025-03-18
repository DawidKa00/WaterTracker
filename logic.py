import json
import os
from datetime import datetime

DATA_FILE = "water_data.json"


def load_data():
    """Wczytuje dane z pliku JSON i dodaje nowy dzień, jeśli potrzeba."""
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
        return data[-1]

    last_entry = data[-1] if data else {}
    new_entry = {
        "date": today,
        "intake": 0,
        "goal": last_entry.get("goal", 2000),
        "glass_size": last_entry.get("glass_size", 250)
    }

    data.append(new_entry)
    save_data(data)

    return new_entry


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
