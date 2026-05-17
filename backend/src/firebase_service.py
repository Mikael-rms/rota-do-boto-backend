from google.cloud import firestore
import time
import uuid
import traceback
from src.firebase_config import db


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
            return {
                "error": "Invalid trips format: expected data.seats dict"
            }

        return seats

    except Exception as e:
        return {
            "error": f"get_trip_seats failed: {e}"
        }


def reserve_seats(
    trip_id: str,
    date: str,
    user_id: str,
    seats: list[str],
    price: float,
    origem: str,
    destino: str,
    nome: str,
    tempo: str = "",
    auto_cancel_seconds: int = 180
):
    try:
        trip_ref = _trip_ref(trip_id, date)

        # verifica se usuário já possui reserva pendente
        existing_orders = (
            db.collection("orders")
            .document(trip_id)
            .collection(date)
            .where("user_id", "==", user_id)
            .where("status", "==", "pending")
            .stream()
        )

        now = int(time.time() * 1000)

        for doc in existing_orders:
            order = doc.to_dict() or {}

            expires_at = order.get("expires_at", 0)

            # se ainda não expirou, impede nova reserva
            if now < expires_at:
                return {
                    "error": "User already has an active reservation"
                }

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

            # reserva assentos
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

        created_at = int(time.time() * 1000)

        expires_at = created_at + (180 * 1000)

        order_ref.set({
            "order_id": order_id,
            "trip_id": trip_id,
            "date": date,
            "user_id": user_id,
            "seats": seats,

            "price": price,
            "total": price * len(seats),
            "origem": origem,
            "destino": destino,
            "nome": nome,
            "tempo": tempo,

            "status": "pending",
            "created_at": created_at,
            "expires_at": expires_at,
        })

        return {
            "message": "Reservation created",
            "order_id": order_id,
            "expires_at": expires_at,
            "duration": auto_cancel_seconds
        }

    except Exception as e:
        traceback.print_exc()

        return {
            "error": f"reserve_seats failed: {e}"
        }

def confirm_payment(order_id: str, trip_id: str, date: str):
    try:
        order_ref = _order_ref(trip_id, date, order_id)

        order_doc = order_ref.get()

        if not order_doc.exists:
            return {"error": "Order not found"}

        order_data = order_doc.to_dict() or {}

        # bloqueia pedido cancelado/expirado
        status = order_data.get("status")

        if status == "paid":
            return {"error": "Cannot cancel a paid order"}

        if status == "cancelled":
            return {"message": "Order already cancelled"}

        # bloqueia pagamento após expiração
        expires_at = order_data.get("expires_at", 0)

        if int(time.time() * 1000) > expires_at:
            return {"error": "Order expired"}

        if order_data.get("status") == "paid":
            return {"message": "Already paid"}

        seats = order_data.get("seats", [])

        # marca pedido como pago
        order_ref.update({
            "status": "paid",
            "paid_at": time.time()
        })

        # marca assentos como pagos
        trip_ref = _trip_ref(trip_id, date)

        trip_doc = trip_ref.get()

        if not trip_doc.exists:
            return {"error": "Trip/date not found"}

        trip_data = trip_doc.to_dict() or {}

        seats_data = trip_data.get("seats", {})

        if not isinstance(seats_data, dict):
            return {
                "error": "Invalid trips format: expected data.seats dict"
            }

        for s in seats:
            seats_data[s] = "paid"

        trip_ref.update({
            "seats": seats_data
        })

        return {"message": "Payment confirmed"}

    except Exception as e:
        traceback.print_exc()

        return {
            "error": f"confirm_payment failed: {e}"
        }

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

        # libera assentos
        trip_ref = _trip_ref(trip_id, date)

        trip_doc = trip_ref.get()

        if not trip_doc.exists:
            return {"error": "Trip/date not found"}

        trip_data = trip_doc.to_dict() or {}

        seats_data = trip_data.get("seats", {})

        if not isinstance(seats_data, dict):
            return {
                "error": "Invalid trips format: expected data.seats dict"
            }

        for s in seats:
            seats_data[s] = "available"

        trip_ref.update({
            "seats": seats_data
        })

        # cancela pedido
        order_ref.update({
            "status": "cancelled",
            "cancelled_at": time.time()
        })

        return {"message": "Order cancelled"}

    except Exception as e:
        traceback.print_exc()

        return {
            "error": f"cancel_order failed: {e}"
        }

def get_user_orders(user_id: str):
    try:
        orders = []

        # list_documents() retorna todos os documentos incluindo os fantasmas
        trip_refs = db.collection("orders").list_documents()

        for trip_ref in trip_refs:
            date_collections = trip_ref.collections()

            for date_collection in date_collections:

                docs = (
                    date_collection
                    .where("user_id", "==", user_id)
                    .where("status", "==", "paid")
                    .stream()
                )

                for doc in docs:
                    data = doc.to_dict()

                    orders.append({
                        "id": doc.id,
                        **data
                    })

        orders.sort(
            key=lambda x: x.get("paid_at", 0),
            reverse=True
        )

        return orders

    except Exception as e:
        traceback.print_exc()

        return {
            "error": f"get_user_orders failed: {e}"
        }