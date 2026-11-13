from views.utils import leer_numero, confirmar  # Importa utilidades de lectura numérica y confirmación
from models.pago_internacional import PagoInternacional  # Importa el modelo PagoInternacional


class PagoView:  # Define la vista de consola para pagos internacionales y divisas
    """
    Vista de consola para el cálculo y gestión de pagos internacionales.
    """

    @staticmethod  # Muestra el menú principal del módulo de pagos internacionales
    def mostrar_menu() -> int:
        print("\n" + "=" * 58)
        print("   MÓDULO DE PAGOS INTERNACIONALES Y DIVISAS (FRANKFURTER)")
        print("=" * 58)
        print("1.- Consultar Tipo de Cambio Actual entre Dos Monedas")
        print("2.- Calcular y Guardar Pago Internacional de Trabajador")
        print("3.- Ver Historial de Pagos Internacionales Guardados")
        print("4.- Diagnosticar Conexión con Frankfurter API")
        print("0.- Volver al Menú Principal")
        print("=" * 58)
        return leer_numero("Seleccione una opción: ")  # Lee y valida opción numérica

    @staticmethod  # Solicita moneda origen y moneda destino para consulta rápida
    def pedir_par_monedas() -> tuple[str, str]:
        print("\n--- CONSULTA DE TIPO DE CAMBIO (ISO 4217) ---")
        origen = input("Moneda base/origen (ej. USD, EUR): ").strip().upper()
        destino = input("Moneda destino (ej. CLP, BRL, MXN, EUR): ").strip().upper()
        return (origen, destino)  # Retorna ambas monedas en mayúsculas

    @staticmethod  # Solicita los datos necesarios para calcular el pago internacional
    def formulario_pago_internacional(sugerir_fn) -> dict | None:
        print("\n--- CÁLCULO DE PAGO INTERNACIONAL ---")
        pais = input("País donde se ejecuta el proyecto (ej. Chile, Brasil, España): ").strip()
        if not pais:  # Valida que el país no venga vacío
            print("[ERROR] Debe indicar el país del proyecto.")
            return None

        moneda_origen = input("Moneda base del contrato (presione Enter para 'USD'): ").strip().upper() or "USD"

        # Sugiere automáticamente la moneda oficial del país si está en el catálogo
        sugerida = sugerir_fn(pais)
        if sugerida:
            moneda_destino = input(f"Moneda destino (presione Enter para '{sugerida}'): ").strip().upper() or sugerida
        else:
            moneda_destino = input("Moneda destino ISO (ej. CLP, EUR, BRL, MXN): ").strip().upper()

        monto_str = input(f"Monto base a pagar en {moneda_origen} (ej. 1500.50): ").strip()
        try:  # Convierte el texto ingresado a número decimal
            monto_base = float(monto_str)
            if monto_base <= 0:  # Rechaza valores negativos o cero
                print("[ERROR] El monto debe ser mayor a 0.")
                return None
        except ValueError:  # Captura si escribió letras en vez de un número
            print("[ERROR] Debe ingresar un monto numérico válido.")
            return None

        emp_raw = input("ID del empleado beneficiario (opcional, Enter para omitir): ").strip()
        id_empleado = int(emp_raw) if emp_raw.isdigit() else None  # Convierte a entero solo si son dígitos

        proy_raw = input("ID del proyecto asociado (opcional, Enter para omitir): ").strip()
        id_proyecto = int(proy_raw) if proy_raw.isdigit() else None  # Convierte a entero solo si son dígitos

        return {  # Retorna todos los datos limpios en un diccionario
            "pais_proyecto": pais,
            "moneda_origen": moneda_origen,
            "moneda_destino": moneda_destino,
            "monto_base": monto_base,
            "id_empleado": id_empleado,
            "id_proyecto": id_proyecto
        }

    @staticmethod  # Muestra en pantalla el detalle de la conversión realizada
    def mostrar_detalle_conversion(pago: PagoInternacional) -> None:
        print("\n" + "-" * 54)
        print(f"  País del Proyecto : {pago.pais_proyecto}")
        print(f"  Monto Base        : {pago.monto_base:,.2f} {pago.moneda_origen}")
        print(f"  Tasa Aplicada     : 1 {pago.moneda_origen} = {pago.tasa_cambio:.4f} {pago.moneda_destino}")
        print(f"  Fecha de Tasa     : {pago.fecha_tasa}")
        print(f"  TOTAL A PAGAR     : {pago.monto_convertido:,.2f} {pago.moneda_destino}")
        print("-" * 54)

    @staticmethod  # Pide confirmación antes de guardar el pago en SQLite
    def confirmar_guardado() -> bool:
        return confirmar("¿Desea guardar este cálculo de pago internacional en la base de datos?")

    @staticmethod  # Muestra la lista histórica de pagos registrados
    def mostrar_historial(pagos: list[PagoInternacional]) -> None:
        if not pagos:  # Si no hay registros en SQLite
            print("\n[INFO] No hay pagos internacionales registrados.")
            return
        print(f"\n--- HISTORIAL DE PAGOS INTERNACIONALES ({len(pagos)}) ---")
        for p in pagos:  # Imprime cada objeto PagoInternacional usando su __str__
            print(f"• {p}")
        print("-" * 58)

    @staticmethod  # Muestra mensajes informativos del módulo
    def mostrar_mensaje(mensaje: str) -> None:
        print(f"\n[DIVISAS] {mensaje}")

    @staticmethod  # Muestra mensajes de error controlados del módulo
    def mostrar_error(error: str) -> None:
        print(f"\n[ERROR DIVISAS] {error}")