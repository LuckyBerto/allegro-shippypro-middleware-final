import json
import requests


# config/tokens
def carica_config():
    with open("config.json", "r") as f:
        return json.load(f)

def carica_tokens():
    with open("tokens.json", "r") as f:
        return json.load(f)

def salva_tokens(tokens):
    with open("tokens.json", "w") as f:
        json.dump(tokens, f, indent=4)


# refresh token
def refresh_access_token():
    config = carica_config()
    tokens = carica_tokens()

    url = "https://allegro.pl/auth/oauth/token"

    data = {
        "grant_type": "refresh_token",
        "refresh_token": tokens["refresh_token"]
    }

    r = requests.post(url, data=data, auth=(config["CLIENT_ID"], config["CLIENT_SECRET"]))
    tokens_new = r.json()

    tokens["access_token"] = tokens_new["access_token"]
    tokens["refresh_token"] = tokens_new["refresh_token"]
    salva_tokens(tokens)

    return tokens["access_token"]


# richiesta ordini
def richiesta_ordini():
    access_token = refresh_access_token()

    # Ultimi 10 ordini NEW + pagati
    url = "https://api.allegro.pl/order/checkout-forms?fulfillment.status=NEW&limit=10&offset=0"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.allegro.public.v1+json"
    }

    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print("ERRORE ALLEGRO:", r.text)
        return []

    data = r.json()

    # DEBUG
    print("\n======= DEBUG ORDINI NEW + PAGATI (ULTIMI 10) =======")
    for o in data.get("checkoutForms", []):
        print(
            f"ID: {o['id']} | status: {o.get('status')} | "
            f"fulfillment: {o.get('fulfillment', {}).get('status')} | "
            f"amount: {o.get('summary', {}).get('totalToPay', {}).get('amount')}"
        )
    print("====================================================\n")

    return data.get("checkoutForms", [])


# prova scraping immagini
from bs4 import BeautifulSoup
import requests

def recupera_immagine_scraping_bs(offer_id):
    url = f"https://allegro.pl/oferta/{offer_id}"
    print(f"[SCRAPING] Recupero immagine (BeautifulSoup) per {offer_id}")

    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            print("[SCRAPING] HTTP ERROR:", r.status_code)
            return None

        # Analizza l'HTML
        soup = BeautifulSoup(r.text, 'html.parser')

        # Tenta di trovare l'immagine principale
        # (Spesso l'immagine principale ha un tag <img> specifico)

        # Cerca il tag <img> con un src che inizia con allegroimg.com 
        # (Il selettore CSS preciso può cambiare nel tempo!)
        img_tag = soup.find('img', src=re.compile(r'https://a\.allegroimg\.com/'))

        if img_tag and img_tag.get('src'):
            img = img_tag.get('src')
            print(f"[SCRAPING] Immagine trovata: {img}")
            return img

        # Se la prima ricerca fallisce, potresti provare a cercare 
        # i dati JSON nascosti nella pagina che contengono le URL

        print("[SCRAPING] Nessuna immagine trovata con selettori semplici.")
        return None

    except Exception as e:
        print("[SCRAPING] Errore:", e)
        return None