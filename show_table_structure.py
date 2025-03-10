from app import create_app
from app.models import db
from sqlalchemy import inspect
import pprint

def get_table_structure():
    inspector = inspect(db.engine)
    
    print("Estructura de la tabla 'ahorros':")
    pprint.pprint(inspector.get_columns('ahorros'))
    
    print("\nEstructura de la tabla 'usuarios':")
    pprint.pprint(inspector.get_columns('usuarios'))

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        get_table_structure() 