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

        # filtra SOLO ordini allegro
        platform = data.get("PlatformName")
        if platform != "Allegro":
            print(f"[IGNORO] Webhook non Allegro → {platform}")
            return jsonify({"ignored": True}), 200

        # estrazione campi
        event = data.get("Event")
        order_id = data.get("OrderID")
        tracking = data.get("TrackingNumber") or data.get("tracking")
        carrier = data.get("CarrierName") or data.get("TrackingCarrier")

        if not order_id:
            print("ERRORE: OrderID mancante nel webhook")
            return jsonify({"error": "OrderID mancante"}), 400

        # aggiorna Allegro SOLO quando esiste un tracking valido
        if event == "TRACKING_UPDATE" and tracking:
            print(f"[OK] Webhook valido per Allegro → ordine {order_id}")
            print(f"     Tracking: {tracking}, Corriere: {carrier}")
            print("     Invio aggiornamento tracking ad Allegro...")

            resp = aggiorna_ordine_allegro(order_id, carrier, tracking)

            print("\n===== RISPOSTA API ALLEGRO =====")
            print(json.dumps(resp, indent=4, ensure_ascii=False))
            print("================================")

            # LOG SPECIFICO PER IL TRACKING
            if isinstance(resp, dict) and ("error" not in resp):
                print(f"[SUCCESSO] Tracking aggiornato su Allegro per ordine {order_id}")
                print(f"           ({carrier} - {tracking})\n")
            else:
                print(f"[ERRORE] Allegro NON ha accettato il tracking per ordine {order_id}")
                print("Possibili cause: ordine ancora NEW o stato non compatibile\n")

            return jsonify({
                "ok": True,
                "updated": True,
                "order_id": order_id,
                "tracking": tracking,
                "carrier": carrier
            }), 200

        # ignoro il resto
        print(f"[IGNORO] Evento non rilevante: {event}")
        return jsonify({"ok": True, "ignored": True}), 200

    except Exception as e:
        print("ERRORE WEBHOOK:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
