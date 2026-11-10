import hashlib  # Importa la librería para cifrar (hash) la contraseña
import hmac     # Importa la librería para comparar hashes de forma segura
import json     # Importa la librería para guardar y leer datos en formato JSON
import os       # Importa la librería para generar el salt y revisar archivos
import re       # Importa la librería para validar entradas con patrones
import getpass  # Importa la librería para pedir la contraseña sin mostrarla
import requests # Importa la librería para consultar las APIs

ARCHIVO = "usuarios.json"  # Nombre del archivo donde se guarda el usuario cifrado

def hashear(clave, salt):  # Define la función que cifra una contraseña con un salt
    # Convierte la contraseña en un hash irreversible usando el salt
    return hashlib.pbkdf2_hmac("sha256", clave.encode(), salt, 200000).hex()  # Aplica PBKDF2 con SHA-256 y 200000 repeticiones, y devuelve el resultado en texto hexadecimal

def validar(texto, patron):  # Define la función que valida un texto según un patrón
    # Quita espacios y devuelve el texto solo si cumple el patrón; si no, None
    texto = texto.strip()  # Elimina los espacios al inicio y al final del texto
    return texto if re.fullmatch(patron, texto) else None  # Devuelve el texto si cumple todo el patrón; si no, devuelve None

def registrar():  # Define la función que crea el usuario la primera vez
    # Crea el usuario la primera vez y guarda su contraseña cifrada
    usuario = validar(input("Crea un usuario (3-20 letras/números/_): "), r"[A-Za-z0-9_]{3,20}")  # Pide el usuario y valida que tenga 3-20 letras, números o guion bajo
    clave = getpass.getpass("Crea una contraseña (mín. 8 caracteres): ")  # Pide la contraseña sin mostrarla en pantalla
    if not usuario or len(clave) < 8:  # Revisa si el usuario es inválido o la contraseña tiene menos de 8 caracteres
        print("Datos inválidos.")  # Informa que los datos ingresados no son válidos
        return False  # Termina la función indicando que el registro falló
    salt = os.urandom(16)  # Genera 16 bytes aleatorios para que el hash sea único
    datos = {"usuario": usuario, "salt": salt.hex(), "hash": hashear(clave, salt)}  # Arma un diccionario con el usuario, el salt y la contraseña cifrada
    with open(ARCHIVO, "w", encoding="utf-8") as f:  # Abre el archivo en modo escritura (lo cierra solo al terminar)
        json.dump(datos, f)  # Guarda el diccionario dentro del archivo en formato JSON
    return True  # Termina la función indicando que el registro fue exitoso

def login():  # Define la función que verifica las credenciales del usuario
    # Pide credenciales (3 intentos) y las compara con el hash guardado
    with open(ARCHIVO, encoding="utf-8") as f:  # Abre el archivo de usuarios en modo lectura
        datos = json.load(f)  # Lee el JSON y lo convierte en un diccionario
    for _ in range(3):  # Repite el proceso hasta 3 veces (3 intentos)
        usuario = validar(input("Usuario: "), r"[A-Za-z0-9_]{3,20}") or ""  # Pide el usuario, lo valida con el patrón y, si es inválido, queda vacío
        clave = getpass.getpass("Contraseña: ")  # Pide la contraseña sin mostrarla en pantalla
        hash_ingresado = hashear(clave, bytes.fromhex(datos["salt"]))  # Cifra la contraseña ingresada usando el salt guardado
        if usuario == datos["usuario"] and hmac.compare_digest(hash_ingresado, datos["hash"]):  # Comprueba que el usuario coincida y que los hashes sean iguales
            return True  # Termina la función indicando que el login fue correcto
        print("Credenciales incorrectas.")  # Avisa que el usuario o la contraseña no coinciden
    return False  # Si se agotan los 3 intentos, indica que el login falló

def consultar_clima(ciudad):  # Define la función que consulta el clima de una ciudad
    # Busca las coordenadas de la ciudad y luego su clima actual
    geo = requests.get("https://geocoding-api.open-meteo.com/v1/search",  # Consulta la API que convierte el nombre de la ciudad en coordenadas
                       params={"name": ciudad, "count": 1}, timeout=10).json()  # Envía la ciudad, pide 1 resultado, corta a los 10 s y convierte la respuesta a diccionario
    if "results" not in geo:  # Revisa si la API no encontró ninguna ciudad
        print("Ciudad no encontrada.")  # Informa que la ciudad no existe
        return  # Termina la función sin consultar el clima
    lugar = geo["results"][0]  # Toma el primer resultado encontrado
    clima = requests.get("https://api.open-meteo.com/v1/forecast",  # Consulta la API del clima
                         params={"latitude": lugar["latitude"], "longitude": lugar["longitude"],  # Envía la latitud y longitud de la ciudad
                                 "current_weather": True}, timeout=10).json()  # Pide el clima actual, corta a los 10 s y convierte la respuesta a diccionario
    print(f"{lugar['name']}: {clima['current_weather']['temperature']} °C")  # Muestra el nombre de la ciudad y su temperatura actual

# Programa principal
if not os.path.exists(ARCHIVO):  # Revisa si todavía no existe el archivo de usuarios
    if not registrar():  # Ejecuta el registro y revisa si falló
        raise SystemExit  # Cierra el programa si el registro falló
if login():  # Ejecuta el login; solo si es correcto entra a este bloque
    ciudad = validar(input("Ciudad: "), r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,50}")  # Pide la ciudad y valida que tenga 2-50 letras o espacios
    if ciudad:  # Revisa si la ciudad pasó la validación
        consultar_clima(ciudad)  # Consulta y muestra el clima de esa ciudad
    else:  # Si la ciudad no pasó la validación
        print("Ciudad inválida.")  # Informa que la ciudad ingresada no es válida
else:  # Si el login falló
    print("Acceso denegado.")  # Informa que no se permite el acceso