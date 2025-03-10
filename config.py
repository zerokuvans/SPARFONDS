import os
from dotenv import load_dotenv
import urllib.parse

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class Config:
    # Configuración de la aplicación
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave_por_defecto')
    
    # Configuración de la base de datos
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_NAME = os.environ.get('DB_NAME', 'sparfonds')
    
    # Escapar la contraseña para manejar caracteres especiales
    ESCAPED_PASSWORD = urllib.parse.quote_plus(DB_PASSWORD)
    
    # Construir la URI de conexión correctamente
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{ESCAPED_PASSWORD}@{DB_HOST}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

# Configuración para elegir según el entorno
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 