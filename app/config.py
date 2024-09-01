# app/config.py
import firebase_admin
from firebase_admin import credentials, firestore, storage

# Inicializar Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'bdhuawei-8c7ba.appspot.com'  # Reemplaza con tu bucket de Firebase
})
db = firestore.client()
bucket = storage.bucket()