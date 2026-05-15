from src.firebase_config import db
#cria as lanchas na database
def create_seats():
    seats = {}

    for i in range(1, 41):
        seat_id = f"S{i}"
        seats[seat_id] = "available"

    db.collection("trips").document("lancha1").set({
        "seats": seats
    })

    

if __name__ == "__main__":
    create_seats()