from app import create_app
from app.models import db
from sqlalchemy import inspect

def get_table_structure():
    inspector = inspect(db.engine)
    
    print("Estructura de la tabla 'ahorros':")
    columns = inspector.get_columns('ahorros')
    for column in columns:
        print(f"- {column['name']}: {column['type']} (Nullable: {column['nullable']})")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        get_table_structure() 