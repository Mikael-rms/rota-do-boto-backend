from pydantic import BaseModel
from typing import List

class SelectSeatsRequest(BaseModel):
    trip_id: str
    date: str
    user_id: str
    seats: List[str]

class ConfirmPaymentRequest(BaseModel):
    order_id: str
    trip_id: str
    date: str

class CancelOrderRequest(BaseModel):
    order_id: str
    trip_id: str
    date: str