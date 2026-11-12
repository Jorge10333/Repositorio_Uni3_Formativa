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

# ¡Modificado! (Se agregó confirmación de contraseña, exigencia de mayúscula/número y protección try/except al guardar el JSON)
def registrar():  # Define la función que crea el usuario la primera vez
    usuario = validar(input("Crea un usuario (3-20 letras/números/_): "), r"[A-Za-z0-9_]{3,20}")  # Pide y valida el nombre de usuario
    clave = getpass.getpass("Crea una contraseña (mín. 8 caracteres, 1 mayúscula y 1 número): ")  # Pide la contraseña oculta
    confirmacion = getpass.getpass("Confirma tu contraseña: ")  # [NUEVO] Pide repetir la contraseña para evitar errores de tipeo

    if not usuario:  # Revisa si el nombre de usuario no cumplió el patrón
        print("Usuario inválido.")  # Informa que el usuario es inválido
        return False  # Cancela el registro
    if clave != confirmacion:  # [NUEVO] Compara si ambas contraseñas escritas son iguales
        print("Las contraseñas no coinciden.")  # Avisa si el usuario se equivocó al escribirla
        return False  # Cancela el registro
    if not re.fullmatch(r"(?=.*[A-Z])(?=.*\d).{8,64}", clave):  # [NUEVO] Exige mínimo 8 caracteres, al menos 1 mayúscula y 1 número
        print("La contraseña debe tener mínimo 8 caracteres, una mayúscula y un número.")  # Explica los requisitos de seguridad
        return False  # Cancela el registro

    salt = os.urandom(16)  # Genera 16 bytes aleatorios para que el hash sea único
    datos = {"usuario": usuario, "salt": salt.hex(), "hash": hashear(clave, salt)}  # Arma el diccionario con los datos cifrados

    # [PASO 3 y 4]: Se protege la escritura del archivo con try/except por si ocurre un fallo de disco o permisos
    try:
        with open(ARCHIVO, "w", encoding="utf-8") as f:  # Abre el archivo en modo escritura
            json.dump(datos, f)  # Guarda el diccionario en formato JSON
        return True  # Indica que el registro fue exitoso
    except OSError:  # Atrapa errores de sistema al intentar crear o escribir el archivo
        print("Error interno: No se pudo guardar el usuario.")  # Muestra un mensaje seguro sin exponer rutas del sistema
        return False  # Indica que el registro falló

#¡Modificado! (Se agregó manejo de errores try/except al leer usuarios.json y al validar las claves para evitar caídas si el archivo se daña)
def login():  # Define la función que verifica las credenciales del usuario
    # Pide credenciales (3 intentos) y las compara con el hash guardado
    try:
        with open(ARCHIVO, encoding="utf-8") as f:  # Abre el archivo de usuarios en modo lectura
            datos = json.load(f)  # Lee el JSON y lo convierte en diccionario
    except (OSError, json.JSONDecodeError):  # (Nuevo: atrapa errores de archivo ilegible o JSON corrupto)
        print("Error de sistema: Archivo de credenciales dañado o inaccesible.")  # Mensaje controlado sin mostrar errores técnicos
        return False  # Deniega el acceso de forma segura
    
    for _ in range(3):  # Repite el proceso hasta 3 veces (3 intentos)
        usuario = validar(input("Usuario: "), r"[A-Za-z0-9_]{3,20}") or ""  # Pide el usuario, lo valida con el patrón y, si es inválido, queda vacío
        clave = getpass.getpass("Contraseña: ")  # Pide la contraseña sin mostrarla en pantalla

        try:  # (Nuevo: protege la lectura de claves dentro del diccionario por si alteraron el archivo)
            hash_ingresado = hashear(clave, bytes.fromhex(datos["salt"]))  # Cifra la contraseña ingresada con el salt guardado
            if usuario == datos["usuario"] and hmac.compare_digest(hash_ingresado, datos["hash"]):  # Compara usuario y hash de forma segura
                return True  # Indica que el login fue correcto
        except (KeyError, ValueError):  # (Nuevo: atrapa errores si faltan datos o el salt está corrupto)
            print("Error de integridad en las credenciales.")  # Informa del problema sin detener el programa con un error rojo
            return False  # Deniega el acceso
        print("Credenciales incorrectas.")  # Avisa que el usuario o la contraseña no coinciden
    return False  # Si se agotan los 3 intentos, indica que el login falló

