from firebase_config import db
import time
import threading
# ----------------------------
# coletar assentos
# ----------------------------
def get_trip_seats(trip_id):
    doc = db.collection("trips").document(trip_id).get()

    if not doc.exists:
        return {"error": "VIAGEM NAO ENCONTRADA"}

    data = doc.to_dict() or {}
    return data.get("seats", {})

#Ordem de cancelamento automatico
def auto_cancel_order(order_id, trip_id, delay=20):
    def task():
        print(f"[AUTO] Started timer for {order_id}")

        time.sleep(delay)

        print(f"[AUTO] Checking order {order_id}")

        try:
            order_ref = db.collection("orders") \
                .document(trip_id) \
                .collection("pedidos") \
                .document(order_id)

            order = order_ref.get()

            if not order.exists:
                print("[AUTO] Order not found")
                return

            data = order.to_dict()

            print(f"[AUTO] Status: {data.get('status')}")

            if data.get("status") == "paid":
                print("[AUTO] Already paid, skipping")
                return

            seats = data.get("seats", [])

            order_ref.update({"status": "cancelled"})

            trip_ref = db.collection("trips").document(trip_id)
            trip = trip_ref.get().to_dict()

            seats_data = trip.get("seats", {})

            for seat in seats:
                seats_data[seat] = "available"

            trip_ref.update({"seats": seats_data})

            print(f"[AUTO] Order {order_id} cancelled successfully")

        except Exception as e:
            print("[AUTO ERROR]", e)

    threading.Thread(target=task).start()


# ----------------------------
# RESERVAR ASSENTOS
# ----------------------------
def reserve_seats(trip_id, user_id, seats):
    ref = db.collection("trips").document(trip_id)
    doc = ref.get()

    if not doc.exists:
        return {"error": "viagem nao encontrada"}

    data = doc.to_dict() or {}
    current_seats = data.get("seats", {})

    # VALIDAR ASSENTOS
    for seat in seats:
        if seat not in current_seats:
            return {"error": f"{seat} nao existe"}
        if current_seats[seat] != "available":
            return {"erro": f"{seat} nao esta disponivel"}

    # reservar assentos
    for seat in seats:
        current_seats[seat] = "reserved"

    ref.update({"seats": current_seats})

    # criar ordem (CORRECT INDENT)
    orders_ref = db.collection("orders").document(trip_id).collection("pedidos")

    order_ref = orders_ref.document()
    order_id = order_ref.id

    order_ref.set({
        "trip_id": trip_id,
        "user_id": user_id,
        "seats": seats,
        "status": "reserved",
        "total": len(seats),
        "created_at": time.time()
    })

    auto_cancel_order(order_id, trip_id)

    return order_id


# ----------------------------
# CONFIRMAR PAGAMENTO
# ----------------------------
def confirm_payment(order_id, trip_id):
    order_ref = db.collection("orders") \
        .document(trip_id) \
        .collection("pedidos") \
        .document(order_id)

    order = order_ref.get()

    if not order.exists:
        return {"error": "PEDIDO NAO ENCONTRADO"}

    data = order.to_dict()
    seats = data["seats"]

    order_ref.update({"status": "PAGO"})

    trip_ref = db.collection("trips").document(trip_id)
    trip = trip_ref.get().to_dict()

    seats_data = trip.get("seats", {})

    for seat in seats:
        seats_data[seat] = "unavailable"

    trip_ref.update({"seats": seats_data})

    return {"message": "PAGAMENTO CONFIRMADO"}


# ----------------------------
# CANCELAR PEDIDO
# ----------------------------
def cancel_order(order_id, trip_id):
    order_ref = db.collection("orders") \
        .document(trip_id) \
        .collection("pedidos") \
        .document(order_id)

    order = order_ref.get()

    if not order.exists:
        return {"error": "PEDIDO NAO ENCONTRADO"}

    data = order.to_dict()
    seats = data["seats"]

    order_ref.update({"status": "CANCELADO"})

    trip_ref = db.collection("trips").document(trip_id)
    trip = trip_ref.get().to_dict()

    seats_data = trip.get("seats", {})

    for seat in seats:
        seats_data[seat] = "available"

    trip_ref.update({"seats": seats_data})

    return {"message": "CANCELADO"}