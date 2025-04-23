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
*   Python 3.6 lub nowszy
*   Biblioteki Python:
    *   `cloudscraper` (i jego zależności, w tym `requests`)
    *   `beautifulsoup4`
    *   `lxml` (jako parser dla BeautifulSoup)
    *   `matplotlib`

## Instalacja
1.  Upewnij się, że masz zainstalowany Python i narzędzie `pip`.
2.  Otwórz terminal lub wiersz poleceń w swoim systemie.
3.  Zainstaluj wszystkie wymagane biblioteki za pomocą poniższego polecenia:
    ```bash
    pip install cloudscraper beautifulsoup4 lxml matplotlib
    ```

## Konfiguracja
Przed pierwszym uruchomieniem skryptu `price_tracker.py`, musisz dostosować kilka parametrów bezpośrednio w pliku:

1.  **Ustawienia E-mail (w sekcji `# --- Konfiguracja ---`):**
    *   `EMAIL_SENDER`: Wpisz swój adres e-mail (np. Gmail), który będzie używany do wysyłania powiadomień.
    *   `EMAIL_PASSWORD`: Podaj **Hasło do aplikacji** wygenerowane dla Twojego konta e-mail. Jest to **zdecydowanie zalecane**, zwłaszcza dla Gmaila z włączoną weryfikacją dwuetapową. Znajdziesz je w ustawieniach bezpieczeństwa konta Google. **Nie używaj swojego głównego hasła do konta!** Jeśli nie możesz użyć hasła do aplikacji, może być konieczne włączenie opcji "Dostęp mniej bezpiecznych aplikacji" na koncie e-mail, co jest mniej bezpieczne.
    *   `EMAIL_RECEIVER`: Wpisz adres e-mail, na który chcesz otrzymywać powiadomienia o spadku ceny. Może to być ten sam adres co `EMAIL_SENDER`.
    *   `SMTP_SERVER`: Adres serwera SMTP Twojego dostawcy poczty (np. `"smtp.gmail.com"` dla Gmaila).
    *   `SMTP_PORT`: Port serwera SMTP (np. `465` dla Gmaila korzystającego z połączenia SSL).

2.  **Interwał sprawdzania (w sekcji `# --- Konfiguracja ---`):**
    *   `CHECK_INTERVAL_SECONDS`: Określa, jak często (w sekundach) skrypt ma sprawdzać cenę produktu. Wartość domyślna to `3600` (co oznacza 1 godzinę). **Ważne:** Unikaj ustawiania bardzo małych wartości (np. poniżej kilkunastu minut), aby zminimalizować ryzyko zablokowania przez serwer Media Expert.

3.  **Nazwa pliku CSV (opcjonalnie):**
    *   `CSV_FILE`: Nazwa pliku, w którym będzie przechowywana historia cen. Domyślnie jest to `'price_history.csv'`. Możesz ją zmienić, jeśli chcesz.

## Użycie
1.  Zapisz kod programu jako plik, na przykład `price_tracker.py`.
2.  Upewnij się, że poprawnie skonfigurowałeś parametry e-mail i interwał sprawdzania w pliku.
3.  Otwórz terminal lub wiersz poleceń, przejdź do folderu, w którym zapisałeś plik.
4.  Uruchom skrypt za pomocą polecenia:
    ```bash
    python price_tracker.py
    ```
5.  Program poprosi Cię o wykonanie dwóch czynności:
    *   Wklejenie pełnego linku URL do strony produktu na `mediaexpert.pl`, którego cenę chcesz śledzić.
    *   Podanie progu cenowego (jako liczby, np. `1599` lub `249.50`), poniżej którego skrypt ma wysłać powiadomienie.
6.  Po podaniu danych, skrypt rozpocznie monitorowanie i będzie wyświetlał informacje w terminalu:
    *   Potwierdzenie rozpoczęcia monitorowania i ustawionego progu.
    *   Komunikaty o każdym cyklu sprawdzania ceny (zawierające datę, godzinę i wynik sprawdzenia - znalezioną cenę lub informację o błędzie).
    *   Wyraźne powiadomienie w terminalu, jeśli cena spadnie poniżej progu i zostanie wysłany e-mail.
    *   Informacje o zapisaniu/aktualizacji wykresu cen.
