from sqlalchemy import Column, String, Text, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
# Ajusta este import si tu Base está en otro lado (ej: app.db.base_class)
from app.db.base import Base 

class catalogo_items(Base):
    __tablename__ = "catalogo_items"
    # Al ser explícitos con el esquema, la tabla se registra como "public.catalogo_items"
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text)
    tipo = Column(String, nullable=False) # ej: 'recurso', 'componente', 'equipamiento'

class RecetaCrafteo(Base):
    __tablename__ = "recetas_crafteo"
    
    # Es buena práctica definir también el esquema aquí si estás usándolo explícitamente
    __table_args__ = (
        UniqueConstraint('item_resultado_id', 'item_requerido_id', name='uniq_resultado_requerido'),
        {'schema': 'public'}
    )

    id = Column(Integer, primary_key=True, index=True)
    
    # CORRECCIÓN: Agregamos 'public.' al inicio para coincidir con el esquema de la tabla destino
    item_resultado_id = Column(Integer, ForeignKey('public.catalogo_items.id'), nullable=False)
    item_requerido_id = Column(Integer, ForeignKey('public.catalogo_items.id'), nullable=False)
    
    cantidad = Column(Integer, nullable=False)

    # Relaciones
    item_resultado = relationship(
        "catalogo_items", 
        foreign_keys=[item_resultado_id],
        backref="recetas_produccion"
    )

    item_requerido = relationship(
        "catalogo_items", 
        foreign_keys=[item_requerido_id], 
        backref="recetas_uso"
    )