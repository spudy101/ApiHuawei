# utils/firebase.py
from app.config import storage_bucket

def upload_image_to_storage(image_path):
    blob = storage_bucket.blob(image_path)
    blob.upload_from_filename(image_path)
    return blob.public_url
