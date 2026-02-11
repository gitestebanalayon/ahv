# # test_websocket_final.py
# import asyncio
# import websockets
# import json

# async def probar_conexion(operativo):
#     uri = f"ws://localhost:8000/ws/pedidos/{operativo}/"
    
#     try:
#         async with websockets.connect(uri) as websocket:
#             print(f"✅ Conectado a operativo: {operativo}")
#             print(f"   URL: {uri}")
            
#             # Esperar mensajes (el consumer no envía nada automáticamente)
#             # Para probar, necesitas enviar un mensaje al grupo desde otro lado
            
#             # Por ahora, solo mantenemos la conexión abierta 10 segundos
#             for i in range(10):
#                 await asyncio.sleep(1)
#                 print(f"⏳ {operativo}: conexión activa... ({i+1}/10)")
            
#             await websocket.close()
#             print(f"🔌 {operativo}: desconectado")
            
#     except Exception as e:
#         print(f"❌ Error con {operativo}: {type(e).__name__} - {e}")

# async def main():
#     # Probar un solo operativo primero
#     await probar_conexion("operativo1")

# if __name__ == "__main__":
#     asyncio.run(main())