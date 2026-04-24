import os
import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials, firestore

# Carrega variáveis do .env
load_dotenv()

# Pega o caminho da credencial do .env
cred_path = os.getenv("FIREBASE_CREDENTIALS")

if not cred_path:
    raise ValueError("FIREBASE_CREDENTIALS não definido no .env")

# Inicializa Firebase com a credencial
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

# Cliente do Firestore
db = firestore.client()