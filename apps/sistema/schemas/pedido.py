from typing import Optional, List
from datetime import date, time, datetime
from ninja import Schema
from decimal import Decimal
from django.utils.timezone import make_naive
from pydantic import field_validator, model_validator, ConfigDict
import re
import pytz

class CrearPedidoSchema(Schema):
    cliente_id: int
    tipo_concreto_id: int
    cantidad_yardas: Decimal
    direccion_entrega: str
    fecha_entrega: date
    hora_entrega: str  # Cambiado a string
    nota: Optional[str] = None
    slump: Optional[int] = None
    agregados: Optional[List[int]] = None
    
    @staticmethod
    def parse_time(time_str: str) -> time:
        """
        Convierte string de tiempo a time object naive
        """
        try:
            # Intentar parsear como datetime con timezone
            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            # Convertir a naive (sin timezone) para MySQL
            if dt.tzinfo:
                dt = make_naive(dt, pytz.UTC)
            return dt.time()
        except (ValueError, AttributeError):
            # Si falla, intentar parsear como time directo
            try:
                return time.fromisoformat(time_str.split('Z')[0])
            except ValueError:
                # Si es formato simple HH:MM:SS
                return time.fromisoformat(time_str)
    
    # ============= VALIDACIÓN DE IDs (ENTEROS) =============

    @field_validator('cliente_id', 'tipo_concreto_id', mode='before')
    @classmethod
    def validar_ids_enteros(cls, v, info):
        """Validar que los IDs sean números enteros válidos"""
        field_name = info.field_name
        
        if v is None:
            raise ValueError(f'El campo {field_name} es requerido')
        
        # Rechazar strings aunque sean números
        if isinstance(v, str):
            raise ValueError(f'El campo {field_name} debe ser un número entero')
        
        if not isinstance(v, int):
            raise ValueError(f'El campo {field_name} debe ser un número entero')
        
        if v <= 0:
            raise ValueError(f'El campo {field_name} debe ser un número positivo')
        
        return v

    @field_validator('agregados', mode='before')
    @classmethod
    def validar_lista_agregados(cls, v, info):
        """Validar que agregados sea una lista de enteros"""
        if v is None:
            return v
        
        if not isinstance(v, list):
            raise ValueError('El campo agregados debe ser una lista')
        
        if len(v) == 0:
            return v
        
        for i, item in enumerate(v):
            if isinstance(item, str):
                raise ValueError(f'El agregado en posición {i+1} debe ser un número entero')
            
            if not isinstance(item, int):
                raise ValueError(f'El agregado en posición {i+1} debe ser un número entero')
            
            if item <= 0:
                raise ValueError(f'El agregado en posición {i+1} debe ser un número positivo')
        
        # Eliminar duplicados
        v = list(set(v))
        
        return v

    # ============= VALIDACIÓN DE CANTIDAD YARDAS (DECIMAL) =============

    @field_validator('cantidad_yardas', mode='before')
    @classmethod
    def validar_cantidad_yardas(cls, v, info):
        """Validar que cantidad_yardas sea un número decimal válido"""
        field_name = info.field_name
        
        if v is None:
            raise ValueError(f'El campo {field_name} es requerido')
        
        # Si es string, validar formato antes de convertir
        if isinstance(v, str):
            v = v.strip()
            
            if not v:
                raise ValueError(f'El campo {field_name} es requerido')
            
            # Validar caracteres permitidos
            if not re.match(r'^[\d\.,]+$', v):
                raise ValueError(f'El campo {field_name} contiene caracteres inválidos')
            
            # Validar que no haya múltiples puntos o comas
            if v.count('.') > 1 or v.count(',') > 1:
                raise ValueError(f'Formato de {field_name} inválido')
            
            # Normalizar decimal (convertir coma a punto)
            v = v.replace(',', '.')
            
            # Validar formato de número decimal
            if not re.match(r'^\d+(\.\d+)?$', v):
                raise ValueError(f'El campo {field_name} debe ser un número válido')
            
            # Validar decimales (máximo 1 decimal)
            if '.' in v:
                decimales = v.split('.')[1]
                if len(decimales) > 1:
                    raise ValueError(f'El campo {field_name} solo puede tener máximo 1 decimal')
        
        # Convertir a Decimal
        try:
            valor = Decimal(str(v))
        except:
            raise ValueError(f'El campo {field_name} debe ser un número válido')
        
        # Validaciones de negocio
        if valor <= 0:
            raise ValueError(f'El campo {field_name} debe ser mayor a 0')
        
        if valor > 1000:
            raise ValueError(f'El campo {field_name} no puede exceder 1000 yardas')
        
        # Validar que sea múltiplo de 0.5
        if valor % Decimal('0.5') != 0:
            raise ValueError(f'El campo {field_name} debe ser múltiplo de 0.5')
        
        return valor

    # ============= VALIDACIÓN DE DIRECCIÓN (STRING) =============

    @field_validator('direccion_entrega', mode='before')
    @classmethod
    def validar_direccion(cls, v, info):
        """Validar que la dirección sea un string válido"""
        field_name = info.field_name
        
        if v is None:
            raise ValueError(f'El campo {field_name} es requerido')
        
        if not isinstance(v, str):
            raise ValueError(f'El campo {field_name} debe ser texto')
        
        v = v.strip()
        
        if not v:
            raise ValueError(f'El campo {field_name} es requerido')
        
        if len(v) < 5:
            raise ValueError(f'El campo {field_name} debe tener al menos 5 caracteres')
        
        if len(v) > 255:
            raise ValueError(f'El campo {field_name} no puede exceder 255 caracteres')
        
        # Validar que no sean solo espacios o caracteres especiales
        if not re.search(r'[a-zA-Z0-9]', v):
            raise ValueError(f'El campo {field_name} debe contener letras o números')
        
        # Prevenir XSS - eliminar etiquetas HTML
        v = re.sub(r'<[^>]*>', '', v)
        
        return v

    # ============= VALIDACIÓN DE FECHA ENTREGA =============

    @field_validator('fecha_entrega', mode='before')
    @classmethod
    def validar_fecha_entrega(cls, v, info):
        """Validar el formato de la fecha de entrega"""
        field_name = info.field_name
        
        if v is None:
            raise ValueError(f'El campo {field_name} es requerido')
        
        if isinstance(v, str):
            v = v.strip()
            
            if not v:
                raise ValueError(f'El campo {field_name} es requerido')
            
            # Validar formato YYYY-MM-DD
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', v):
                raise ValueError(f'Formato de {field_name} inválido. Use YYYY-MM-DD')
            
            # Validar que sean números válidos
            año, mes, dia = v.split('-')
            
            if not (1 <= int(mes) <= 12):
                raise ValueError(f'Mes inválido en {field_name}')
            
            if not (1 <= int(dia) <= 31):
                raise ValueError(f'Día inválido en {field_name}')
        
        # Convertir a date
        try:
            fecha = date.fromisoformat(v) if isinstance(v, str) else v
        except ValueError:
            raise ValueError(f'Fecha inválida en {field_name}')
        
        # Validar que no sea anterior a hoy
        from datetime import date as d
        if fecha < d.today():
            raise ValueError(f'La {field_name} no puede ser anterior a hoy')
        
        # Validar límite máximo (30 días)
        from datetime import timedelta
        max_fecha = d.today() + timedelta(days=30)
        if fecha > max_fecha:
            raise ValueError(f'La {field_name} no puede ser más de 30 días en el futuro')
        
        return fecha

    # ============= VALIDACIÓN DE HORA ENTREGA =============

    @field_validator('hora_entrega', mode='before')
    @classmethod
    def validar_hora_entrega(cls, v, info):
        """Validar el formato de la hora de entrega"""
        field_name = info.field_name
        
        if v is None:
            raise ValueError(f'El campo {field_name} es requerido')
        
        if not isinstance(v, str):
            raise ValueError(f'El campo {field_name} debe ser texto')
        
        v = v.strip()
        
        if not v:
            raise ValueError(f'El campo {field_name} es requerido')
        
        # Aceptar formatos: HH, HH:MM, HH:MM:SS
        patrones = [
            r'^([01]?[0-9]|2[0-3])$',                                   # HH
            r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$',                        # HH:MM
            r'^([01]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$'             # HH:MM:SS
        ]
        
        hora_valida = False
        for patron in patrones:
            if re.match(patron, v):
                hora_valida = True
                break
        
        if not hora_valida:
            raise ValueError(f'Formato de {field_name} inválido. Use HH:MM:SS (ej: 14:30:00)')
        
        # Normalizar a formato HH:MM:SS
        partes = v.split(':')
        if len(partes) == 1:
            v = f"{int(partes[0]):02d}:00:00"
        elif len(partes) == 2:
            v = f"{int(partes[0]):02d}:{int(partes[1]):02d}:00"
        else:
            v = f"{int(partes[0]):02d}:{int(partes[1]):02d}:{int(partes[2]):02d}"
        
        # Validar horario laboral (opcional)
        hora = int(v.split(':')[0])
        if hora < 6 or hora > 22:
            raise ValueError(f'La {field_name} debe estar entre 06:00 y 22:00')
        
        return v

    # ============= VALIDACIÓN DE SLUMP (OPCIONAL) =============

    @field_validator('slump', mode='before')
    @classmethod
    def validar_slump(cls, v, info):
        """Validar que el slump sea un número entero válido"""
        if v is None:
            return v
        
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return None
            
            if not v.isdigit():
                raise ValueError('El campo slump debe ser un número entero')
            v = int(v)
        
        if not isinstance(v, int):
            raise ValueError('El campo slump debe ser un número entero')
        
        if v < 1 or v > 10:
            raise ValueError('El campo slump debe estar entre 1 y 10')
        
        valores_permitidos = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        if v not in valores_permitidos:
            raise ValueError(f'El campo slump debe ser uno de: {valores_permitidos}')
        
        return v

    # ============= VALIDACIÓN DE NOTA (OPCIONAL) =============

    @field_validator('nota', mode='before')
    @classmethod
    def validar_nota(cls, v, info):
        """Validar que la nota sea un string válido"""
        if v is None:
            return v
        
        if not isinstance(v, str):
            raise ValueError('El campo nota debe ser texto')
        
        v = v.strip()
        
        if not v:
            return None
        
        if len(v) > 500:
            raise ValueError('El campo nota no puede exceder 500 caracteres')
        
        if len(v) < 3:
            raise ValueError('El campo nota debe tener al menos 3 caracteres')
        
        # Prevenir XSS
        v = re.sub(r'<[^>]*>', '', v)
        
        return v

    # ============= VALIDACIONES CRUZADAS =============

    @model_validator(mode='after')
    def validar_fecha_hora_combinada(self):
        """Validar que fecha y hora combinadas no sean en el pasado"""
        if self.fecha_entrega and self.hora_entrega:
            try:
                # Parsear la hora
                partes = self.hora_entrega.split(':')
                hora = int(partes[0])
                minuto = int(partes[1]) if len(partes) > 1 else 0
                segundo = int(partes[2]) if len(partes) > 2 else 0
                
                # Crear datetime combinado
                fecha_hora_entrega = datetime.combine(
                    self.fecha_entrega, 
                    datetime.min.time()
                ).replace(hour=hora, minute=minuto, second=segundo)
                
                # Comparar con ahora
                ahora = datetime.now()
                
                if fecha_hora_entrega < ahora:
                    raise ValueError('La fecha y hora de entrega no pueden ser en el pasado')
                    
            except Exception as e:
                raise ValueError(f'Error validando fecha/hora: {str(e)}')
        
        return self

    @model_validator(mode='after')
    def validar_slump_segun_concreto(self):
        """Validar slump según tipo de concreto (ejemplo)"""
        # Esta validación requeriría consultar la base de datos
        # Se puede implementar en la vista o con un validator personalizado
        return self

    # ============= MÉTODO AUXILIAR =============

    @staticmethod
    def parse_time(time_str: str) -> time:
        """Convierte string de tiempo a time object naive"""
        if not time_str:
            raise ValueError('La hora de entrega es requerida')
        
        try:
            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            if dt.tzinfo:
                dt = make_naive(dt, pytz.UTC)
            return dt.time()
        except (ValueError, AttributeError):
            try:
                return time.fromisoformat(time_str.split('Z')[0])
            except ValueError:
                partes = time_str.split(':')
                if len(partes) == 1:
                    return time(int(partes[0]), 0, 0)
                elif len(partes) == 2:
                    return time(int(partes[0]), int(partes[1]), 0)
                else:
                    return time(int(partes[0]), int(partes[1]), int(partes[2]))

