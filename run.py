import os
from app import create_app

# Determinar el entorno (desarrollo por defecto)
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    app.run() 