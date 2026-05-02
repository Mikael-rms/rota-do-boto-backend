from firebase_config import db

def create_seats():
    seats = {}

    for i in range(1, 41):
        seat_id = f"S{i}"
        seats[seat_id] = "available"

    db.collection("trips").document("lancha1").set({
        "seats": seats
    })

    print("trip1 created with seats S1–S40")

if __name__ == "__main__":
    create_seats()