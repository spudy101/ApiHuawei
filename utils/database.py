# utils/database.py
from app.config import db
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from firebase_admin import firestore

def save_detection_to_db(Type, latitud, longitud, image_urls, comments, description, title, user, comuna, id_categoria):
    detection_ref = db.collection('alerta')
    detection_ref.add({
        'Type': Type,
        'latitud': latitud,
        'longitud': longitud,
        'image_urls': image_urls,  # Guardar la lista de URLs
        'comments': comments,
        'description': description,
        'fecha': firestore.SERVER_TIMESTAMP,
        'title': title,
        'user': user,
        'comuna': comuna,
        'id_categoria': id_categoria
    })

def get_all_detections():
    detections = []
    docs = db.collection('alerta').stream()

    for doc in docs:
        data = doc.to_dict()

        detections.append(data)

    return detections
