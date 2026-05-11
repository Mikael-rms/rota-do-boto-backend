import time

from firebase_config import db
from firebase_service import cancel_order


def release_expired_orders():
    while True:
        try:
            now = int(time.time() * 1000)

            orders_ref = db.collection("orders")

            trips = orders_ref.stream()

            for trip_doc in trips:
                trip_id = trip_doc.id

                dates = (
                    orders_ref
                    .document(trip_id)
                    .collections()
                )

                for date_collection in dates:
                    date = date_collection.id

                    pending_orders = (
                        date_collection
                        .where("status", "==", "pending")
                        .stream()
                    )

                    for order_doc in pending_orders:
                        order = order_doc.to_dict()

                        expires_at = order.get(
                            "expires_at",
                            0
                        )

                        if now >= expires_at:
                            print(
                                f"Cancelando pedido expirado: {order['order_id']}"
                            )

                            cancel_order(
                                order["order_id"],
                                trip_id,
                                date
                            )

        except Exception as e:
            print("Expiration worker error:", e)

        time.sleep(30)