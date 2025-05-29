import firebase_admin
from firebase_admin import credentials, firestore, storage
import os
from dotenv import load_dotenv
load_dotenv()

cred = credentials.Certificate('key.json')

app = firebase_admin.initialize_app(cred, {
    'storageBucket': os.getenv('bucket_url')
})
bucket = storage.bucket()

db = firestore.client()