import json
import os
from datetime import datetime

DATA_FILE = "water_data.json"


def load_data(days=None):
    """Wczytuje dane z pliku JSON i zwraca określoną liczbę dni."""
    data = _read_json_file()

    today = datetime.today().strftime('%Y-%m-%d')

    if not data or data[-1].get("date") != today:
        last_entry = data[-1] if data else {}
        latest_entry = {
            "date": today,
            "intake": 0,
            "goal": last_entry.get("goal", 2000),
            "glass_size": last_entry.get("glass_size", 250)
        }
        data.append(latest_entry)
        save_data(data)
    else:
        latest_entry = data[-1]

    return data[-days:] if days else latest_entry


def save_data(data):
    """Zapisuje całą listę dni do pliku JSON."""
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


def add_water(data):
    """Dodaje wodę i zapisuje zmiany."""
    _update_daily_data(data, "intake", data["intake"] + data["glass_size"])


def remove_water(data):
    """Usuwa wodę i zapisuje zmiany."""
    _update_daily_data(data, "intake", max(0, data["intake"] - data["glass_size"]))


def update_settings(data, goal, glass_size):
    """Aktualizuje ustawienia i zapisuje zmiany."""
    data["goal"], data["glass_size"] = goal, glass_size
    save_data(update_data_list(data))


def update_data_list(updated_entry):
    """Aktualizuje listę dni w pliku JSON, zastępując wpis dla bieżącego dnia."""
    data = _read_json_file()

    if data and data[-1]["date"] == updated_entry["date"]:
        data[-1] = updated_entry
    else:
        data.append(updated_entry)

    return data


def _read_json_file():
    """Pomocnicza funkcja wczytująca dane z pliku JSON."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            try:
                data = json.load(file)
                return data if isinstance(data, list) else []
            except json.JSONDecodeError:
                return []
    return []


def _update_daily_data(data, key, value):
    """Pomocnicza funkcja aktualizująca dane dzienne."""
    data[key] = value
    save_data(update_data_list(data))
