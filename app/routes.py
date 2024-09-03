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

    descripcion = data.get('descripcion')
    latitud = data.get('latitud')
    longitud = data.get('longitud')
    image_data = data.get('image_data')
    id_categoria = data.get('id_categoria')

    if not image_data:
        return jsonify({"error": "No se ha enviado imagen"}), 400

    comuna = get_comuna(latitud, longitud)
    
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

    # Verificar si hay detecciones cercanas recientes de la misma categoría
    detection_ref = db.collection('deteccion')
    query_time = datetime.now() - timedelta(hours=1)
    detecciones_recientes = detection_ref \
        .where('id_categoria', '==', id_categoria) \
        .where('fecha', '>=', query_time).stream()

    for deteccion in detecciones_recientes:
        data = deteccion.to_dict()
        coord_1 = (latitud, longitud)
        coord_2 = (float(data['latitud']), float(data['longitud']))
        distancia = geodesic(coord_1, coord_2).km

        if distancia <= 1:  # Si está a menos de 1 km de distancia
            return jsonify({"error": "Ya existe una detección reciente en esta área."}), 400

    # Guardar la detección en la base de datos con la URL pública y el id_categoria
    save_detection_to_db(descripcion, latitud, longitud, image_url, id_categoria, comuna)

    return jsonify({"message": "Detección guardada con éxito", "image_url": image_url})


@api_bp.route('/detections', methods=['GET'])
def get_detections():
    try:
        detections = get_all_detections()
        return jsonify(detections), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
