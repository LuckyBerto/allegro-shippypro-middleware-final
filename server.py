from flask import Flask, request, jsonify
import json
from allegro_update import aggiorna_ordine_allegro

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return "Webhook server attivo!", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json

        print("\n===== WEBHOOK RICEVUTO DA SHIPPYPRO =====")
        print(json.dumps(data, indent=4, ensure_ascii=False))
        print("==========================================")

        # FILTRO SOLO ordini provenienti da Allegro
        marketplace = data.get("MarketplacePlatform")
        if marketplace != "Allegro":
            print(f"[IGNORO] Webhook non Allegro → {marketplace}")
            return jsonify({"ignored": True}), 200

        # Recupero dati fondamentali
        event = data.get("Event")
        order_id = data.get("OrderID")              # ID dell’ordine Allegro
        tracking = data.get("tracking")             # tracking number
        carrier = data.get("TrackingCarrier")       # corriere

        if not order_id:
            print("ERRORE: OrderID mancante nel webhook")
            return jsonify({"error": "OrderID mancante"}), 400

        # Decidiamo quando aggiornare Allegro
        # ShippyPro NON invia "OrderShipped".
        # Invia TRACKING_UPDATE con "code" e "message" vari.
        # Se ha un tracking, lo consideriamo 'spedito'.

        if event == "TRACKING_UPDATE" and tracking:
            print(f"[OK] Aggiornamento spedizione Allegro → {order_id}")
            print(f"     Tracking: {tracking}, Corriere: {carrier}")

            # Aggiorna Allegro
            resp = aggiorna_ordine_allegro(order_id, carrier, tracking)

            print("Risposta Allegro:", resp)

            return jsonify({
                "ok": True,
                "updated": True,
                "order_id": order_id,
                "tracking": tracking,
                "carrier": carrier
            }), 200

        # Ignoro altri eventi
        print(f"[IGNORO] Evento non rilevante: {event}")
        return jsonify({"ok": True, "ignored": True}), 200

    except Exception as e:
        print("ERRORE WEBHOOK:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
