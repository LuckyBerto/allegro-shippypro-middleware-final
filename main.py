import json
from allegro import richiesta_ordini
from shippypro import invio_ordine_shippy
from fulfillment import update_allegro_tracking


def sync_orders():
    print("Recupero ordini da Allegro...")

    orders = richiesta_ordini()

    if not orders:
        print("Nessun ordine da sincronizzare.")
        return

    print(f"Ordini trovati: {len(orders)}")

    for order in orders:

        order_id = order["id"]
        print(f"\n--- ANALISI ORDINE {order_id} ---")

        # Stato API Allegro
        api_status = order.get("status")
        if api_status != "READY_FOR_PROCESSING":
            print("Ignoro: ordine non è nello stato READY FOR PROCESSING")
            continue

        # Cancellazioni
        if order.get("summary", {}).get("status") == "CANCELLED":
            print("Ignoro: ordine cancellato")
            continue

        # Articoli cancellati
        for item in order.get("lineItems", []):
            if item.get("status") == "CANCELLED":
                print("Ignoro: articolo cancellato")
                continue

        # Pagamento
        if not order.get("payment", {}).get("finishedAt"):
            print("Ignoro: NON pagato")
            continue

        print("Ordine valido → invio a ShippyPro")

        result = invio_ordine_shippy(order)
        print("Risposta ShippyPro:", result)


        # Se c'è tracking aggiorna Allegro
        if result.get("tracking_number") and result.get("carrier"):
            update_allegro_tracking(order_id, result["carrier"], result["tracking_number"])

    print("Fine sincronizzazione")
        

if __name__ == "__main__":
    sync_orders()
