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

# Nagłówek aplikacji
header_label = tb.Label(root, text="Tracker Wody", font=("Arial", 16, "bold"))
header_label.pack(pady=10)

# Środkowa sekcja z animacją
canvas_frame = tb.Frame(root)
canvas_frame.pack(pady=10)

canvas = tk.Canvas(canvas_frame, width=150, height=250, bg="white", highlightthickness=2, relief="ridge")
canvas.pack()

# Rysowanie konturu
glass_outline = canvas.create_rectangle(40, 20, 110, 230, outline="black", width=2)

# Tworzenie prostokąta jako poziom wody
water_fill = canvas.create_rectangle(41, 230, 109, 230, fill="blue", outline="blue")

# Etykieta postępu
intake_label = tb.Label(root, text="", font=("Arial", 12))
intake_label.pack(pady=5)

# Przyciski sterujące
btn_frame = tb.Frame(root)
btn_frame.pack(pady=10)

btn_remove = tb.Button(btn_frame, text="-", command=lambda: remove_water(), width=5)
btn_remove.grid(row=0, column=0, padx=10)

btn_add = tb.Button(btn_frame, text="+", command=lambda: add_water(), width=5)
btn_add.grid(row=0, column=1, padx=10)

# PANEL USTAWIEŃ (schowany domyślnie)
settings_frame = tb.Frame(root, width=200, height=450, style="dark")
settings_frame.place(x=320, y=0)  # Początkowa pozycja poza ekranem

tb.Label(settings_frame, text="Ustawienia", font=("Arial", 14, "bold"), background="#2C2F33").pack(pady=10)

# Suwak celu (skok co 50)
tb.Label(settings_frame, text="Cel (ml):", background="#2C2F33").pack(pady=5)
goal_var = tk.IntVar(value=data["goal"])
goal_label = tb.Label(settings_frame, text=f"Aktualny cel: {goal_var.get()} ml", background="#2C2F33")
goal_label.pack()

def update_goal(value):
    """Zaokrągla wartość suwaka celu do wielokrotności 50."""
    rounded = round(int(float(value)) / 50) * 50
    goal_var.set(rounded)
    goal_label.config(text=f"Aktualny cel: {rounded} ml")

goal_slider = tb.Scale(settings_frame, from_=500, to=5000, variable=goal_var, orient="horizontal", length=180, command=update_goal)
goal_slider.pack()

# Suwak wielkości szklanki (skok co 25)
tb.Label(settings_frame, text="Wielkość szklanki (ml):").pack(pady=5)
glass_var = tk.IntVar(value=data["glass_size"])
glass_label = tb.Label(settings_frame, text=f"Aktualna wielkość szklanki: {glass_var.get()} ml")
glass_label.pack()

def update_glass_size(value):
    """Zaokrągla wartość suwaka rozmiaru szklanki do wielokrotności 25."""
    rounded = round(int(float(value)) / 25) * 25
    glass_var.set(rounded)
    glass_label.config(text=f"Aktualna wielkość szklanki: {rounded} ml")

glass_slider = tb.Scale(settings_frame, from_=100, to=1000, variable=glass_var, orient="horizontal", length=180, command=update_glass_size)
glass_slider.pack()

def update_labels(*args):
    """Aktualizuje etykiety pokazujące aktualnie ustawione wartości."""
    goal_label.config(text=f"Aktualny cel: {goal_var.get()} ml")
    glass_label.config(text=f"Aktualna wielkość szklanki: {glass_var.get()} ml")

# Aktualizacja etykiet przy zmianie wartości slidera
goal_var.trace_add("write", update_labels)
glass_var.trace_add("write", update_labels)

def save_settings():
    """Zapisuje ustawienia i zamyka panel."""
    goal = goal_var.get()
    glass_size = glass_var.get()
    logic.update_settings(data, goal, glass_size)
    refresh_ui()
    toggle_settings()

tb.Button(settings_frame, text="Zapisz", command=save_settings).pack(pady=10)

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
