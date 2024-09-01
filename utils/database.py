# utils/database.py
from app.config import db
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from firebase_admin import firestore

def save_detection_to_db(descripcion, latitud, longitud, image_url):
    detection_ref = db.collection('detecciones')
    detection_ref.add({
        'descripcion': descripcion,
        'latitud': latitud,
        'longitud': longitud,
        'image_url': image_url,
        'fecha': firestore.SERVER_TIMESTAMP
    })

def get_all_detections():
    detections = []
    docs = db.collection('detecciones').stream()
    for doc in docs:
        detections.append(doc.to_dict())
    return detections