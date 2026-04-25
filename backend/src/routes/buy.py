from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.config.firebase import db
import firebase_admin
from firebase_admin import firestore

app = FastAPI()

class BuyRequest(BaseModel):
    userId: str
    tripId: str
    seats: list[int]
    total: float
    origem: str
    destino: str


@app.post("/buy")
def buy(data: BuyRequest):
    transaction = db.transaction()
    trip_ref = db.collection("trips").document(data.tripId)

    @firestore.transactional
    def run_transaction(transaction, trip_ref):
        snapshot = trip_ref.get(transaction=transaction)

        if not snapshot.exists:
            raise HTTPException(status_code=404, detail="Trip não encontrada")

        trip_data = snapshot.to_dict()
        occupied = trip_data.get("occupiedSeats", [])

        # 🔥 valida conflito
        for seat in data.seats:
            if seat in occupied:
                raise HTTPException(
                    status_code=400,
                    detail=f"Assento {seat} já está ocupado"
                )

        # 🔥 atualiza assentos
        new_occupied = occupied + data.seats

        transaction.update(trip_ref, {
            "occupiedSeats": new_occupied
        })

        # 🔥 cria pedido
        order_ref = db.collection("orders").document()

        transaction.set(order_ref, {
            "userId": data.userId,
            "tripId": data.tripId,
            "seats": data.seats,
            "total": data.total,
            "status": "confirmado",
            "origem": data.origem,
            "destino": data.destino
        })

    run_transaction(transaction, trip_ref)

    return {"success": True}