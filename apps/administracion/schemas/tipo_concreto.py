from typing import Optional, List
from datetime import datetime
from ninja import Schema, ModelSchema
from pydantic import field_validator, model_validator, ConfigDict
from decimal import Decimal

class SchemaCrear(Schema):
    nombre: str
    descripcion: Optional[str] = None

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator('nombre', mode='before')
    @classmethod
    def validar_nombre_tipo(cls, v):
        """Validar que el nombre sea de tipo string"""
        if v is None:
            raise ValueError('El campo nombre es requerido')
        
        # Validar que sea string
        if not isinstance(v, str):
            raise ValueError('El campo nombre debe ser string')
        
        # Validar que no esté vacío después de quitar espacios
        v = v.strip()
        if not v:
            raise ValueError('El campo nombre no puede estar vacío')
        
        # Validar longitud mínima
        if len(v) < 3:
            raise ValueError('El nombre debe tener al menos 3 caracteres')
        
        # Validar longitud máxima
        if len(v) > 100:
            raise ValueError('El nombre no puede exceder los 100 caracteres')
        
        return v


# class TipoPeriodoUpdateSchema(Schema):
#     nombre: Optional[str] = None
#     descripcion: Optional[str] = None
#     is_active: Optional[bool] = None

class SchemaListar(Schema):
    id: int
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    precio_actual: Optional[Decimal] = None
    
    class Config:
        from_attributes = True
        
    @staticmethod
    def from_orm(obj):
        """Método personalizado para incluir el property"""
        return {
            "id": obj.id,
            "codigo": obj.codigo,
            "nombre": obj.nombre,
            "descripcion": obj.descripcion,
            "precio_actual": obj.precio_actual  # Esto usa el property
        }