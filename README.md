# EcoTech Solutions - Sistema de Gestión Segura y Consumo de APIs (Unidad 3)

Asignatura: TI3021 Programación Orientada a Objeto Seguro

Integrantes: Jorge Lagos, Sebastian San Martin.

## Descripción
Sistema de gestión interna en Python para EcoTech Solutions bajo arquitectura **MVC + DAO + Singleton** con persistencia en **SQLite**, autenticación segura con `scrypt`, control de acceso por roles (RBAC) e integración resiliente con **Open-Meteo** (clima en terreno) y **Frankfurter API** (pagos internacionales).

## Estructura
- `models/`: entidades y DAOs (`usuario`, `empleado`, `departamento`, `proyecto`, `empleado_proyecto`, `registro_tiempo`, `reporte_clima`, `pago_internacional`)
- `services/`: cliente HTTP con `Session`, *timeouts* y reintentos (`http_client.py`), clima (`clima_service.py`) y divisas (`divisa_service.py`)
- `controllers/`: guardias RBAC (`seguridad.py`) y controladores de autenticación, entidades, clima y pagos
- `views/`: interfaz de consola, lectura oculta con `getpass` y validación estricta de entradas
- `config/`: variables de entorno (`settings.py`), conexión Singleton SQLite (`database.py`) y bitácora (`logging_config.py`)
- `exceptions.py` / `main.py`: jerarquía de excepciones personalizadas y punto de entrada

## Seguridad, APIs y POO aplicada
- **Autenticación y RBAC:** hash `scrypt` con sal aleatoria de 16 bytes, comparación `hmac.compare_digest`, bloqueo persistente en SQLite (3 intentos / 5 min) y permisos por rol (`Administrador`, `Gerente`, `Empleado`, `Operador`).
- **Consumo de APIs:** consultas parametrizadas a Open-Meteo y Frankfurter API v2 con filtrado JSON, aritmética `Decimal` y modo contingencia ante caídas de red.
- **Manejo de Errores:** captura granular (`ApiTimeoutError`, `ApiConexionError`, `ApiHttpError`, `ValidacionError`, `AccesoDenegadoError`) con registro en `logs/ecotech.log`.

## Cómo ejecutar
1. Crear entorno e instalar dependencias:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt

   copy .env.example .env
   python main.py