# test_jugadores.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Cargar variables de entorno
load_dotenv()

# Construir la URL de conexión
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Crear engine de SQLAlchemy
engine = create_engine(DATABASE_URL)

# Consultar y mostrar los registros de la tabla 'jugador'
with engine.connect() as conn:
    result = conn.execute(text("SELECT nombre, estado FROM asteroides WHERE nombre = 'eduardo'"))
    jugadores = result.fetchall()
    for jugador in jugadores:
        print(jugador)