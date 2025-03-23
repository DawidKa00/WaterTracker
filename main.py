import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import Button, PhotoImage, messagebox

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from setuptools_scm import get_version

import logic


class WaterTrackerApp:
    """Główna klasa aplikacji śledzącej spożycie wody zarządza UI i interakcjami użytkownika."""

    def __init__(self):
        """Inicjalizuje aplikację, ładuje dane, tworzy okno i interfejs użytkownika."""
        self.canvas = None
        self.current_drop_image = None
        self.drop_image_id = None
        self.intake_label = None
        self.buttons = None
        self.drop_images = None
        self.button_images = None
        self.chart_window = None
        self.output_path = Path(__file__).parent
        self.assets_path = self.output_path / "assets/"

        self.data = logic.load_data()

        self.window = tk.Tk()
        self.window.geometry("372x475")
        self.window.configure(bg="#555555")
        self.window.title("Tracker Wody")
        self.window.iconbitmap(os.path.join(self.assets_path, "droplet.ico"))
        self.window.resizable(False, False)

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.tk_canvas = tk.Canvas(
            self.window, bg="#555555", height=525, width=372,
            bd=0, highlightthickness=0, relief="ridge"
        )
        self.tk_canvas.place(x=0, y=0)

        self.chart_canvas = None

        self.load_assets()
        self.create_widgets()
        self.update_ui()

        self.window.bind("<KeyPress-q>", lambda event: self.remove_water())
        self.window.bind("<KeyPress-a>", lambda event: self.remove_water())
        self.window.bind("<KeyPress-z>", lambda event: self.remove_water())
        self.window.bind("<KeyPress-e>", lambda event: self.add_water())
        self.window.bind("<KeyPress-d>", lambda event: self.add_water())
        self.window.bind("<KeyPress-x>", lambda event: self.add_water())

        self.window.mainloop()

    def relative_to_assets(self, path: str) -> Path:
        """Zwraca pełną ścieżkę do zasobów aplikacji."""
        """Ładuje obrazy przycisków i wskaźników postępu."""
        return self.assets_path / path

    def load_assets(self):
        """Ładuje obrazy przycisków i wskaźników postępu."""
        self.button_images = [
            PhotoImage(file=self.relative_to_assets("button_1.png")),
            PhotoImage(file=self.relative_to_assets("button_2.png")),
            PhotoImage(file=self.relative_to_assets("button_3.png")),
            PhotoImage(file=self.relative_to_assets("button_4.png"))
        ]
        self.drop_images = [
            PhotoImage(file=self.relative_to_assets(f"image_{i}.png")) for i in range(10)
        ]

    def create_widgets(self):
        """Tworzy elementy interfejsu użytkownika, w tym przyciski i etykiety."""
        self.buttons = [
            Button(image=self.button_images[0], borderwidth=0, highlightthickness=0,
                   command=self.open_settings, relief="flat"),
            Button(image=self.button_images[1], borderwidth=0, highlightthickness=0,
                   command=self.add_water, relief="flat"),
            Button(image=self.button_images[2], borderwidth=0, highlightthickness=0,
                   command=self.remove_water, relief="flat"),
            Button(image=self.button_images[3], borderwidth=0, highlightthickness=0,
                   command=lambda: self.create_chart_window(7), relief="flat")
        ]
        self.buttons[0].place(x=324, y=0, width=48, height=48)
        self.buttons[1].place(x=251, y=340, width=66, height=66)
        self.buttons[2].place(x=52, y=338, width=66, height=66)
        self.buttons[3].place(x=0, y=0, width=48, height=48)

        self.intake_label = self.tk_canvas.create_text(
            186, 286, anchor="center", text="", fill="#FFFFFF", font=("RobotoRoman Medium", 14 * -1)
        )
        self.drop_image_id = self.tk_canvas.create_image(184, 157, image=self.drop_images[0])

    def update_ui(self):
        """Aktualizuje interfejs użytkownika na podstawie aktualnych danych."""
        self.tk_canvas.itemconfig(self.intake_label, text=f"{self.data['intake']}/{self.data['goal']}")

        progress = min(9, max(0, int((self.data["intake"] / self.data["goal"]) * 9)))
        self.current_drop_image = self.drop_images[progress]

        self.tk_canvas.delete(self.drop_image_id)
        self.drop_image_id = self.tk_canvas.create_image(184, 157, image=self.current_drop_image)

        if self.chart_canvas:
            self.update_chart()
    def add_water(self):
        """Dodaje wodę do dziennego spożycia i odświeża interfejs."""
        logic.add_water(self.data)
        self.update_ui()

    def remove_water(self):
        """Usuwa wodę z dziennego spożycia i odświeża interfejs."""
        logic.remove_water(self.data)
        self.update_ui()

    def create_chart_window(self, days):
        """Tworzy nowe okno wykresu i inicjalizuje Canvas."""
        if not self.chart_canvas:
            self.chart_canvas = tk.Toplevel(self.window)
            self.chart_canvas.title("Historia spożycia wody")
            self.chart_canvas.geometry("800x400")
            self.chart_canvas.configure(bg="#555555")

            self.chart_canvas.protocol("WM_DELETE_WINDOW", self.chart_canvas.destroy)

            self.figure, self.ax = plt.subplots(figsize=(8, 4))
            self.figure.patch.set_facecolor('#555555')  # Ustawienie tła całej figury
            self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_canvas)
            self.canvas.get_tk_widget().pack()
        else:
            self.chart_canvas.focus()

        self.update_chart(days)

    def update_chart(self, days=7):
        """Aktualizuje wykres spożycia wody."""
        data = logic.load_data(days)

        dates = [entry["date"] for entry in data]
        intake = [entry["intake"] for entry in data]
        goals = [entry["goal"] for entry in data]

        self.ax.clear()

        self.ax.bar(dates, intake, color='#007aff', label="Spożycie wody")
        self.ax.plot(dates, goals, color='white', marker='o', linestyle='dashed', label="Cel")

        self.ax.set_xlabel("Data", color='white')
        self.ax.set_ylabel("Ilość wody (ml)", color='white')
        self.ax.set_title(f"Spożycie wody - ostatnie {days} dni", color='white')

        self.ax.set_ylim(bottom=min(intake) - 250)
        self.ax.set_facecolor('#555555')  # Tło samego wykresu

        self.ax.tick_params(axis='x', rotation=45, colors='white')  # Kolor wartości na osi X
        self.ax.tick_params(axis='y', colors='white')  # Kolor wartości na osi Y

        legend = self.ax.legend(facecolor='#777777', edgecolor='white')  # Tło legendy i ramka
        for text in legend.get_texts():
            text.set_color("white")  # Kolor tekstu w legendzie

        self.figure.subplots_adjust(bottom=0.25)
        self.canvas.draw()

    def open_settings(self):
        """Otwiera okno ustawień, umożliwiające zmianę celu i rozmiaru szklanki."""
        settings_window = tk.Toplevel(self.window)
        settings_window.title("Ustawienia")
        settings_window.geometry("250x250")
        settings_window.configure(bg="#444444")

        # Cel (ml) z suwakiem
        tk.Label(settings_window, text="Cel (ml):", bg="#444444", fg="white").pack(pady=5)
        goal_slider = tk.Scale(settings_window, from_=100, to=5000, orient="horizontal",
                               length=200, sliderlength=20, bg="#444444", fg="white", resolution=50)
        goal_slider.set(self.data["goal"])  # Ustawiamy wartość początkową
        goal_slider.pack(pady=5)

        # Rozmiar szklanki (ml) z suwakiem
        tk.Label(settings_window, text="Rozmiar szklanki (ml):", bg="#444444", fg="white").pack(pady=5)
        glass_slider = tk.Scale(settings_window, from_=50, to=1000, orient="horizontal",
                                length=200, sliderlength=20, bg="#444444", fg="white", resolution=25)
        glass_slider.set(self.data["glass_size"])  # Ustawiamy wartość początkową
        glass_slider.pack(pady=5)

        def save_settings():
            """Zapisuje nowe ustawienia celu i rozmiaru szklanki, jeśli są poprawne."""
            try:
                new_goal = int(goal_slider.get())
                new_glass_size = int(glass_slider.get())
                if new_goal <= 0 or new_glass_size <= 0:
                    messagebox.showerror("Błąd", "Wartości muszą być większe niż 0!")
                    return
                logic.update_settings(self.data, new_goal, new_glass_size)
                self.update_ui()
                settings_window.destroy()
            except ValueError:
                messagebox.showerror("Błąd", "Podaj poprawne liczby!")

        save_button = tk.Button(settings_window, text="Zapisz", command=save_settings, bg="#008CBA", fg="white")
        save_button.pack(pady=10)

        version_label = tk.Label(settings_window, text=f"Wersja: {get_version()}", bg="#444444",
                                 fg="white")
        version_label.pack(pady=5)

    def on_closing(self):
        self.window.destroy()
        sys.exit()

if __name__ == "__main__":
    WaterTrackerApp()
