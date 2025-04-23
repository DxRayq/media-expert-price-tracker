[![Contributors](https://img.shields.io/github/contributors/DxRayq/media-expert-price-tracker?style=flat-square)](https://github.com/DxRayq/media-expert-price-tracker/graphs/contributors) [![Forks](https://img.shields.io/github/forks/DxRayq/media-expert-price-tracker?style=flat-square)](https://github.com/DxRayq/media-expert-price-tracker/network/members) [![Stars](https://img.shields.io/github/stars/DxRayq/media-expert-price-tracker?style=flat-square)](https://github.com/DxRayq/media-expert-price-tracker/stargazers) [![Issues](https://img.shields.io/github/issues/DxRayq/media-expert-price-tracker?style=flat-square)](https://github.com/DxRayq/media-expert-price-tracker/issues) [![License](https://img.shields.io/github/license/DxRayq/media-expert-price-tracker?style=flat-square)](./LICENSE) [![Python Version](https://img.shields.io/badge/python-3.6%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org)

# Media Expert Price Tracker

## Opis
Aplikacja w Pythonie do monitorowania ceny wybranego produktu na stronie `mediaexpert.pl`. Gdy cena spadnie poniżej ustalonego progu, wysyła powiadomienie e-mail. Dodatkowo zapisuje historię cen w pliku CSV i generuje wykres zmian cen.

## Funkcje
*   Pobieranie aktualnej nazwy i ceny produktu z podanego linku URL Media Expert.
*   Zapisywanie historii cen (data, godzina, cena) w pliku CSV.
*   Okresowe sprawdzanie ceny w zadanym interwale.
*   Wysyłanie powiadomień e-mail, gdy cena produktu spadnie poniżej zdefiniowanego progu.
*   Generowanie wykresu historii cen produktu (plik PNG).
*   Wykorzystanie biblioteki `cloudscraper` do obchodzenia podstawowych zabezpieczeń anti-bot (Cloudflare), które mogą blokować standardowe zapytania.

## Wymagania
*   Python 3.6 lub nowszy [![Python Version](https://img.shields.io/badge/python-3.6%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
*   Biblioteki Python (zobacz `requirements.txt`):
    *   `cloudscraper` (i jego zależności, w tym `requests`)
    *   `beautifulsoup4`
    *   `lxml` (jako parser dla BeautifulSoup)
    *   `matplotlib`

## Instalacja
1.  Upewnij się, że masz zainstalowany Python (wersja 3.6+) i narzędzie `pip`.
2.  Sklonuj repozytorium lub pobierz pliki.
    ```bash
    git clone https://github.com/DxRayq/media-expert-price-tracker.git
    cd media-expert-price-tracker
    ```
3.  Przejdź do folderu projektu w terminalu.
4.  Zainstaluj wymagane biblioteki:
    ```bash
    pip install -r requirements.txt
    ```

## Konfiguracja
Przed pierwszym uruchomieniem skryptu `price_tracker.py`, musisz dostosować kilka parametrów bezpośrednio w pliku:

1.  **Ustawienia E-mail:**
    *   `EMAIL_SENDER`: Wpisz swój adres e-mail (obecnie jest zaimplementowany Gmail), który będzie używany do wysyłania powiadomień.
    *   `EMAIL_PASSWORD`: Podaj **Hasło do aplikacji** wygenerowane dla Twojego konta e-mail. Jest to **zdecydowanie zalecane**, zwłaszcza dla Gmaila z włączoną weryfikacją dwuetapową. Znajdziesz je w ustawieniach bezpieczeństwa konta Google. **Nie używaj swojego głównego hasła do konta!** Jeśli nie możesz użyć hasła do aplikacji, może być konieczne włączenie opcji "Dostęp mniej bezpiecznych aplikacji" na koncie e-mail, co jest mniej bezpieczne. (`Bezpieczeństwo -> Weryfikacja dwuetapowa -> Hasła do aplikacji`)
    *   `EMAIL_RECEIVER`: Wpisz adres e-mail, na który chcesz otrzymywać powiadomienia o spadku ceny. Może to być ten sam adres co `EMAIL_SENDER`.
    *   `SMTP_SERVER`: Adres serwera SMTP Twojego dostawcy poczty (`"smtp.gmail.com"` dla Gmaila).
    *   `SMTP_PORT`: Port serwera SMTP (`465` dla Gmaila korzystającego z połączenia SSL).

2.  **Interwał sprawdzania:**
    *   `CHECK_INTERVAL_SECONDS`: Określa, jak często (w sekundach) skrypt ma sprawdzać cenę produktu. Wartość domyślna to `3600` (co oznacza 1 godzinę). **Ważne:** Unikaj ustawiania bardzo małych wartości (np. poniżej kilkunastu minut), aby zminimalizować ryzyko zablokowania przez serwer Media Expert.

3.  **Nazwa pliku CSV (opcjonalnie):**
    *   `CSV_FILE`: Nazwa pliku, w którym będzie przechowywana historia cen. Domyślnie jest to `'price_history.csv'`. Możesz ją zmienić, jeśli chcesz.

## Użycie
1.  Przejdź do folderu projektu w terminalu.
2.  Uruchom skrypt za pomocą polecenia:
    ```bash
    python price_tracker.py
    ```
3.  Program poprosi Cię o wykonanie dwóch czynności:
    *   Wklejenie pełnego linku URL do strony produktu na `mediaexpert.pl`, którego cenę chcesz śledzić.
    *   Podanie progu cenowego (jako liczby, np. `1599` lub `249.50`), poniżej którego skrypt ma wysłać powiadomienie.
4.  Po podaniu danych, skrypt rozpocznie monitorowanie i będzie wyświetlał informacje w terminalu:
    *   Potwierdzenie rozpoczęcia monitorowania i ustawionego progu.
    *   Komunikaty o każdym cyklu sprawdzania ceny (zawierające datę, godzinę i wynik sprawdzenia - znalezioną cenę lub informację o błędzie).
    *   Wyraźne powiadomienie w terminalu, jeśli cena spadnie poniżej progu i zostanie wysłany e-mail.
    *   Informacje o zapisaniu/aktualizacji wykresu cen.
5.  Skrypt będzie działał w pętli, sprawdzając cenę w ustalonych odstępach czasu, aż do momentu jego ręcznego zatrzymania.
6.  Aby zatrzymać działanie skryptu, wróć do okna terminala, w którym jest uruchomiony, i naciśnij kombinację klawiszy `Ctrl + C`.

## Pliki wyjściowe
Podczas działania, skrypt tworzy i/lub aktualizuje następujące pliki w tym samym katalogu, w którym został uruchomiony:

*   **`price_history.csv`**: Plik tekstowy w formacie CSV (Comma Separated Values), który przechowuje historię odczytanych cen dla monitorowanego produktu. Każdy wiersz zawiera:
    *   `timestamp`: Dokładny czas odczytu ceny w formacie ISO 8601.
    *   `url`: Link do produktu.
    *   `product_name`: Odczytana nazwa produktu.
    *   `price`: Odczytana cena produktu.
    Nowe odczyty są dopisywane na końcu pliku.
*   **`price_chart.png`**: Plik graficzny (obraz PNG) zawierający wykres liniowy przedstawiający historię zmian cen monitorowanego produktu. Oś X reprezentuje czas, a oś Y cenę w PLN. Wykres jest generowany lub aktualizowany po każdym pomyślnym odczycie ceny.

## Ważne uwagi
*   **Etyka:** Proszę, używaj tego skryptu w sposób odpowiedzialny i wyłącznie do monitorowania cen na własny użytek. Nadmierne odpytywanie serwera może prowadzić do blokady i jest nieetyczne.
*   **Zmienność stron:** Pamiętaj, że sklepy internetowe często aktualizują swoje strony. Skrypt może wymagać modyfikacji w przyszłości, aby dostosować się do tych zmian. Działanie skryptu nie jest gwarantowane na zawsze.
*   **Ograniczenia:** Skrypt jest zaprojektowany dla strony `mediaexpert.pl`. Próba użycia go na innych stronach najprawdopodobniej się nie powiedzie bez znaczących modyfikacji.

## Zgłaszanie błędów i sugestie
Jeśli znajdziesz błąd lub masz pomysł na nową funkcję, proszę, utwórz zgłoszenie (Issue) w repozytorium GitHub:
[![Issues](https://img.shields.io/github/issues/DxRayq/media-expert-price-tracker?style=flat-square)](https://github.com/DxRayq/media-expert-price-tracker/issues) -> [Utwórz nowe zgłoszenie](https://github.com/DxRayq/media-expert-price-tracker/issues/new/choose)
