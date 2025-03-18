# Water Tracker App

Aplikacja do śledzenia spożycia wody, umożliwiająca ustawienie dziennego celu oraz rozmiaru szklanki. Użytkownik może
dodawać lub usuwać wodę z dziennego spożycia, a interfejs graficzny aktualizuje się na bieżąco, pokazując postęp w
osiąganiu celu.

## Wymagania

- Python 3.x
- Tkinter (do interfejsu graficznego)
- JSON (do przechowywania danych)

## Instalacja

1. Zainstaluj wymagane biblioteki (jeśli nie są zainstalowane):

   ```bash
   pip install tkinter
    ```

2. Pobierz lub sklonuj repozytorium.
3. Upewnij się, że pliki zasobów (ikony, obrazy) znajdują się w folderze assets w tym samym katalogu co skrypt.

## Uruchomienie aplikacji

1. Uruchom plik `main.py`: 
    ```bash
    python main.py
    ```
2. Aplikacja uruchomi się w oknie GUI, gdzie można zarządzać dziennym spożyciem wody, ustawić cel i rozmiar szklanki, a
   także dodawać lub usuwać wodę.

## Funkcje aplikacji

1. Dodaj wodę: Zwiększa dzienne spożycie wody o wartość rozmiaru szklanki.
2. Usuń wodę: Zmniejsza dzienne spożycie wody o wartość rozmiaru szklanki, ale nie pozwala na wartość mniejszą niż 0.
3. Ustawienia: Umożliwia zmianę celu dziennego (w ml) oraz rozmiaru szklanki.

## Jak to działa

1. Ładowanie danych: Aplikacja wczytuje dane z pliku JSON. Jeśli dane na dzisiejszy dzień nie istnieją, zostaną
   utworzone nowe z domyślnymi wartościami.
2. Zarządzanie spożyciem wody: Użytkownik może dodawać lub usuwać wodę, a interfejs odświeża się, wyświetlając postęp w
   osiągnięciu celu.
3. Zapis danych: Wszystkie zmiany są zapisywane do pliku `water_data.json`, dzięki czemu dane są przechowywane pomiędzy
   sesjami.

## Licencja

Ten projekt jest udostępniany na licencji MIT. Można go dowolnie modyfikować i wykorzystywać.
