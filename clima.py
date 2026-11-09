# Librería para hacer solicitudes HTTP a una API
import requests

# Dirección de la API de clima
url = "https://api.open-meteo.com/v1/forecast"  

params = {                      # Datos que se envían a la API en la consulta
    "latitude": -36.6,          # Latitud del lugar (Chillán)
    "longitude": -72.1,         # Longitud del lugar
    "current_weather": True,    # Pide el clima actual
}

# Hace la consulta; si tarda más de 10 s, se corta
respuesta = requests.get(url, params=params, timeout=10)

# Muestra el código de estado (200 = todo bien)
print(respuesta.status_code)  

# Convierte la respuesta JSON en un diccionario de Python
datos = respuesta.json()  

# Muestra la temperatura actual
print(datos["current_weather"]["temperature"])  


# Luego de escribir todo lo anterior. Escribo lo Siguiente en la terminal:
### pip install requests
### python clima.py