import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
import logic

# Wczytanie danych
data = logic.load_data()

# Tworzenie okna głównego
root = tb.Window(themename="darkly")
root.title("Tracker Wody")
root.geometry("320x450")
root.resizable(False, False)

# Menu aplikacji
menu_bar = tk.Menu(root)

file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Zamknij", command=root.quit)
menu_bar.add_cascade(label="Plik", menu=file_menu)

options_menu = tk.Menu(menu_bar, tearoff=0)
options_menu.add_command(label="Ustawienia", command=lambda: toggle_settings())
menu_bar.add_cascade(label="Opcje", menu=options_menu)

help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="O aplikacji", command=lambda: messagebox.showinfo("O aplikacji", "Tracker Wody v1.0\nAutor: Dawid Kapciak"))
menu_bar.add_cascade(label="Pomoc", menu=help_menu)

root.config(menu=menu_bar)

# Górny pasek z tytułem i przyciskiem ustawień
header_frame = tb.Frame(root)
header_frame.pack(fill="x", padx=10, pady=5)

header_label = tb.Label(header_frame, text="Tracker Wody", font=("Arial", 16, "bold"))
header_label.pack(side="left")

# Środkowa sekcja z animacją szklanki
canvas_frame = tb.Frame(root)
canvas_frame.pack(pady=10)

canvas = tk.Canvas(canvas_frame, width=150, height=250, bg="white", highlightthickness=2, relief="ridge")
canvas.pack()

# Rysowanie konturu szklanki
glass_outline = canvas.create_rectangle(40, 20, 110, 230, outline="black", width=2)

# Tworzenie prostokąta jako poziom wody
water_fill = canvas.create_rectangle(41, 230, 109, 230, fill="blue", outline="blue")

# Etykieta postępu
intake_label = tb.Label(root, text="", font=("Arial", 12))
intake_label.pack(pady=5)

# Przyciski sterujące
btn_frame = tb.Frame(root)
btn_frame.pack(pady=10)

btn_remove = tb.Button(btn_frame, text="-", command=lambda: remove_water(), bootstyle="danger-outline", width=5)
btn_remove.grid(row=0, column=0, padx=10)

btn_add = tb.Button(btn_frame, text="+", command=lambda: add_water(), bootstyle="success-outline", width=5)
btn_add.grid(row=0, column=1, padx=10)

# PANEL USTAWIEŃ (schowany domyślnie)
settings_frame = tb.Frame(root, width=200, height=450, bootstyle="light")
settings_frame.place(x=320, y=0)  # Początkowa pozycja poza ekranem

tb.Label(settings_frame, text="Ustawienia", font=("Arial", 14, "bold")).pack(pady=10)

tb.Label(settings_frame, text="Cel (ml):").pack(pady=5)
goal_entry = tb.Entry(settings_frame)
goal_entry.pack()
goal_entry.insert(0, str(data["goal"]))

tb.Label(settings_frame, text="Wielkość szklanki (ml):").pack(pady=5)
glass_entry = tb.Entry(settings_frame)
glass_entry.pack()
glass_entry.insert(0, str(data["glass_size"]))

def save_settings():
    """Zapisuje ustawienia i zamyka panel."""
    try:
        goal = int(goal_entry.get())
        glass_size = int(glass_entry.get())
        logic.update_settings(data, goal, glass_size)
        refresh_ui()
        toggle_settings()
    except ValueError:
        messagebox.showerror("Błąd", "Podaj poprawne wartości liczbowe.")

tb.Button(settings_frame, text="Zapisz", command=save_settings, bootstyle="primary").pack(pady=10)

def toggle_settings():
    """Wysuwa lub chowa panel ustawień."""
    if settings_frame.winfo_x() > 300:  # Jeśli jest poza ekranem
        settings_frame.place(x=120, y=0)  # Wysuwa panel na ekran
    else:
        settings_frame.place(x=320, y=0)  # Chowa panel

def refresh_ui():
    """Aktualizuje UI, w tym animację napełniania szklanki."""
    percentage = logic.update_progress(data) / 100
    water_level = 230 - (percentage * 210)  # 210 to wysokość wypełnienia
    canvas.coords(water_fill, 41, water_level, 109, 230)  # Aktualizacja poziomu wody
    intake_label.config(text=f"{data['intake']} ml / {data['goal']} ml")

def add_water():
    logic.add_water(data)
    refresh_ui()

def remove_water():
    logic.remove_water(data)
    refresh_ui()

# Inicjalizacja UI
refresh_ui()
root.mainloop()
