from typing import Optional, List
from ninja import Schema

class SchemaListarVehiculo(Schema):
    id: int
    matricula: str
    alias: str
    modelo: Optional[str] = None
    marca: Optional[str] = None

class SchemaListar(Schema):
    id: int
    vehiculo_id: Optional[SchemaListarVehiculo] = None  # Mantén vehiculo_id si así lo prefieres en la respuesta
    nombre: str
    licencia: str
    telefono: str
    
    @classmethod
    def from_orm(cls, conductor):
        # Serializar el vehículo del conductor
        vehiculo_data = None
        if hasattr(conductor, 'vehiculo') and conductor.vehiculo:
            vehiculo_data = SchemaListarVehiculo.from_orm(conductor.vehiculo)
        # O si el campo se llama 'vehiculo_id' en el modelo:
        # elif hasattr(conductor, 'vehiculo_id') and conductor.vehiculo_id:
        #     vehiculo_data = SchemaListarVehiculo.from_orm(conductor.vehiculo_id)
        
        return cls(
            id=conductor.id,
            vehiculo_id=vehiculo_data,
            nombre=conductor.nombre,
            licencia=conductor.licencia,
            telefono=conductor.telefono
        )