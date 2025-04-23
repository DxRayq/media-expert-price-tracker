import cloudscraper
from bs4 import BeautifulSoup
import re
import csv
import os
import time
from datetime import datetime
import smtplib
from email.message import EmailMessage
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

CSV_FILE = 'price_history.csv'
CHECK_INTERVAL_SECONDS = 3600 # co ile sekund ma się odświeżać sprawdzanie ceny

# fill in your details
EMAIL_SENDER = "test@gmail.com"  # Adres e-mail z którego będziesz wysyłać
EMAIL_PASSWORD = ""  # Hasło (PRZECZYTAJ README!!!)
EMAIL_RECEIVER = "" # Adres e-mail do którego będziesz otrzymywać maile

SMTP_SERVER = "smtp.gmail.com"  # Dla Gmaila
SMTP_PORT = 465 # Dla Gmaila z SSL

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.google.com/', 
    'DNT': '1', 
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

def get_product_info(url, scraper):
    try:
        response = scraper.get(url, headers=HEADERS, timeout=20)
        print(f"Status odpowiedzi: {response.status_code}")
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        name_tag = soup.find('h1', attrs={'itemprop': 'name'})
        if name_tag:
            product_name = name_tag.text.strip()
        else:
            name_tag = soup.select_one('h1.pd-name')
            product_name = name_tag.text.strip() if name_tag else "Nie znaleziono nazwy"

        price_box = soup.find('div', attrs={'data-zone': 'pricebox'})
        price_whole = None
        price_penny = '00'

        if price_box:
            possible_whole_classes = ['a-price_price', 'is-big .whole', 'whole', '.price .a-price_price']
            for selector in possible_whole_classes:
                 whole_tag = price_box.select_one(selector)
                 if whole_tag:
                     price_whole = whole_tag.text.strip()
                     break
            penny_tag = price_box.select_one('.a-price_penny')
            if penny_tag:
                price_penny = penny_tag.text.strip()

        if not price_whole:
            meta_price_tag = soup.find('meta', attrs={'property': 'product:price:amount'})
            if meta_price_tag and meta_price_tag.get('content'):
                price_str_meta = meta_price_tag['content']
                if '.' in price_str_meta:
                     parts = price_str_meta.split('.')
                     price_whole = parts[0]
                     price_penny = parts[1] if len(parts) > 1 else '00'
                else:
                     price_whole = price_str_meta
                     price_penny = '00'

        if price_whole:
            price_whole_cleaned = re.sub(r'\D', '', price_whole)
            price_penny_cleaned = re.sub(r'\D', '', price_penny).ljust(2, '0') 

            if price_whole_cleaned:
                 full_price_str = f"{price_whole_cleaned}.{price_penny_cleaned}"
                 try:
                     price_float = float(full_price_str)
                     return product_name, price_float
                 except ValueError:
                     print(f"Błąd: Nie można przekonwertować ceny '{full_price_str}' na liczbę.")
                     return product_name, None
            else:
                print("Błąd: Nie udało się wyodrębnić części całkowitej ceny.")
                return product_name, None
        else:
            print("Błąd: Nie znaleziono elementu ceny na stronie.")
            price_tag_data = soup.find(attrs={'data-price': True})
            if price_tag_data and price_tag_data['data-price']:
                 try:
                     price_float = float(price_tag_data['data-price'])
                     print(f"Znaleziono cenę w atrybucie data-price: {price_float}")
                     return product_name, price_float
                 except (ValueError, KeyError):
                    print("Nie udało się pobrać ceny z atrybutu data-price.")
                    return product_name, None
            else:
                 return product_name, None

    except requests.exceptions.RequestException as e:
        print(f"Błąd połączenia: {e}")
        if hasattr(e, 'response') and e.response is not None:
             print(f"Treść odpowiedzi (fragment): {e.response.text[:500]}")
        return "Błąd połączenia", None
    except Exception as e:
         print(f"Wystąpił nieoczekiwany błąd: {e}")
         return "Błąd przetwarzania strony", None


def save_price(url, product_name, price):
    file_exists = os.path.isfile(CSV_FILE)
    now = datetime.now().isoformat()

    try:
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['timestamp', 'url', 'product_name', 'price']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists or os.path.getsize(CSV_FILE) == 0:
                writer.writeheader()

            writer.writerow({'timestamp': now, 'url': url, 'product_name': product_name, 'price': price})
    except IOError as e:
        print(f"Błąd zapisu do pliku CSV ({CSV_FILE}): {e}")
    except Exception as e:
        print(f"Nieoczekiwany błąd podczas zapisu do CSV: {e}")


