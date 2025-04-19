import os
from pathlib import Path

BASE_DIR = Path(__file__).parent


class Config:
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    SECRET_KEY = 'your-secret-key-here'

    @staticmethod
    def init_app(app):
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)