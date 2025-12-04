import json
import requests
import base64
import time
from allegro import carica_config, recupera_immagine_scraping_bs

config = carica_config()


# auth
def shippypro_auth_header(api_key):
    raw = f"{api_key}:".encode("utf-8")
    encoded = base64.b64encode(raw).decode("utf-8")
    return f"Basic {encoded}"


# formattazione ordine
def formato_shippy(order):

    buyer = order["buyer"]
    address = order["delivery"]["address"]
    summary = order["summary"]
    delivery_cost = order["delivery"]["cost"]
    items = order["lineItems"]

    total_amount = float(summary["totalToPay"]["amount"])
    shipping_cost = float(delivery_cost["amount"])
    items_count = sum(item["quantity"] for item in items)

    ts = int(time.time())

    enriched_items = []

    print("\n[DEBUG] IMMAGINI ITEMS PER SHIPPYPRO:")

    for item in items:
        offer = item["offer"]
        offer_id = offer["id"]

        # scraping img
        img_url = recupera_immagine_scraping_bs(offer_id)

        print(f"  SKU: {offer_id} → img: {img_url}")

        enriched_items.append({
            "sku": offer_id,
            "title": offer["name"],
            "description": offer["name"],
            "quantity": item["quantity"],
            "price": float(item["price"]["amount"]),
            "imageurl": img_url or ""
        })

    data = {
        "Method": "PutOrder",
        "APIKey": config["SHIPPYPRO_API_KEY"],

        "Params": {
            "APIOrdersID": int(config["SHIPPYPRO_API_ORDERS_ID"]),
            "OrderID": order["id"],
            "TransactionID": order["id"],
            "Date": ts,
            "Currency": summary["totalToPay"]["currency"],
            "Total": total_amount,
            "ShipmentAmountPaid": shipping_cost,

            "to_address": {
                "name": f"{buyer['firstName']} {buyer['lastName']}",
                "company": "",
                "street1": address["street"],
                "street2": "",
                "city": address["city"],
                "state": "",
                "zip": address["zipCode"],
                "country": address["countryCode"],
                "phone": buyer["phoneNumber"],
                "email": buyer["email"]
            },

            "parcels": [
                {"weight": 1, "width": 10, "height": 10, "length": 10}
            ],

            "items": enriched_items,
            "ItemsCount": items_count,
            "ContentDescription": "Order from Allegro",
            "Status": "ToShip",
            "Incoterm": "DAP",
            "BillAccountNumber": "",
            "PaymentMethod": "Paid",
            "ShippingService": order["delivery"]["method"]["name"],
            "Note": ""
        }
    }

    return data


# invio a shippypro
def invio_ordine_shippy(order):

    url = "https://www.shippypro.com/api/PutOrder"
    payload = formato_shippy(order)

    headers = {
        "Authorization": shippypro_auth_header(config["SHIPPYPRO_API_KEY"]),
        "Content-Type": "application/json"
    }

    print("\n========= PAYLOAD INVIATO A SHIPPYPRO =========")
    print(json.dumps(payload, indent=4, ensure_ascii=False))
    print("================================================\n")

    response = requests.post(url, json=payload, headers=headers, timeout=15)

    try:
        data = response.json()
    except:
        return {"error": "Invalid JSON", "raw": response.text}

    return {
        "raw": data,
        "tracking_number": data.get("TrackingNumber"),
        "carrier": data.get("CourierName")
    }
