import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Carrega o .env
load_dotenv()

# Pega o diretório onde este arquivo (firebase.py) está
# Isso vai retornar o caminho até .../src/config/
base_dir = os.path.dirname(os.path.abspath(__file__))

# Monta o caminho completo para o arquivo JSON na mesma pasta
path = os.path.join(base_dir, "serviceAccountKey.json")

print(f"🔥 Tentando carregar credenciais em: {path}")

# Inicializa o Firebase
cred = credentials.Certificate(path)
firebase_admin.initialize_app(cred)

db = firestore.client()