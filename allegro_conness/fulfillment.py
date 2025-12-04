import json
import requests
from allegro import refresh_access_token, carica_config

#aggiorno tracking allegro
def update_allegro_tracking(order_id, carrier_code, tracking_number):
    """
    Aggiorna l'ordine Allegro con tracking e corriere.
    """

    access_token = refresh_access_token()
    config = carica_config()

    url = f"https://api.allegro.pl/order/checkout-forms/{order_id}/shipments"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.allegro.public.v1+json",
        "Content-Type": "application/vnd.allegro.public.v1+json"
    }

    body = {
        "carrierId": carrier_code,
        "waybill": tracking_number
    }

    resp = requests.post(url, json=body, headers=headers)

    try:
        return resp.json()
    except:
        return {"error": resp.text}
