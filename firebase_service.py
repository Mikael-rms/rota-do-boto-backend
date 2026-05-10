from google.cloud import firestore
import time
import uuid
import threading
import traceback
from firebase_config import db


def _trip_ref(trip_id: str, date: str):
    # trips/{lancha}/{date}/data
    return db.collection("trips").document(trip_id).collection(date).document("data")


def _order_ref(trip_id: str, date: str, order_id: str):
    # orders/{lancha}/{date}/{order_id}
    return db.collection("orders").document(trip_id).collection(date).document(order_id)


def get_trip_seats(trip_id: str, date: str):
    try:
        doc = _trip_ref(trip_id, date).get()
        if not doc.exists:
            return {"error": "Trip/date not found"}

        data = doc.to_dict() or {}
        seats = data.get("seats", {})
        if not isinstance(seats, dict):
            return {"error": "Invalid trips format: expected data.seats dict"}

        return seats
    except Exception as e:
        return {"error": f"get_trip_seats failed: {e}"}


def reserve_seats(
    trip_id: str,
    date: str,
    user_id: str,
    seats: list[str],
    auto_cancel_seconds: int = 180
):
    try:
        trip_ref = _trip_ref(trip_id, date)

        transaction = db.transaction()

        @firestore.transactional
        def reserve_in_transaction(transaction, trip_ref):

            trip_doc = trip_ref.get(transaction=transaction)

            if not trip_doc.exists:
                return {"error": "Trip/date not found"}

            trip_data = trip_doc.to_dict() or {}

            seats_data = trip_data.get("seats", {})

            if not isinstance(seats_data, dict):
                return {
                    "error": "Invalid trips format"
                }

            # verifica disponibilidade
            for s in seats:
                status = seats_data.get(s)

                if status != "available":
                    return {
                        "error": f"{s} not available (status={status})"
                    }

            # reserva
            for s in seats:
                seats_data[s] = "reserved"

            transaction.update(trip_ref, {
                "seats": seats_data
            })

            return {"success": True}

        result = reserve_in_transaction(
            transaction,
            trip_ref
        )

        if result.get("error"):
            return result

        # cria pedido
        order_id = str(uuid.uuid4())

        order_ref = _order_ref(
            trip_id,
            date,
            order_id
        )

        created_at = time.time()

        expires_at = created_at + auto_cancel_seconds

        order_ref.set({
            "order_id": order_id,
            "trip_id": trip_id,
            "date": date,
            "user_id": user_id,
            "seats": seats,
            "status": "pending",
            "created_at": created_at,
            "expires_at": expires_at,
        })

        # thread auto cancel
        t = threading.Thread(
            target=auto_cancel_order,
            args=(
                order_id,
                trip_id,
                date,
                auto_cancel_seconds
            ),
            daemon=True
        )

        t.start()

        return {
            "message": "Reservation created",
            "order_id": order_id,
            "expires_at": expires_at
        }

    except Exception as e:
        traceback.print_exc()

        return {
            "error": f"reserve_seats failed: {e}"
        }
    try:
        trip_ref = _trip_ref(trip_id, date)
        trip_doc = trip_ref.get()

        if not trip_doc.exists:
            return {"error": "Trip/date not found"}

        trip_data = trip_doc.to_dict() or {}
        seats_data = trip_data.get("seats", {})
        if not isinstance(seats_data, dict):
            return {"error": "Invalid trips format: expected data.seats dict"}

        # valida assentos
        for s in seats:
            status = seats_data.get(s)
            if status != "available":
                return {"error": f"{s} not available (status={status})"}

        # reserva assentos
        for s in seats:
            seats_data[s] = "reserved"

        # update only seats field
        trip_ref.update({"seats": seats_data})

        # cria pedido
        order_id = str(uuid.uuid4())
        order_ref = _order_ref(trip_id, date, order_id)
        order_ref.set({
            "order_id": order_id,
            "trip_id": trip_id,
            "date": date,
            "user_id": user_id,
            "seats": seats,
            "status": "pending",
            "created_at": time.time(),
        })

        # auto cancelamento threading
        t = threading.Thread(
            target=auto_cancel_order,
            args=(order_id, trip_id, date, auto_cancel_seconds),
            daemon=True
        )
        t.start()

        expires_at = time.time() + auto_cancel_seconds

        return {
            "message": "Reservation created",
            "order_id": order_id,
            "expires_at": expires_at
        }

    except Exception as e:
        # this prevents silent 500s
        traceback.print_exc()
        return {"error": f"reserve_seats failed: {e}"}


def confirm_payment(order_id: str, trip_id: str, date: str):
    try:
        order_ref = _order_ref(trip_id, date, order_id)
        order_doc = order_ref.get()
        if not order_doc.exists:
            return {"error": "Order not found"}

        order_data = order_doc.to_dict() or {}
        if order_data.get("status") == "paid":
            return {"message": "Already paid"}

        seats = order_data.get("seats", [])

        # marca como pago
        order_ref.update({"status": "paid", "paid_at": time.time()})

        # marca como pago
        trip_ref = _trip_ref(trip_id, date)
        trip_doc = trip_ref.get()
        if not trip_doc.exists:
            return {"error": "Trip/date not found"}

        trip_data = trip_doc.to_dict() or {}
        seats_data = trip_data.get("seats", {})
        if not isinstance(seats_data, dict):
            return {"error": "Invalid trips format: expected data.seats dict"}

        for s in seats:
            seats_data[s] = "paid"   # or "unavailable" if you prefer

        trip_ref.update({"seats": seats_data})

        return {"message": "Payment confirmed"}
    except Exception as e:
        traceback.print_exc()
        return {"error": f"confirm_payment failed: {e}"}


def cancel_order(order_id: str, trip_id: str, date: str):
    try:
        order_ref = _order_ref(trip_id, date, order_id)
        order_doc = order_ref.get()
        if not order_doc.exists:
            return {"error": "Order not found"}

        order_data = order_doc.to_dict() or {}
        status = order_data.get("status")

        if status == "paid":
            return {"error": "Cannot cancel a paid order"}

        seats = order_data.get("seats", [])

        # assentos livres
        trip_ref = _trip_ref(trip_id, date)
        trip_doc = trip_ref.get()
        if not trip_doc.exists:
            return {"error": "Trip/date not found"}

        trip_data = trip_doc.to_dict() or {}
        seats_data = trip_data.get("seats", {})
        if not isinstance(seats_data, dict):
            return {"error": "Invalid trips format: expected data.seats dict"}

        for s in seats:
            seats_data[s] = "available"

        trip_ref.update({"seats": seats_data})

        # cancelar pedido(historico)
        order_ref.update({"status": "cancelled", "cancelled_at": time.time()})

        return {"message": "Order cancelled"}
    except Exception as e:
        traceback.print_exc()
        return {"error": f"cancel_order failed: {e}"}


def auto_cancel_order(order_id: str, trip_id: str, date: str, delay: int = 180):
    try:
        time.sleep(delay)

        order_ref = _order_ref(trip_id, date, order_id)
        order_doc = order_ref.get()
        if not order_doc.exists:
            print("[AUTO] Order not found:", order_id)
            return

        order_data = order_doc.to_dict() or {}
        if order_data.get("status") != "pending":
            print("[AUTO] Not pending anymore:", order_id, "status=", order_data.get("status"))
            return

        # cancelar manualmente
        result = cancel_order(order_id, trip_id, date)
        print("[AUTO] Auto-cancel result:", order_id, result)

    except Exception:
        print("[AUTO ERROR] crashed:")
        traceback.print_exc()