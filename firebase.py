import firebase_admin
from firebase_admin import credentials, firestore, storage
from google.cloud.firestore_v1.collection import CollectionReference
from google.cloud.firestore_v1.document import DocumentReference
import os
from dotenv import load_dotenv
load_dotenv()

cred = credentials.Certificate('key.json')

app = firebase_admin.initialize_app(cred, {
    'storageBucket': os.getenv('bucket_url')
})
bucket = storage.bucket()

db = firestore.client()

def household_ref() -> CollectionReference:
    return db.collection('household')

def user_ref() -> CollectionReference:
    return db.collection('users')

# Use these for end-to-end testing, as these collections are in the real database but are reserved for testing.
def household_test_ref() -> CollectionReference:
    return db.collection('test_household')

def user_test_ref() -> CollectionReference:
    return db.collection('test_user')