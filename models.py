from pydantic import BaseModel
from typing import List

class SelecionarAssentos(BaseModel):
    trip_id: str
    user_id: str
    seats: List[str]

class ConfirmarPagamento(BaseModel):
    order_id: str
    trip_id: str

class CancelarPagamento(BaseModel):
    order_id: str
    trip_id: str