from firebase_config import db
# ----------------------------
# GET SEATS
# ----------------------------
def get_trip_seats(trip_id):
    doc = db.collection("trips").document(trip_id).get()

    if not doc.exists:
        return {"error": "Trip not found"}

    data = doc.to_dict() or {}
    return data.get("seats", {})


# ----------------------------
# RESERVE SEATS
# ----------------------------
def reserve_seats(trip_id, user_id, seats):
    ref = db.collection("trips").document(trip_id)
    doc = ref.get()

    if not doc.exists:
        return {"error": "Trip not found"}

    data = doc.to_dict() or {}
    current_seats = data.get("seats", {})

    # validate seats
    for seat in seats:
        if seat not in current_seats:
            return {"error": f"{seat} does not exist"}
        if current_seats[seat] != "available":
            return {"error": f"{seat} not available"}

    # reserve seats
    for seat in seats:
        current_seats[seat] = "reserved"

    ref.update({"seats": current_seats})

    # create order (CORRECT INDENT)
    orders_ref = db.collection("orders").document(trip_id).collection("pedidos")

    order_ref = orders_ref.document()
    order_id = order_ref.id

    order_ref.set({
        "trip_id": trip_id,
        "user_id": user_id,
        "seats": seats,
        "status": "reserved",
        "total": len(seats)
    })

    return order_id


# ----------------------------
# CONFIRM PAYMENT
# ----------------------------
def confirm_payment(order_id, trip_id):
    order_ref = db.collection("orders") \
        .document(trip_id) \
        .collection("pedidos") \
        .document(order_id)

    order = order_ref.get()

    if not order.exists:
        return {"error": "Order not found"}

    data = order.to_dict()
    seats = data["seats"]

    order_ref.update({"status": "paid"})

    trip_ref = db.collection("trips").document(trip_id)
    trip = trip_ref.get().to_dict()

    seats_data = trip.get("seats", {})

    for seat in seats:
        seats_data[seat] = "unavailable"

    trip_ref.update({"seats": seats_data})

    return {"message": "payment confirmed"}


# ----------------------------
# CANCEL ORDER
# ----------------------------
def cancel_order(order_id, trip_id):
    order_ref = db.collection("orders") \
        .document(trip_id) \
        .collection("pedidos") \
        .document(order_id)

    order = order_ref.get()

    if not order.exists:
        return {"error": "Order not found"}

    data = order.to_dict()
    seats = data["seats"]

    order_ref.update({"status": "cancelled"})

    trip_ref = db.collection("trips").document(trip_id)
    trip = trip_ref.get().to_dict()

    seats_data = trip.get("seats", {})

    for seat in seats:
        seats_data[seat] = "available"

    trip_ref.update({"seats": seats_data})

    return {"message": "cancelled"}