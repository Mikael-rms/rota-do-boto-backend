import os
import json

from dotenv import load_dotenv

import firebase_admin

from firebase_admin import credentials
from firebase_admin import firestore


load_dotenv()

firebase_key = os.getenv("FIREBASE_KEY")

if not firebase_key:
    raise ValueError("FIREBASE_KEY not found")

firebase_dict = json.loads(firebase_key)

cred = credentials.Certificate(firebase_dict)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()