def load_prices(url_filter):
    timestamps = []
    prices = []
    product_name = "Produkt"

    if not os.path.isfile(CSV_FILE):
        print(f"Plik historii {CSV_FILE} nie istnieje.")
        return timestamps, prices, product_name

    try:
        with open(CSV_FILE, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            sorted_rows = sorted(reader, key=lambda row: row['timestamp'])

            for row in sorted_rows:
                if row['url'] == url_filter:
                    try:
                        if row['price'] and row['price'].lower() != 'none':
                           timestamps.append(datetime.fromisoformat(row['timestamp']))
                           prices.append(float(row['price']))
                           if row.get('product_name'):
                                product_name = row['product_name']
                        else:
                            print(f"Pominięto wpis z pustą ceną: {row}")
                    except (ValueError, TypeError) as e:
                         print(f"Błąd konwersji danych w wierszu: {row}. Błąd: {e}")
                    except Exception as e:
                        print(f"Nieoczekiwany błąd podczas odczytu wiersza: {row}. Błąd: {e}")

    except FileNotFoundError:
        print(f"Plik {CSV_FILE} nie został znaleziony.")
    except IOError as e:
        print(f"Błąd odczytu pliku CSV ({CSV_FILE}): {e}")
    except Exception as e:
        print(f"Nieoczekiwany błąd podczas odczytu CSV: {e}")

    return timestamps, prices, product_name


def plot_prices(timestamps, prices, product_name, filename="price_chart.png"):
    if not timestamps or not prices:
        print("Brak danych do wygenerowania wykresu.")
        return

    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, prices, marker='o', linestyle='-')

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5, maxticks=10)) 
    plt.gcf().autofmt_xdate()

    plt.title(f'Historia cen dla: {product_name[:50]}...')
    plt.xlabel('Data i godzina')
    plt.ylabel('Cena (PLN)')
    plt.grid(True)
    plt.tight_layout()

    try:
        plt.savefig(filename)
        print(f"Wykres zapisany jako: {filename}")
    except Exception as e:
        print(f"Błąd podczas zapisywania wykresu: {e}")


def send_email_notification(subject, body):
    if not EMAIL_SENDER or not EMAIL_PASSWORD or not EMAIL_RECEIVER:
        print("Błąd: Dane do wysyłki e-mail nie są skonfigurowane.")
        return

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    try:
        print("Łączenie z serwerem SMTP...")
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            print("Logowanie do konta e-mail...")
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            print("Wysyłanie e-maila...")
            server.send_message(msg)
            print("Powiadomienie e-mail wysłane pomyślnie!")
    except smtplib.SMTPAuthenticationError:
        print("Błąd autentykacji SMTP. Sprawdź login/hasło (lub hasło do aplikacji).")
        print("Upewnij się też, że zezwolono na dostęp mniej bezpiecznych aplikacji lub używasz hasła do aplikacji (zalecane).")
    except smtplib.SMTPServerDisconnected:
        print("Serwer SMTP rozłączył się niespodziewanie.")
    except smtplib.SMTPException as e:
        print(f"Błąd SMTP: {e}")
    except Exception as e:
        print(f"Nieoczekiwany błąd podczas wysyłania e-maila: {e}")

if __name__ == "__main__":
    product_url = input("Wklej link do produktu na Media Expert: ")
    while True:
        try:
            threshold_str = input("Powiadom mnie, gdy cena spadnie poniżej (PLN): ")
            price_threshold = float(threshold_str)
            break
        except ValueError:
            print("Nieprawidłowa wartość. Wpisz liczbę (np. 1500.50).")

    scraper = cloudscraper.create_scraper()

    print(f"Rozpoczynam monitorowanie produktu: {product_url}")
    print(f"Powiadomienie zostanie wysłane, gdy cena spadnie poniżej {price_threshold:.2f} PLN.")
    print(f"Sprawdzanie co {CHECK_INTERVAL_SECONDS // 60} minut.")
    print("-" * 30)

    last_notified_price = float('inf')

    try:
        while True:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Sprawdzam cenę...")
            product_name, current_price = get_product_info(product_url, scraper)

            if current_price is not None:
                print(f"   Produkt: {product_name}")
                print(f"   Aktualna cena: {current_price:.2f} PLN")
                save_price(product_url, product_name, current_price)

                if current_price < price_threshold:
                    if current_price < last_notified_price:
                        print(f"!!! Cena {current_price:.2f} PLN jest poniżej progu {price_threshold:.2f} PLN!")
                        subject = f"ALERT CENOWY: {product_name[:30]}..."
                        body = (
                            f"Cena produktu spadła poniżej Twojego progu!\n\n"
                            f"Produkt: {product_name}\n"
                            f"Link: {product_url}\n\n"
                            f"Aktualna cena: {current_price:.2f} PLN\n"
                            f"Twój próg: {price_threshold:.2f} PLN"
                        )
                        send_email_notification(subject, body)
                        last_notified_price = current_price
                    else:
                         print(f"Cena {current_price:.2f} PLN jest poniżej progu, ale już o tym (lub niższej cenie) powiadomiono.")
                else:
                    if last_notified_price < price_threshold:
                         print("Cena wzrosła powyżej progu - resetuję flagę powiadomienia.")
                         last_notified_price = float('inf')


                timestamps, prices, name_for_plot = load_prices(product_url)
                plot_prices(timestamps, prices, name_for_plot)

            else:
                print("   Nie udało się pobrać aktualnej ceny.")

            print(f"Następne sprawdzenie za {CHECK_INTERVAL_SECONDS // 60} minut...")
            print("-" * 30)
            time.sleep(CHECK_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nZatrzymano monitorowanie.")
        print("Generowanie końcowego wykresu...")
        timestamps, prices, name_for_plot = load_prices(product_url)
        plot_prices(timestamps, prices, name_for_plot)
        print("Zakończono.")
    except Exception as e:
        print(f"\nWystąpił krytyczny błąd: {e}")
        import traceback
        traceback.print_exc()