7.  Skrypt będzie działał w pętli, sprawdzając cenę w ustalonych odstępach czasu, aż do momentu jego ręcznego zatrzymania.
8.  Aby zatrzymać działanie skryptu, wróć do okna terminala, w którym jest uruchomiony, i naciśnij kombinację klawiszy `Ctrl + C`.

## Pliki wyjściowe
Podczas działania, skrypt tworzy i/lub aktualizuje następujące pliki w tym samym katalogu, w którym został uruchomiony:

*   **`price_history.csv`**: Plik tekstowy w formacie CSV (Comma Separated Values), który przechowuje historię odczytanych cen dla monitorowanego produktu. Każdy wiersz zawiera:
    *   `timestamp`: Dokładny czas odczytu ceny w formacie ISO 8601.
    *   `url`: Link do produktu.
    *   `product_name`: Odczytana nazwa produktu.
    *   `price`: Odczytana cena produktu.
    Nowe odczyty są dopisywane na końcu pliku.
*   **`price_chart.png`**: Plik graficzny (obraz PNG) zawierający wykres liniowy przedstawiający historię zmian cen monitorowanego produktu. Oś X reprezentuje czas, a oś Y cenę w PLN. Wykres jest generowany lub aktualizowany po każdym pomyślnym odczycie ceny.

## Rozwiązywanie problemów
*   **Błąd 403 Forbidden:** Mimo użycia `cloudscraper`, bardzo agresywne zabezpieczenia strony mogą nadal blokować skrypt. W takim przypadku:
    *   Spróbuj zwiększyć `CHECK_INTERVAL_SECONDS`.
    *   Upewnij się, że `cloudscraper` jest aktualny (`pip install --upgrade cloudscraper`).
    *   W ostateczności może być konieczne użycie bardziej zaawansowanych technik jak Selenium/Playwright (sterowanie przeglądarką) lub proxy.
    *   Czasami problem może być tymczasowy (np. blokada IP) - spróbuj ponownie później.
*   **Nie znaleziono ceny / Nie znaleziono nazwy / Błąd przetwarzania strony:** Strona `mediaexpert.pl` mogła zmienić swoją strukturę HTML. Skrypt opiera się na specyficznych elementach strony (tagi, klasy, atrybuty) do znalezienia danych. Jeśli wystąpią zmiany, skrypt może przestać działać poprawnie. Konieczne będzie wtedy:
    1.  Zbadanie kodu źródłowego strony produktu w przeglądarce (Narzędzia deweloperskie - F12).
    2.  Zidentyfikowanie nowych selektorów CSS lub tagów HTML zawierających nazwę i cenę.
    3.  Zaktualizowanie odpowiednich fragmentów kodu w funkcji `get_product_info` w pliku `price_tracker.py`.
*   **Błędy SMTP (wysyłanie e-mail):**
    *   Dokładnie sprawdź poprawność `EMAIL_SENDER`, `EMAIL_PASSWORD` (czy na pewno jest to hasło do aplikacji?), `SMTP_SERVER` i `SMTP_PORT`.
    *   Sprawdź ustawienia bezpieczeństwa swojego konta e-mail (czy dostęp dla aplikacji jest włączony, czy nie ma blokad bezpieczeństwa).
    *   Upewnij się, że Twoja sieć lub firewall nie blokują połączeń wychodzących na porcie `SMTP_PORT`.

## Ważne uwagi
*   **Etyka:** Proszę, używaj tego skryptu w sposób odpowiedzialny i wyłącznie do monitorowania cen na własny użytek. Nadmierne odpytywanie serwera może prowadzić do blokady i jest nieetyczne.
*   **Zmienność stron:** Pamiętaj, że sklepy internetowe często aktualizują swoje strony. Skrypt może wymagać modyfikacji w przyszłości, aby dostosować się do tych zmian. Działanie skryptu nie jest gwarantowane na zawsze.
*   **Ograniczenia:** Skrypt jest zaprojektowany dla strony `mediaexpert.pl`. Próba użycia go na innych stronach najprawdopodobniej się nie powiedzie bez znaczących modyfikacji.
