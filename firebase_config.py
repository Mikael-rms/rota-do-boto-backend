import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

key_path = os.getenv("FIREBASE_KEY_PATH")

if not key_path:
    raise ValueError("FIREBASE_KEY_PATH not set in .env")

cred = credentials.Certificate(os.path.join(BASE_DIR, key_path))

firebase_admin.initialize_app(cred)

db = firestore.client()