import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

path = os.getenv("FIREBASE_CREDENTIALS_PATH")
print("PATH:", path)
cred = credentials.Certificate(path)
firebase_admin.initialize_app(cred)

db = firestore.client()