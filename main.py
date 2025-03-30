import os
import sys
import tkinter as tk
from pathlib import Path
from threading import Thread
from tkinter import Button, PhotoImage, messagebox

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import logic
from drink_detect import WaterDrinkingDetector  # Importowanie klasy detektora
from version import __version__


class WaterTrackerApp:
    """Główna klasa aplikacji śledzącej spożycie wody zarządza UI i interakcjami użytkownika."""

    def __init__(self):
        """Inicjalizuje aplikację, ładuje dane, tworzy okno i interfejs użytkownika."""
        self.canvas = self.current_drop_image = self.drop_image_id = None
        self.intake_label = self.buttons = self.drop_images = self.button_images = None
        self.chart_window = self.chart_canvas = None

        self.output_path = Path(__file__).parent
        self.assets_path = self.output_path / "assets/"
        self.data = logic.load_data()

        self.window = self._create_main_window()
        self.tk_canvas = tk.Canvas(self.window, bg="#555555", height=525, width=372, bd=0, highlightthickness=0,
                                   relief="ridge")
        self.tk_canvas.place(x=0, y=0)

        self.load_assets()
        self.create_widgets()
        self.update_ui()
        self._bind_keys()

        self.water_detector = None

        self.window.mainloop()

    def _create_main_window(self):
        """Tworzy główne okno aplikacji."""
        window = tk.Tk()
        window.geometry("372x475")
        window.title("Tracker Wody")
        window.configure(bg="#555555")
        window.iconbitmap(os.path.join(self.assets_path, "droplet.ico"))
        window.resizable(False, False)
        window.protocol("WM_DELETE_WINDOW", self.on_closing)
        return window

    def _bind_keys(self):
        """Przypisuje skróty klawiaturowe dla dodawania i usuwania wody."""
        for key in "qaz":
            self.window.bind(f"<KeyPress-{key}>", lambda event: self.remove_water())
        for key in "edx":
            self.window.bind(f"<KeyPress-{key}>", lambda event: self.add_water())

    def relative_to_assets(self, path: str) -> Path:
        """Zwraca pełną ścieżkę do zasobów aplikacji."""
        return self.assets_path / path

    def load_assets(self):
        """Ładuje obrazy przycisków i wskaźników postępu."""
        self.button_images = [PhotoImage(file=self.relative_to_assets(f"button_{i + 1}.png")) for i in range(5)]
        self.drop_images = [PhotoImage(file=self.relative_to_assets(f"image_{i}.png")) for i in range(10)]

    def create_widgets(self):
        """Tworzy elementy interfejsu użytkownika, w tym przyciski i etykiety."""
        button_config = [
            (self.open_settings, 324, 0, 48, 48),
            (self.add_water, 251, 340, 66, 66),
            (self.remove_water, 52, 340, 66, 66),
            (lambda: self.create_chart_window(7), 0, 0, 48, 48),
            (self.toggle_water_detection, 150, 340, 66, 66),  # Dodajemy przycisk do uruchomienia detekcji
        ]
        self.buttons = [
            Button(image=self.button_images[i], borderwidth=0, highlightthickness=0, command=config[0], relief="flat")
            .place(x=config[1], y=config[2], width=config[3], height=config[4])
            for i, config in enumerate(button_config)
        ]
        self.intake_label = self.tk_canvas.create_text(186, 286, anchor="center", text="", fill="#FFFFFF",
                                                       font=("RobotoRoman Medium", 14 * -1))
        self.drop_image_id = self.tk_canvas.create_image(184, 157, image=self.drop_images[0])

    def update_ui(self):
        """Aktualizuje interfejs użytkownika na podstawie aktualnych danych."""
        self.tk_canvas.itemconfig(self.intake_label, text=f"{self.data['intake']}/{self.data['goal']}")
        progress = min(9, max(0, int((self.data["intake"] / self.data["goal"]) * 9)))
        self.current_drop_image = self.drop_images[progress]
        self.tk_canvas.itemconfig(self.drop_image_id, image=self.current_drop_image)
        if self.chart_canvas:
            self.update_chart()

    def add_water(self, sip=False):
        """Dodaje wodę do dziennego spożycia i odświeża interfejs."""
        logic.add_water(self.data, sip)
        self.update_ui()

    def remove_water(self):
        """Usuwa wodę z dziennego spożycia i odświeża interfejs."""
        logic.remove_water(self.data)
        self.update_ui()

    def destroy_window(self):
        """Usuwa okno wykresu i resetuje związany z nim Canvas."""
        if self.chart_canvas:
            self.chart_canvas.destroy()
            self.chart_canvas = None

    def create_chart_window(self, days):
        """Tworzy nowe okno wykresu i inicjalizuje Canvas."""
        if not self.chart_canvas:
            self.chart_canvas = tk.Toplevel(self.window)
            self.chart_canvas.title("Historia spożycia wody")
            self.chart_canvas.geometry("800x400")
            self.chart_canvas.configure(bg="#555555")
            self.chart_canvas.protocol("WM_DELETE_WINDOW", self.destroy_window)

            self.figure, self.ax = plt.subplots(figsize=(8, 4))
            self.figure.patch.set_facecolor('#555555')
            self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_canvas)
            self.canvas.get_tk_widget().pack()

        self.update_chart(days)

    def update_chart(self, days=7):
        """Aktualizuje wykres spożycia wody."""
        data = logic.load_data(days)
        dates, intake, goals = zip(*[(entry["date"], entry["intake"], entry["goal"]) for entry in data])

        self.ax.clear()
        self.ax.bar(dates, intake, color='#007aff', label="Spożycie wody")
        self.ax.plot(dates, goals, color='white', marker='o', linestyle='dashed', label="Cel")

        self.ax.set(
            xlabel="Data", ylabel="Ilość wody (ml)", title=f"Spożycie wody - ostatnie {days} dni",
            facecolor='#555555', ylim=(min(intake) - 250, None)
        )
        self.ax.tick_params(axis='x', rotation=45, colors='white')
        self.ax.tick_params(axis='y', colors='white')

        self.ax.title.set_color("white")
        self.ax.xaxis.label.set_color("white")
        self.ax.yaxis.label.set_color("white")

        legend = self.ax.legend(facecolor='#777777', edgecolor='white')
        for text in legend.get_texts():
            text.set_color("white")

        self.figure.subplots_adjust(bottom=0.25)
        self.canvas.draw()

    def open_settings(self):
        """Otwiera okno ustawień, umożliwiające zmianę celu i rozmiaru szklanki."""

        def save_settings():
            """Zapisuje nowe ustawienia celu i rozmiaru szklanki."""
            new_goal, new_glass_size, new_sip_size = goal_slider.get(), glass_slider.get(), sip_slider.get()
            if new_goal <= 0 or new_glass_size <= 0 or new_sip_size <= 0:
                messagebox.showerror("Błąd", "Wartości muszą być większe niż 0!")
            else:
                logic.update_settings(self.data, new_goal, new_glass_size, new_sip_size)
                self.update_ui()
                settings_window.destroy()

        settings_window = tk.Toplevel(self.window)
        settings_window.title("Ustawienia")
        settings_window.geometry("250x330")
        settings_window.configure(bg="#444444")

        tk.Label(settings_window, text="Cel (ml):", bg="#444444", fg="white").pack(pady=5)
        goal_slider = tk.Scale(settings_window, from_=100, to=5000, orient="horizontal", length=200, bg="#444444",
                               fg="white", resolution=50)
        goal_slider.set(self.data["goal"])
        goal_slider.pack(pady=5)

        tk.Label(settings_window, text="Rozmiar szklanki (ml):", bg="#444444", fg="white").pack(pady=5)
        glass_slider = tk.Scale(settings_window, from_=50, to=1000, orient="horizontal", length=200, bg="#444444",
                                fg="white", resolution=25)
        glass_slider.set(self.data["glass_size"])
        glass_slider.pack(pady=5)

        tk.Label(settings_window, text="Rozmiar sip (ml):", bg="#444444", fg="white").pack(pady=5)
        sip_slider = tk.Scale(settings_window, from_=25, to=250, orient="horizontal", length=200, bg="#444444",
                              fg="white", resolution=12.50, digits=4)
        sip_slider.set(self.data["sip_size"])
        sip_slider.pack(pady=5)

        tk.Button(settings_window, text="Zapisz", command=save_settings, bg="#008CBA", fg="white").pack(pady=10)
        tk.Label(settings_window, text=f"Wersja: {__version__}", bg="#444444", fg="white").pack(pady=5)

    def toggle_water_detection(self):
        """Uruchamia lub zatrzymuje detekcję picia wody."""
        if self.water_detector is None:
            self.water_detector = WaterDrinkingDetector(self, detection_interval=10, show_window=False)
            thread = Thread(target=self.water_detector.start_detection)
            thread.daemon = True
            thread.start()
            messagebox.showinfo("Detekcja uruchomiona", "Detekcja picia wody została uruchomiona.")
        else:
            self.water_detector.stop_detection()
            self.water_detector = None
            messagebox.showinfo("Detekcja zatrzymana", "Detekcja picia wody została zatrzymana.")

    def on_closing(self):
        if self.water_detector:
            self.water_detector.stop_detection()
        self.window.destroy()
        sys.exit()

if __name__ == "__main__":
    WaterTrackerApp()
