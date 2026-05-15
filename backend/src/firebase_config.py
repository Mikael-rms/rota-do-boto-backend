import os
import firebase_admin
from firebase_admin import credentials, firestore

key_path = os.getenv('FIREBASE_KEY_PATH', 'firebasekey.json')
cred = credentials.Certificate(key_path)

firebase_admin.initialize_app(cred)

db = firestore.client()