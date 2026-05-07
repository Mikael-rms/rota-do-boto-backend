import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

path = os.getenv("FIREBASE_KEY_PATH")

print("DEBUG PATH:", path)  

if not path:
    raise ValueError("FIREBASE_KEY_PATH not set in .env")

cred = credentials.Certificate(os.path.join(BASE_DIR, path))
firebase_admin.initialize_app(cred)

db = firestore.client()