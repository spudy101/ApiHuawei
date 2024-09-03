# utils/database.py
from app.config import db
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from firebase_admin import firestore

def save_detection_to_db(descripcion, latitud, longitud, image_urls, id_categoria, comuna):
    detection_ref = db.collection('deteccion')
    detection_ref.add({
        'descripcion': descripcion,
        'latitud': latitud,
        'longitud': longitud,
        'image_urls': image_urls,  # Guardar la lista de URLs
        'id_categoria': id_categoria,
        'comuna': comuna,
        'fecha': firestore.SERVER_TIMESTAMP
    })

def get_all_detections():
    detections = []
    docs = db.collection('deteccion').stream()

    # Cache para evitar consultar la misma categoría varias veces
    categorias_cache = {}

    for doc in docs:
        data = doc.to_dict()

        # Obtener el id de la categoría
        id_categoria = data.get('id_categoria')

        if id_categoria:
            # Verificar si el id_categoria ya está en el cache
            if id_categoria in categorias_cache:
                nombre_categoria = categorias_cache[id_categoria]
            else:
                # Consultar la categoría en la colección 'categoria'
                categoria_doc = db.collection('categoria').document(id_categoria).get()

                if categoria_doc.exists:
                    nombre_categoria = categoria_doc.to_dict().get('nombre_categoria')
                    categorias_cache[id_categoria] = nombre_categoria
                else:
                    nombre_categoria = "Categoría no encontrada"

            # Añadir el nombre de la categoría a los datos de la detección
            data['nombre_categoria'] = nombre_categoria
        else:
            data['nombre_categoria'] = "ID de categoría no proporcionado"

        detections.append(data)

    return detections

