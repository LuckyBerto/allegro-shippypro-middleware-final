import requests
import json
from allegro import refresh_access_token


def aggiorna_ordine_allegro(order_id, carrier, tracking):

    token = refresh_access_token()

    url = f"https://api.allegro.pl/order/checkout-forms/{order_id}/shipments"

    payload = {
        "carrierId": carrier,
        "waybill": tracking
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.allegro.public.v1+json",
        "Content-Type": "application/json"
    }

    r = requests.post(url, json=payload, headers=headers)

    try:
        return r.json()
    except:
        return {"raw": r.text}
