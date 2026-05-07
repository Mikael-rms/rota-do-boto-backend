
from firebase_config import db
from datetime import datetime, timedelta

# todos os barcos
lanchas = ["lancha1", "lancha2", "lancha3", "lancha4"]

# maio 2026
start_date = datetime(2026, 5, 1)
end_date = datetime(2026, 5, 31)

current = start_date

while current <= end_date:

    date_str = current.strftime("%Y-%m-%d")

    print(f"Creating {date_str}")

    for lancha in lanchas:

        
        # cria as viagens
     

        seats = {}

        for i in range(1, 41):
            seats[f"S{i}"] = "available"

        db.collection("trips") \
            .document(lancha) \
            .collection(date_str) \
            .document("data") \
            .set({
                "seats": seats
            })

       
        # cria os pedidos
        

        db.collection("orders") \
            .document(lancha) \
            .collection(date_str) \
            .document("init") \
            .set({
                "created": True
            })

    current += timedelta(days=1)

print("DONE")

