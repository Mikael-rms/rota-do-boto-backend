from config.firebase import db

def init_orders():
    lanchas = ["lancha1", "lancha2", "lancha3", "lancha4"]

    for lancha in lanchas:
        db.collection("orders").document(lancha).set({
            "created": True
        })

    print("Orders structure created!")

if __name__ == "__main__":
    init_orders()