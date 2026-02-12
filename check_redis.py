import redis
from decouple import config

def test_redis_connection():
    try:
        redis_url = config('REDIS_URL')
        print(f"Intentando conectar a: {redis_url}")
        
        # Conectar usando la URL
        r = redis.from_url(redis_url)
        
        # Probar conexión
        r.ping()
        print("✅ Conexión Redis exitosa!")
        
        # Probar channels
        print("Probando funcionalidad básica...")
        r.set('test_key', 'test_value', ex=10)
        value = r.get('test_key')
        print(f"✅ Valor recuperado: {value.decode()}")
        
        return True
    except Exception as e:
        print(f"❌ Error conectando a Redis: {e}")
        return False

if __name__ == "__main__":
    test_redis_connection()