# services/codigo_service.py
from django.db.models import Max
from django.utils.crypto import get_random_string
import re

class CodigoGenerator:
    """
    Servicio para generar códigos automáticos
    """
    
    def __init__(self, modelo, campo_codigo='codigo', prefijo='', longitud_minima=1000):
        self.modelo = modelo
        self.campo_codigo = campo_codigo
        self.prefijo = prefijo
        self.longitud_minima = longitud_minima
        self._patron_regex = None
    
    @property
    def patron_regex(self):
        """Obtiene o genera el patrón regex"""
        if self._patron_regex is None and self.prefijo:
            self._patron_regex = rf'^{re.escape(self.prefijo)}\d+$'
        return self._patron_regex
    
    @patron_regex.setter
    def patron_regex(self, valor):
        self._patron_regex = valor
    
    def generar(self, **filtros_extra):
        """
        Genera un nuevo código
        """
        try:
            # Construir queryset con filtros
            queryset = self.modelo.objects.all()
            
            # Aplicar filtros extra si existen
            if filtros_extra:
                queryset = queryset.filter(**filtros_extra)
            
            # Aplicar filtro por patrón si existe
            if self.patron_regex:
                queryset = queryset.filter(**{f"{self.campo_codigo}__regex": self.patron_regex})
            
            # Obtener último código
            ultimo = queryset.aggregate(
                max_numero=Max(self.campo_codigo)
            )
            
            ultimo_numero = self._extraer_numero(ultimo['max_numero'])
            nuevo_numero = max(self.longitud_minima, ultimo_numero + 1)
            
            return f'{self.prefijo}{nuevo_numero}'
            
        except Exception as e:
            print(f"Error generando código: {e}")
            return f'{self.prefijo}{get_random_string(6, "0123456789")}'
    
    def _extraer_numero(self, codigo):
        """Extrae el número de un código"""
        if not codigo:
            return 0
        
        try:
            if self.prefijo:
                numero_str = codigo.replace(self.prefijo, '')
            else:
                match = re.search(r'\d+$', codigo)
                numero_str = match.group() if match else '0'
            
            return int(numero_str)
        except (ValueError, AttributeError):
            return self.longitud_minima - 1
    
    def asignar_a_instancia(self, instancia, **filtros_extra):
        """Asigna código a una instancia si no tiene"""
        if not getattr(instancia, self.campo_codigo):
            nuevo_codigo = self.generar(**filtros_extra)
            setattr(instancia, self.campo_codigo, nuevo_codigo)
            return True
        return False


# Clase helper para usar directamente
def generar_codigo(modelo, prefijo='', campo='codigo', min_valor=1000):
    """Función helper para generar códigos rápidamente"""
    generator = CodigoGenerator(modelo, campo, prefijo, min_valor)
    return generator.generar()