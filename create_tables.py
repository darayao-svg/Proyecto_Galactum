# Importaciones de sistema para arreglar el path de importación
import sys
import os

# Añade el directorio principal del proyecto al path de Python
# para que pueda encontrar la carpeta 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))


# --- El resto del código es similar, pero con la importación corregida ---
from dotenv import load_dotenv
from sqlalchemy import create_engine

# ¡IMPORTACIÓN CORREGIDA!
# Basado en tu proyecto, la clase Base probablemente está en session.py
from app.db.session import Base 

# Importa los modelos para que SQLAlchemy sepa qué tablas crear
from app.models.user import User
from app.models.server import Server


# Carga las variables de entorno desde tu archivo .env
print("Cargando configuración desde el archivo .env...")
load_dotenv()

# Lee cada variable de entorno necesaria para la conexión
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Construye la URL de conexión a la base de datos de Supabase
if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    raise ValueError("Una o más variables de entorno de la base de datos no están definidas en tu archivo .env")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def main():
    try:
        # Crea el "motor" de SQLAlchemy con la URL de Supabase
        engine = create_engine(DATABASE_URL)
        
        print("Conectando a la base de datos en Supabase...")
        engine.connect()
        print("Conexión exitosa.")

        print("Creando todas las tablas si no existen...")
        # SQLAlchemy crea las tablas en Supabase
        Base.metadata.create_all(bind=engine)
        print("¡Listo! Las tablas han sido creadas exitosamente en Supabase.")

    except Exception as e:
        print(f"Ocurrió un error: {e}")


if __name__ == "__main__":
    main()