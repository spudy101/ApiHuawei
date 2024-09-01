from flask import Blueprint, request, jsonify
import base64
from datetime import datetime
from utils.database import save_detection_to_db, get_all_detections
from app.config import bucket
 
api_bp = Blueprint('api', __name__)

@api_bp.route('/add_detecciones', methods=['POST'])
def add_detection():
    data = request.get_json()

    descripcion = data.get('descripcion')
    latitud = data.get('latitud')
    longitud = data.get('longitud')
    image_data = data.get('image_data')

    if not image_data:
        return jsonify({"error": "No se ha enviado imagen"}), 400

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

    # Guardar la detección en la base de datos con la URL pública
    save_detection_to_db(descripcion, latitud, longitud, image_url)

    return jsonify({"message": "Detección guardada con éxito", "image_url": image_url})

@api_bp.route('/detections', methods=['GET'])
def get_detections():
    try:
        detections = get_all_detections()
        return jsonify(detections), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
