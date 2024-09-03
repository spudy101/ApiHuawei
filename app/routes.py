from flask import Blueprint, request, jsonify
import random
import base64
from utils.database import save_detection_to_db, get_all_detections
from app.config import bucket, db 
from datetime import datetime, timedelta
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderInsufficientPrivileges, GeocoderServiceError

api_bp = Blueprint('api', __name__)

def get_comuna(lat, lon):
    try:
        geolocator = Nominatim(user_agent="nombre_de_tu_aplicacion")
        location = geolocator.reverse((lat, lon), exactly_one=True)
        address = location.raw['address']
        comuna = address.get('city_district', None) or address.get('suburb', None) or address.get('town', None)
        return comuna
    except GeocoderInsufficientPrivileges as e:
        print(f"Error de privilegios insuficientes: {e}")
        return None
    except GeocoderServiceError as e:
        print(f"Error del servicio de geocodificación: {e}")
        return None

@api_bp.route('/add_detecciones', methods=['POST'])
def add_detection():
    data = request.get_json()
    latitud = data.get('latitud')
    longitud = data.get('longitud')
    image_data_list = data.get('image_data')  # Lista de imágenes en base64
    description = data.get('description')

    tipos_alerta = ['Choque', 'Fuego', 'Pelea', 'Robo', 'Vandalismo']
    tipo_alerta = random.choice(tipos_alerta)

    # Obtener el iconMarkerId correspondiente al tipo de alerta
    iconMarkerId = obtener_icon_marker_id(tipo_alerta)

    # Validar que se ha enviado una lista de imágenes
    if not isinstance(image_data_list, list):
        return jsonify({"error": "Las imágenes deben ser enviadas en una lista"}), 400

    comuna = get_comuna(latitud, longitud)
    coordenadas = [latitud, longitud]
    urls = []

    for image_data in image_data_list:
        # Decodificar la imagen
        image_bytes = base64.b64decode(image_data)
        image_name = f"detected_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

        # Crear un blob en el bucket y subir la imagen
        blob = bucket.blob(image_name)
        blob.upload_from_string(image_bytes, content_type='image/jpeg')

        # Hacer que la imagen sea pública
        blob.make_public()

        # Obtener la URL pública
        image_url = blob.public_url
        urls.append(image_url)

    # Guardar la detección en la base de datos con las URLs de las imágenes
    save_detection_to_db(tipo_alerta, [], comuna, urls, coordenadas, description, tipo_alerta, iconMarkerId)

    return jsonify({"message": "Detecciones guardadas con éxito", "image_urls": urls})

def obtener_icon_marker_id(tipo_alerta):
    try:
        # Consulta a Firebase para obtener el iconMarker correspondiente al tipo de alerta
        icon_markers_ref = db.collection('iconMarker')
        query = icon_markers_ref.where('type', '==', tipo_alerta).stream()

        for doc in query:
            return doc.id  # Retorna el primer ID encontrado para el tipo de alerta

        raise ValueError(f"No se encontró un iconMarker para el tipo {tipo_alerta}")

    except Exception as e:
        print(f"Error al obtener el iconMarkerId: {e}")
        return "default_icon_id"  # Retorna un ID por defecto si no se encuentra el icono

@api_bp.route('/detections', methods=['GET'])
def get_detections():
    try:
        detections = get_all_detections()
        return jsonify(detections), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
