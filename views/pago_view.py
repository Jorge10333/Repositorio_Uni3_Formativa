from views.utils import leer_numero, leer_monto, leer_id_opcional, confirmar
from models.pago_internacional import PagoInternacional


class PagoView:  # Interfaz de consola para Pagos Internacionales y Divisas
    @staticmethod
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
        return leer_numero("Seleccione una opción: ")

    @staticmethod
    def pedir_par_monedas() -> tuple[str, str]:
        print("\n--- CONSULTA DE TIPO DE CAMBIO (ISO 4217) ---")
        origen = input("Moneda base/origen (ej. USD, EUR): ").strip().upper()
        destino = input("Moneda destino (ej. CLP, BRL, MXN, EUR): ").strip().upper()
        return (origen, destino)

    @staticmethod
    def formulario_pago_internacional(sugerir_fn) -> dict | None:
        print("\n--- CÁLCULO DE PAGO INTERNACIONAL ---")
        pais = input("País donde se ejecuta el proyecto (ej. Chile, Brasil, España): ").strip()
        if not pais:
            print("[ERROR] Debe indicar el país del proyecto.")
            return None

        moneda_origen = input("Moneda base del contrato (Enter para 'USD'): ").strip().upper() or "USD"
        sugerida = sugerir_fn(pais)
        if sugerida:
            moneda_destino = input(f"Moneda destino (Enter para '{sugerida}'): ").strip().upper() or sugerida
        else:
            moneda_destino = input("Moneda destino ISO (ej. CLP, EUR, BRL, MXN): ").strip().upper()

        monto_base = leer_monto(f"Monto base a pagar en {moneda_origen} (ej. 1500.50): ")
        if monto_base is None:
            return None

        id_empleado = leer_id_opcional("ID del empleado beneficiario (opcional, Enter para omitir): ")
        id_proyecto = leer_id_opcional("ID del proyecto asociado (opcional, Enter para omitir): ")

        return {
            "pais_proyecto": pais,
            "moneda_origen": moneda_origen,
            "moneda_destino": moneda_destino,
            "monto_base": monto_base,
            "id_empleado": id_empleado,
            "id_proyecto": id_proyecto,
        }

    @staticmethod
    def mostrar_detalle_conversion(pago: PagoInternacional) -> None:
        print("\n" + "-" * 54)
        print(f"  Origen Dato       : {pago.origen.upper()}")
        print(f"  País del Proyecto : {pago.pais_proyecto}")
        print(f"  Monto Base        : {pago.monto_base:,.2f} {pago.moneda_origen}")
        print(f"  Tasa Aplicada     : 1 {pago.moneda_origen} = {pago.tasa_cambio:.4f} {pago.moneda_destino}")
        print(f"  Fecha de Tasa     : {pago.fecha_tasa or 'No disponible (referencial)'}")
        print(f"  TOTAL A PAGAR     : {pago.monto_convertido:,.2f} {pago.moneda_destino}")
        print("-" * 54)

    @staticmethod
    def confirmar_guardado() -> bool:
        return confirmar("¿Desea guardar este cálculo de pago internacional en la base de datos?")

    @staticmethod
    def mostrar_historial(pagos: list[PagoInternacional]) -> None:
        if not pagos:
            print("\n[INFO] No hay pagos internacionales registrados.")
            return
        print(f"\n--- HISTORIAL DE PAGOS INTERNACIONALES ({len(pagos)}) ---")
        for p in pagos:
            print(f"• {p}")
        print("-" * 58)

    @staticmethod
    def mostrar_mensaje(mensaje: str) -> None:
        print(f"\n[DIVISAS] {mensaje}")

    @staticmethod
    def mostrar_error(error: str) -> None:
        print(f"\n[ERROR DIVISAS] {error}")