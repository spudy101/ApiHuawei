from flask import Blueprint, request, jsonify
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
    id_categoria = data.get('id_categoria')

    # Validar que se ha enviado una lista de imágenes
    if not isinstance(image_data_list, list):
        return jsonify({"error": "Las imágenes deben ser enviadas en una lista"}), 400

    comuna = get_comuna(latitud, longitud)
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

    # Otros campos de la detección
    comments = "Alertar a los vecinos!"
    Type = "Vandalismo"
    title = "Vandalismo"
    user = "Jorge"

    # Guardar la detección en la base de datos con las URLs de las imágenes
    save_detection_to_db(Type, latitud, longitud, urls, comments, description, title, user, comuna, id_categoria)

    return jsonify({"message": "Detecciones guardadas con éxito", "image_urls": urls})

@api_bp.route('/detections', methods=['GET'])
def get_detections():
    try:
        detections = get_all_detections()
        return jsonify(detections), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
