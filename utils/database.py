# utils/database.py
from app.config import db
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from firebase_admin import firestore

def save_detection_to_db(Type, comentariosid, comuna, image_urls, cordenadas, description, title, iconMarkerId):
    detection_ref = db.collection('alerta')
    detection_ref.add({
        'Type': Type,
        'comentariosID': comentariosid,
        'comuna': comuna,
        'image_urls': image_urls,  # Guardar la lista de URLs
        'cordenadas': cordenadas,
        'description': description,
        'fecha': firestore.SERVER_TIMESTAMP,
        'title': title,
        'iconMarkerid': iconMarkerId,
    })

def get_all_detections():
    detections = []
    docs = db.collection('alerta').stream()

    for doc in docs:
        data = doc.to_dict()

        detections.append(data)

    return detections
