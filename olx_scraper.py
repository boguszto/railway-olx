import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import time
import schedule
from datetime import datetime

# 👉 KONFIGURACJA
URL = 'https://www.olx.pl/nieruchomosci/regietow/?search%5Bdist%5D=15&search%5Border%5D=created_at:desc'
EMAIL_OD = 'twojemail@gmail.com'
EMAIL_HASLO = 'twojehasloaplikacji'  # Hasło aplikacji Gmail, nie zwykłe!
EMAIL_DO = 'adresdociebie@example.com'


# 👉 WYSYŁKA MAILA
def wyslij_maila(ogloszenia):
    if not ogloszenia:
        return
    tresc = ''
    for ogloszenie in ogloszenia:
        tresc += f"{ogloszenie['tytul']}\n{ogloszenie['lokalizacja']} - {ogloszenie['cena']}\n{ogloszenie['link']}\n\n"

    msg = MIMEText(tresc)
    msg['Subject'] = f'Nowe ogłoszenia OLX ({len(ogloszenia)}) - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
    msg['From'] = EMAIL_OD
    msg['To'] = EMAIL_DO

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_OD, EMAIL_HASLO)
        server.sendmail(EMAIL_OD, EMAIL_DO, msg.as_string())

# 👉 SPRAWDZANIE STRONY
ostatnie_id = set()

def sprawdz_olx():
    global ostatnie_id
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Sprawdzam ogłoszenia...")

    headers = {'User-Agent': 'Mozilla/5.0'}
    r = requests.get(URL, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    ogloszenia = []
    for oferta in soup.select('div[data-cy="l-card"]'):
        link_tag = oferta.select_one('a')
        if not link_tag:
            continue

        link = 'https://www.olx.pl' + link_tag['href']
        tytul = oferta.select_one('h6').text.strip() if oferta.select_one('h6') else 'Brak tytułu'
        lokalizacja = oferta.select_one('p.css-1a4brun').text.strip() if oferta.select_one('p.css-1a4brun') else 'Brak lokalizacji'
        cena = oferta.select_one('p.css-10b0gli').text.strip() if oferta.select_one('p.css-10b0gli') else 'Brak ceny'

        ogloszenie_id = link.split('/')[-2]
        if ogloszenie_id not in ostatnie_id:
            ogloszenia.append({
                'tytul': tytul,
                'lokalizacja': lokalizacja,
                'cena': cena,
                'link': link
            })
            ostatnie_id.add(ogloszenie_id)

    if ogloszenia:
        print(f"Znaleziono {len(ogloszenia)} nowych ogłoszeń.")
        wyslij_maila(ogloszenia)
    else:
        print("Brak nowych ogłoszeń.")

# 👉 PLANOWANIE CO 30 MINUT
schedule.every(30).minutes.do(sprawdz_olx)

print("Bot OLX uruchomiony. Sprawdzanie co 30 minut...")
sprawdz_olx()

while True:
    schedule.run_pending()
    time.sleep(1)
