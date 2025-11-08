# app/models/alianzas.py
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from ..db.base import Base # ¡Revisa esta importación!
import datetime

class Alianza(Base):
    __tablename__ = "alianzas"
    
    alianza_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True, nullable=False)
    tag = Column(String, unique=True, length=5, nullable=False)
    owner_jugador_id = Column(Integer, ForeignKey('jugadores.id'))
    puntos_prestigio = Column(Integer, default=0)
    descripcion = Column(String)
    
    miembros = relationship("MiembroAlianza", back_populates="alianza")

class MiembroAlianza(Base):
    __tablename__ = "alianza_miembros"
    
    miembro_id = Column(Integer, primary_key=True)
    alianza_id = Column(Integer, ForeignKey('alianzas.alianza_id'))
    jugador_id = Column(Integer, ForeignKey('jugadores.id'))
    rol = Column(Enum('lider', 'oficial', 'miembro', name='rol_alianza_enum'), default='miembro')
    
    alianza = relationship("Alianza", back_populates="miembros")
    # Puedes añadir 'jugador = relationship("Jugador")' si lo necesitas

class Asedio(Base):
    __tablename__ = "asedios"
    
    asedio_id = Column(Integer, primary_key=True)
    planeta_id = Column(String, index=True, nullable=False)
    alianza_atacante_id = Column(Integer, ForeignKey('alianzas.alianza_id'))
    fecha_inicio = Column(DateTime, default=datetime.datetime.utcnow)
    fecha_fin = Column(DateTime, nullable=False)

class RefuerzoAsedio(Base):
    __tablename__ = "asedio_refuerzos"
    
    refuerzo_id = Column(Integer, primary_key=True)
    asedio_id = Column(Integer, ForeignKey('asedios.asedio_id'))
    jugador_id = Column(Integer, ForeignKey('jugadores.id'))
    unidades_enviadas = Column(String) # JSON String: '[{"tipo": "Infanteria", "qty": 1000}]'
    recursos_enviados = Column(String) # JSON String