class SchemaListarEntrega(Schema):
    id: int
    pedido_id: int
    codigo_entrega: str
    yardas_asignadas: Decimal
    
    @classmethod
    def from_orm(cls, entrega):
        return cls(
            id=entrega.id,
            pedido_id=entrega.pedido_id,
            codigo_entrega=entrega.codigo_entrega,
            yardas_asignadas=entrega.yardas_asignadas,
        )

class SchemaListarPedido(Schema):
    id: int
    codigo_pedido: str
    cantidad_yardas: Decimal
    entregas: List[SchemaListarEntrega] = []
    
    # ✅ SOLO LO QUE NECESITAS
    cliente_nombre: str
    tipo_concreto_nombre: str
    direccion_entrega: str
    fecha_entrega: date
    hora_entrega: str
    estado_pedido: str
    precio_total: Decimal
    agregados: List[dict] = []  # Lista de objetos con id y nombre
    
    @classmethod
    def from_orm(cls, pedido):
        return cls(
            id=pedido.id,
            codigo_pedido=pedido.codigo_pedido,
            cantidad_yardas=pedido.cantidad_yardas,
            entregas=[SchemaListarEntrega.from_orm(e) for e in pedido.entrega_set.all()],
            
            # Nombres directamente
            cliente_nombre=pedido.cliente.nombre_apellido or pedido.cliente.username,
            tipo_concreto_nombre=pedido.tipo_concreto.nombre,
            direccion_entrega=pedido.direccion_entrega,
            fecha_entrega=pedido.fecha_entrega,
            hora_entrega=str(pedido.hora_entrega) if pedido.hora_entrega else "",
            estado_pedido=str(pedido.estado_pedido),
            precio_total=pedido.precio_total or 0,
            
            # ✅ AGREGADOS COMO LISTA DE OBJETOS
            agregados=[
                {"id": a.id, "nombre": a.nombre} 
                for a in pedido.agregado.all()
            ]
        )

class EntregaActionResponse(Schema):
    success: bool
    message: str
    estado: Optional[str] = None
    fecha_hora_salida: Optional[datetime] = None
    fecha_hora_entrega: Optional[datetime] = None
    conductor_disponible: Optional[bool] = None
    vehiculo_disponible: Optional[bool] = None
    pedido_estado: Optional[str] = None

class EntregaActionRequest(Schema):
    motivo: Optional[str] = None  # Para cancelaciones