import requests
from bs4 import BeautifulSoup
import pandas as pd
from termcolor import colored

URL = "https://secondlifestorage.com/index.php?pages/cell-database/"
OUTPUT_FILE = "resultats.csv"

# Retourne le contenu d'une page
def get_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    }

    # On récupère la page
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Le chargement de la page {url} a échoué avec le code de statut :", response.status_code)
        print("")
        
        return False
    
    
    # Analyser le HTML de la page
    soup = BeautifulSoup(response.text, 'html.parser')

    return soup


# Récupère les données de la page principale
def get_data(data):

    page = get_page(URL)
    if not page:
        return
    
    # Si la page contient un captcha, on n'a pas accès aux données
    if "captcha" in page.get_text(separator=" ").strip():
        print(colored("CAPTACHA détecté, impossible de récupérer les données. Action manuelle sur le site nécessaire.", 'red'))
        exit(0)

    # On récupère les lignes du deuxième tableau de la page
    rows = page.find_all('div', class_='bbTable')[1].find_all('tr')

    rows = [row.find_all('td') for row in rows[1:]]

    print(f"{len(rows)} batteries détectées, récupération des données...\n")

    i = 1;
    for cells in rows:
        number = colored(f"[{i}/{len(rows)}]", "blue")
        dots = "." * (i%4) + " " * (3 - i%4)
        print(f"Récupération des batteries {number}{dots}", end="\r")

        # On rempli les données
        data['brand'].append(cells[0].text.strip())
        data['model'].append(cells[1].text.strip())
        data['type'].append(cells[2].text.strip())
        data['colour_1'].append(cells[3].text.strip())
        data['colour_2'].append(cells[4].text.strip())
        img = cells[5].find('img')
        data['img_1_url'].append([img['src'] if img else ''][0])
        link = cells[6].find('a')["href"]

        
        # On récupère les infos complémentaires
        get_specific_data(data, link)

        i += 1

    print(f"Récupération des batteries {colored(f'[{len(rows)}/{len(rows)}]', 'blue')}... {colored('OK', 'green')}")


# Récupère les données spécifiques à une batterie
def get_specific_data(data, url):

    # Si il n'y a pas de lien, on ne peut pas récupérer les infos complémentaires
    if not url:
        data['capacity'].append('')
        data['voltage'].append('')
        data['charging'].append('')
        data['discharging'].append('')
        data['description'].append('')
        data['img_2_url'].append('')
        data['img_3_url'].append('')
        data['forum_link'].append('')
        data['spreadsheet_link'].append('')
        return
    
    data['forum_link'].append(url)

    page = get_page(url)
    if not page:
        return

    # On récupère les lignes du premier tableau de la page
    rows = page.find('table', class_='celldata').find_all('tr')

    # On récupère les infos complémentaires
    for cells in [row.find_all('td') for row in rows[1:]]:

        category = cells[0].text.strip()
        text = cells[1].get_text(separator=" ").strip()    
        if "---" in text:
            text = ""

        if category == 'Capacity:':
            data['capacity'].append(text)
        elif category == 'Voltage:':
            data['voltage'].append(text)
        elif category == 'Charging:':
            data['charging'].append(text)
        elif category == 'Discharging:':
            data['discharging'].append(text)
        elif category == 'Description:':
            data['description'].append(text)

    # on cherche le lien vers le spreadsheet
    spreadsheed_link = page.find('div', class_='bbWrapper').find('a')
    if spreadsheed_link and "None" not in spreadsheed_link.text.strip():
        data['spreadsheet_link'].append(spreadsheed_link['href'])
    else:
        data['spreadsheet_link'].append('')

    # on cherche les images 2 et 3
    # dans le div class="bbWrapper", balise img
    imgs = page.find('div', class_='bbWrapper').find_all('img')
    data['img_2_url'].append([imgs[1]['src'] if len(imgs) >1 else ''][0])
    data['img_3_url'].append([imgs[2]['src'] if len(imgs) >2 else ''][0])


# Exporte les données au format CSV
def export_data(data):
    df = pd.DataFrame(data)

    df.to_csv('resultats.csv', index=False, sep=';')

    print(f"\nLes données extraites sont stockées dans le fichier {OUTPUT_FILE}.")


if __name__ == "__main__":
    print("Lancement du scrapping...\n")

    # On défini les datas qu'on va récupérer
    data = {
        'brand': [],
        'model': [],
        'type': [],
        'colour_1': [],
        'colour_2': [],
        'capacity': [],
        'voltage': [],
        'charging': [],
        'discharging': [],
        'description': [],
        'img_1_url': [],
        'img_2_url': [],
        'img_3_url': [],
        'forum_link': [],
        'spreadsheet_link': [],
    }

    # On récupère les données
    get_data(data)

    # On exporte les données
    export_data(data)

    print("")
    print("Scrapping terminé !")