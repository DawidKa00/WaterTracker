import os
import tkinter as tk
from pathlib import Path
from tkinter import Canvas, Button, PhotoImage, messagebox

import logic


class WaterTrackerApp:
    """Główna klasa aplikacji śledzącej spożycie wody, zarządza UI i interakcjami użytkownika."""

    def __init__(self):
        """Inicjalizuje aplikację, ładuje dane, tworzy okno i interfejs użytkownika."""
        self.output_path = Path(__file__).parent
        self.assets_path = self.output_path / "assets/"

        self.data = logic.load_data()

        self.window = tk.Tk()
        self.window.geometry("372x475")
        self.window.configure(bg="#555555")
        self.window.title("Tracker Wody")
        self.window.iconbitmap(os.path.join(self.assets_path, "droplet.ico"))
        self.window.resizable(False, False)

        self.canvas = Canvas(
            self.window, bg="#555555", height=525, width=372,
            bd=0, highlightthickness=0, relief="ridge"
        )
        self.canvas.place(x=0, y=0)

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
            PhotoImage(file=self.relative_to_assets("button_3.png"))
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
                   command=self.remove_water, relief="flat")
        ]
        self.buttons[0].place(x=324, y=0, width=48, height=48)
        self.buttons[1].place(x=251, y=340, width=66, height=66)
        self.buttons[2].place(x=52, y=338, width=66, height=66)

        self.intake_label = self.canvas.create_text(
            186, 286, anchor="center", text="", fill="#FFFFFF", font=("RobotoRoman Medium", 14 * -1)
        )
        self.drop_image_id = self.canvas.create_image(184, 157, image=self.drop_images[0])

    def update_ui(self):
        """Aktualizuje interfejs użytkownika na podstawie aktualnych danych."""
        self.canvas.itemconfig(self.intake_label, text=f"{self.data['intake']}/{self.data['goal']}")
        progress = min(9, max(0, int((self.data["intake"] / self.data["goal"]) * 9)))

        # Ustawienie nowego obrazu kropli
        self.current_drop_image = self.drop_images[progress]
        self.canvas.delete(self.drop_image_id)  # Usuwamy poprzedni obraz

        # Tworzymy nowy obraz w tym samym miejscu
        self.drop_image_id = self.canvas.create_image(184, 157, image=self.current_drop_image)

    def add_water(self):
        """Dodaje wodę do dziennego spożycia i odświeża interfejs."""
        logic.add_water(self.data)
        self.update_ui()

    def remove_water(self):
        """Usuwa wodę z dziennego spożycia i odświeża interfejs."""
        logic.remove_water(self.data)
        self.update_ui()

    def open_settings(self):
        """Otwiera okno ustawień, umożliwiające zmianę celu i rozmiaru szklanki."""
        settings_window = tk.Toplevel(self.window)
        settings_window.title("Ustawienia")
        settings_window.geometry("250x200")
        settings_window.configure(bg="#444444")

        tk.Label(settings_window, text="Cel (ml):", bg="#444444", fg="white").pack(pady=5)
        goal_entry = tk.Entry(settings_window)
        goal_entry.insert(0, str(self.data["goal"]))
        goal_entry.pack(pady=5)

        tk.Label(settings_window, text="Rozmiar szklanki (ml):", bg="#444444", fg="white").pack(pady=5)
        glass_entry = tk.Entry(settings_window)
        glass_entry.insert(0, str(self.data["glass_size"]))
        glass_entry.pack(pady=5)

        def save_settings():
            """Zapisuje nowe ustawienia celu i rozmiaru szklanki, jeśli są poprawne."""
            try:
                new_goal = int(goal_entry.get())
                new_glass_size = int(glass_entry.get())
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


if __name__ == "__main__":
    WaterTrackerApp()
