from fastapi import FastAPI
import firebase_service as fb
from models import SelectSeatsRequest, ConfirmPaymentRequest, CancelOrderRequest

app = FastAPI()

@app.get("/trips/{trip_id}/{date}/seats")
def seats(trip_id: str, date: str):
    return fb.get_trip_seats(trip_id, date)

@app.post("/reserve")
def reserve(data: SelectSeatsRequest):
    return fb.reserve_seats(data.trip_id, data.date, data.user_id, data.seats)

@app.post("/confirm")
def confirm(data: ConfirmPaymentRequest):
    return fb.confirm_payment(data.order_id, data.trip_id, data.date)

@app.post("/cancel")
def cancel(data: CancelOrderRequest):
    return fb.cancel_order(data.order_id, data.trip_id, data.date)