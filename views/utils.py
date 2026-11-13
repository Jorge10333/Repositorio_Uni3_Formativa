# Utilidades de lectura de consola reutilizables
def leer_numero(mensaje: str) -> int:
    # Fuerza la entrada de un número entero válido
    while True:
        try:
            return int(input(mensaje))
        except ValueError:
            print("❌ Entrada inválida. Por favor, ingrese un número entero.")

def leer_float(mensaje: str) -> float:
    # Fuerza la entrada de un número decimal válido
    while True:
        try:
            return float(input(mensaje))
        except ValueError:
            print("❌ Entrada inválida. Por favor, ingrese un número válido.")

def confirmar(mensaje: str) -> bool:
    # Pide confirmación binaria (s/n)
    respuesta = input(f"{mensaje} (s/n): ").strip().lower()
    return respuesta == 's'