# ¡Modificado! (Se envolvió todo en try/except y se validó que status_code sea 200 antes de leer el JSON para que no colapse si falla la red o la API)
def consultar_clima(ciudad):  # Define la función que consulta el clima de una ciudad
    try:  # (Nuevo: atrapa cualquier fallo de conexión o respuesta de la API)
        resp_geo = requests.get(  # Hace la petición HTTP a la API de geolocalización
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": ciudad, "count": 1},
            timeout=10  # Corta la espera si tarda más de 10 segundos
        )
        if resp_geo.status_code != 200:  # (Nuevo: verifica que el código HTTP sea 200 OK antes de procesar el JSON)
            print(f"Servicio de geolocalización no disponible (HTTP {resp_geo.status_code}).")  # Muestra el código de error de forma controlada
            return  # Sale de la función sin que el programa colapse

        geo = resp_geo.json()  # Convierte la respuesta a diccionario ahora que sabemos que es válida
        if "results" not in geo or not geo["results"]:  # Revisa si la API no encontró ninguna ciudad
            print("Ciudad no encontrada.")  # Informa que la ciudad no existe
            return  # Termina la función sin consultar el clima

        lugar = geo["results"][0]  # Toma el primer resultado encontrado
        resp_clima = requests.get(  # Hace la petición HTTP a la API del clima
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lugar["latitude"],
                "longitude": lugar["longitude"],
                "current_weather": True
            },
            timeout=10  # Corta la espera a los 10 segundos
        )
        if resp_clima.status_code != 200:  # (Nuevo: valida el código HTTP de la consulta de temperatura de Open-Meteo)
            print(f"Servicio de clima no disponible (HTTP {resp_clima.status_code}).")  # Avisa si el servidor falló
            return  # Sale de la función sin errores bruscos

        clima = resp_clima.json()  # Convierte la respuesta del clima a diccionario
        print(f"{lugar['name']}: {clima['current_weather']['temperature']} °C")  # Muestra la ciudad y su temperatura actual

    except requests.exceptions.Timeout:  # (Nuevo: captura el error si la API tarda más de 10 segundos en responder)
        print("Error: Tiempo de espera agotado al conectar con el servidor.")  # Mensaje claro para el usuario
    except requests.exceptions.ConnectionError:  # (Nuevo: captura el error si se corta el internet o no hay red)
        print("Error: No hay conexión a internet o el servicio es inaccesible.")  # Evita que salga el error rojo con rutas del sistema
    except (requests.exceptions.RequestException, KeyError, ValueError):  # (Nuevo: atrapa cualquier otro error de red o respuesta malformada)
        print("Error: No se pudieron procesar los datos del clima.")  # Restringe información sensible del sistema

# Programa principal
# ¡Modificado! (Se agregó bucle while para consultar varias ciudades sin cerrar el programa, validación de archivo vacío y captura de Ctrl+C)
try:  # (Nuevo: evita que al presionar Ctrl+C se muestren rutas internas del sistema)
    if not os.path.exists(ARCHIVO) or os.path.getsize(ARCHIVO) == 0:  # (Modificado: ahora también revisa si el archivo quedó vacío con 0 bytes)
        if not registrar():  # Ejecuta el registro y revisa si falló
            raise SystemExit  # Cierra el programa si el registro falló

    if login():  # Ejecuta el login; solo si es correcto entra a este bloque
        while True:  # (Nuevo: mantiene el programa activo para consultar varias ciudades hasta escribir 'salir')
            ciudad = validar(input("\nCiudad (o escribe 'salir' para terminar): "), r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]{2,50}")  # Pide y valida la ciudad
            if not ciudad:  # Si la ciudad tiene números, símbolos o está vacía
                print("Ciudad inválida.")  # Informa que la entrada no es válida
                continue  # (Nuevo: vuelve a pedir la ciudad en lugar de cerrar el programa)
            if ciudad.lower() == "salir":  # (Nuevo: permite salir limpiamente cuando el usuario lo decida)
                print("Sesión cerrada.")  # Despide al usuario
                break  # Rompe el bucle y termina el programa
            consultar_clima(ciudad)  # Consulta y muestra el clima de la ciudad ingresada
    else:  # Si el login falló
        print("Acceso denegado.")  # Informa que no se permite el acceso

except (KeyboardInterrupt, EOFError):  # (atrapa la cancelación manual con Ctrl+C)
    print("\nEjecución cancelada de forma segura por el usuario.")  # Cierra limpiamente sin exponer trazas técnicas