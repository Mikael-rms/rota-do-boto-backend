from fastapi import FastAPI
from pydantic import BaseModel
from src.config.firebase import db

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
    trip_ref = db.collection("trips").document(data.tripId)
    trip = trip_ref.get()

    if not trip.exists:
        return {"error": "Trip não encontrada"}

    trip_data = trip.to_dict()
    occupied = trip_data.get("occupiedSeats", [])

    # 🔥 validar conflito
    for seat in data.seats:
        if seat in occupied:
            return {"error": f"Assento {seat} já ocupado"}

    # 🔥 atualizar assentos
    new_occupied = occupied + data.seats
    trip_ref.update({
        "occupiedSeats": new_occupied
    })

    # 🔥 criar pedido
    db.collection("orders").add({
        "userId": data.userId,
        "tripId": data.tripId,
        "seats": data.seats,
        "total": data.total,
        "status": "confirmado",
        "origem": data.origem,
        "destino": data.destino
    })

    return {"success": True}