import math  # Valida que los números decimales sean finitos (rechaza nan e inf)

MONTO_MAX = 1_000_000.0  # Límite máximo permitido por operación financiera


def leer_numero(mensaje: str) -> int:  # Fuerza la lectura de un número entero válido
    while True:
        try:
            return int(input(mensaje).strip())
        except ValueError:
            print("[ERROR] Entrada inválida. Ingrese un número entero.")


def leer_float(mensaje: str) -> float:  # Fuerza la lectura de un decimal finito
    while True:
        texto = input(mensaje).strip().replace(",", ".")
        try:
            valor = float(texto)
            if math.isfinite(valor):  # Rechaza valores especiales como 'inf' o 'nan'
                return valor
        except ValueError:
            pass
        print("[ERROR] Entrada inválida. Ingrese un número decimal finito.")


def leer_monto(mensaje: str) -> float | None:  # Valida montos financieros entre >0 y MONTO_MAX
    texto = input(mensaje).strip().replace(",", ".")
    try:
        valor = float(texto)
    except ValueError:
        print("[ERROR] Ingrese un monto numérico válido (ej. 1500.50).")
        return None
    if not math.isfinite(valor) or valor <= 0 or valor > MONTO_MAX:
        print(f"[ERROR] El monto debe ser mayor que 0 y hasta {MONTO_MAX:,.0f}.")
        return None
    return valor


def leer_id_opcional(mensaje: str) -> int | None:  # Reemplaza .isdigit() evitando errores con superíndices
    texto = input(mensaje).strip()
    if not texto:
        return None  # Enter vacío significa que no se asocia ID
    try:
        valor = int(texto)
    except ValueError:
        print("[ERROR] El ID debe ser un número entero positivo.")
        return None
    if valor <= 0:
        print("[ERROR] El ID debe ser mayor que 0.")
        return None
    return valor


def confirmar(mensaje: str) -> bool:  # Solicita confirmación explícita (s/n)
    respuesta = input(f"{mensaje} (s/n): ").strip().lower()
    return respuesta == "s"