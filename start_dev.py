# start_dev.py
import logging
import os
import subprocess
import threading
import time
from ngrok import ngrok

# --- Configuración ---
DJANGO_PORT = 8000
logger = logging.getLogger(__name__)

# Función para iniciar el servidor de Django en un hilo separado
def start_django():
    """Ejecuta 'python manage.py runserver 8000'."""
    try:
        logger.info("Iniciando servidor de Django en el puerto %s...", DJANGO_PORT)
        subprocess.run(
            ["python", "manage.py", "runserver", str(DJANGO_PORT)], 
            # ⭐ MODIFICACIÓN: Usamos check=False para que el script no muera
            # y eliminamos PIPE para que la salida de Django sea visible en la consola.
            check=False
        )
    except FileNotFoundError:
        logger.error("Error: Asegúrate de que Python esté en tu PATH.")

# --- Lógica principal ---
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # ⭐ MODIFICACIÓN: Autenticación de ngrok usando tu token
    NGROK_AUTH_TOKEN = "34lhnMzFahkQLOMzD8iVNP0w0IZ_4WTPRhiVu7DUZBLBJZbV7"
    try:
        ngrok.set_auth_token(NGROK_AUTH_TOKEN)
    except Exception as e:
        logger.error("Error al establecer el Authtoken: %s", e)
        sys.exit(1) # Detener si la autenticación falla
    
    # 1. Iniciar Django en un hilo de fondo (thread)
    django_thread = threading.Thread(target=start_django, daemon=True)
    django_thread.start()

    # Dar tiempo a Django para que inicie (crítico)
    time.sleep(3) 
    
    # 2. Iniciar el túnel ngrok
    try:
        tunnel = ngrok.connect(DJANGO_PORT)
        
        # Obtener y mostrar la URL de ngrok
        public_url = tunnel.url()
        logger.info("🎉 Aplicación Django en línea (ngrok): %s", public_url)
        logger.info("Presiona Ctrl+C para detener ambos servidores.")
        
        # Mantener el hilo principal vivo mientras Django y ngrok se ejecutan
        while django_thread.is_alive():
            time.sleep(1)
            
    except Exception as e:
        logger.error("Fallo al conectar ngrok: %s. ¿Está ngrok instalado y autenticado?", e)
    finally:
        # 3. Detener ngrok y asegurar el cierre de Django
        logger.info("Deteniendo ngrok y servidor de Django...")
        ngrok.kill()
        logger.info("Servidor detenido.")