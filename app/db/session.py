# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Base declarativa para que los modelos la hereden.
# Esto es lo único que definimos a nivel global en este archivo.
Base = declarative_base()

# NOTA IMPORTANTE:
# Hemos eliminado la creación del 'engine' y 'SessionLocal' de este archivo.
# Se crearán en app/main.py para asegurar que usen las variables de entorno
# correctas de Render (producción) en lugar de valores locales por defecto.
# La función get_db también se ha eliminado porque su lógica ahora
# dependerá de cómo se gestionen las sesiones en los endpoints.