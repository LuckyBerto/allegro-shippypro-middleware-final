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
        print(json.dumps(data, indent=4))
        print("==========================================")

        event = data.get("Event", "")
        order_id = data.get("OrderID")
        tracking = data.get("TrackingNumber")
        carrier = data.get("Courier")

        if not order_id:
            return jsonify({"error": "OrderID mancante"}), 400

        # EVENTO: ordine spedito
        if event == "OrderShipped" and tracking and carrier:
            print(f"Aggiorno Allegro → Ordine {order_id}, tracking {tracking}")
            resp = aggiorna_ordine_allegro(order_id, carrier, tracking)
            return jsonify({"ok": True, "allegro_response": resp}), 200

        # EVENTO: altri aggiornamenti
        return jsonify({"ok": True, "msg": "Evento ignorato"}), 200

    except Exception as e:
        print("ERRORE WEBHOOK:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
