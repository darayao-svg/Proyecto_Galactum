# create_tables.py
from app.db.session import engine, Base
from app.models.user import User
from app.models.server import Server

def main():
    print("Creando tablas si no existen...")
    Base.metadata.create_all(bind=engine)
    print("Listo.")

if __name__ == "__main__":
    main()
