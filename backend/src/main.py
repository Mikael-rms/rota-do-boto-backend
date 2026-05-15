from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src import firebase_service as fb
from src.models import (
    SelectSeatsRequest,
    ConfirmPaymentRequest,
    CancelOrderRequest
)
import threading

from tasks.expiration_worker import (
    release_expired_orders
)
threading.Thread(
    target=release_expired_orders,
    daemon=True
).start()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/trips/{trip_id}/{date}/seats")
def seats(trip_id: str, date: str):
    return fb.get_trip_seats(trip_id, date)

@app.post("/reserve")
def reserve(data: SelectSeatsRequest):
    return fb.reserve_seats(
        data.trip_id,
        data.date,
        data.user_id,
        data.seats,
        data.price,
        data.origem,
        data.destino,
        data.nome,
        data.tempo,
    )
    

@app.post("/confirm")
def confirm(data: ConfirmPaymentRequest):
    return fb.confirm_payment(
        data.order_id,
        data.trip_id,
        data.date
    )

@app.post("/cancel")
def cancel(data: CancelOrderRequest):
    return fb.cancel_order(
        data.order_id,
        data.trip_id,
        data.date
    )

@app.get("/orders/{user_id}")
def get_orders(user_id: str):
    return fb.get_user_orders(user_id)