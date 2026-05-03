from config.firebase import db
from fastapi import FastAPI
from models import *
import firebase_service as fb

app = FastAPI()

@app.get("/trips/{trip_id}/seats")
def seats(trip_id: str):
    return fb.get_trip_seats(trip_id)

@app.post("/reserve")
def reserve(data: SelecionarAssentos):
    order_id = fb.reserve_seats(data.trip_id, data.user_id, data.seats)
    return {"order_id": order_id}

@app.post("/confirm")
def confirm(data: ConfirmarPagamento):
    fb.confirm_payment(data.order_id, data.trip_id)
    return {"message": "pago"}

@app.post("/cancel")
def cancel(data: CancelarPagamento):
    fb.cancel_order(data.order_id, data.trip_id)
    return {"message": "cancelado"}