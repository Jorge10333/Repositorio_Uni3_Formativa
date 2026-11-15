# Documentación de Uso Crítico de Herramientas de IA (Criterio 3.1.4)

**Asignatura:** TI3021 — Programación Orientada a Objeto Seguro  
**Proyecto:** EcoTech Solutions (Unidad 3)  
**Integrantes:** Jorge Lagos, Sebastian San Martin.

---

## 1. Evidencia de Prompts y Componentes Generados (Indicador 3.1.4.I.13)

| Etapa | Prompt / Solicitud Realizada a la IA | Componente / Archivo Generado |
| :--- | :--- | :--- |
| **1. Integración de APIs (Ejemplo Unidad 3)** | *"Ayúdame a integrar las APIs de clima y divisas apegándonos al ejemplo de la Unidad 3 (usando `requests.get`, `timeout`, validación de respuestas JSON y excepciones)."* | `services/clima_service.py`, `services/divisa_service.py`, `exceptions.py` |
| **2. Configuración y Persistencia** | *"Organiza las variables externas en `.env`, la conexión Singleton a SQLite y el registro de errores en archivo log."* | `config/settings.py`, `config/database.py`, `config/logging_config.py` |
| **3. Seguridad y Autenticación** | *"Mejora la seguridad de usuarios reemplazando SHA-256 por `scrypt` con sal, bloqueo persistente en SQLite y creación inicial del administrador con contraseña oculta."* | `models/usuario.py`, `models/usuario_dao.py`, `controllers/seguridad.py`, `controllers/auth_controller.py` |
| **4. Precisión Financiera y Vistas** | *"Asegura cálculos monetarios exactos con `Decimal`, validación de números y lectura oculta con `getpass` en consola."* | `models/pago_internacional.py`, `views/utils.py`, `views/auth_view.py`, `views/clima_view.py`, `views/pago_view.py` |

---

## 2. Análisis Técnico del Funcionamiento del Código (Indicador 3.1.4.I.14)

1. **Consumo de APIs Externas (`services/clima_service.py` y `services/divisa_service.py`):**
   * Siguiendo el esquema de la Unidad 3, cada servicio realiza peticiones HTTP con `requests.get(url, params=..., timeout=...)` evitando esperas indefinidas si un servidor externo no responde.
   * **Open-Meteo:** Consulta primero las coordenadas de la ciudad mediante geocodificación y luego obtiene el clima actual extrayendo únicamente temperatura, humedad, velocidad del viento y código meteorológico desde el diccionario JSON.
   * **Frankfurter API:** Consulta la tasa de cambio entre monedas ISO 4217, verifica que la respuesta JSON contenga una tasa numérica válida y positiva, y ante fallos de red activa un modo de contingencia referencial.

2. **Autenticación Criptográfica y Control de Acceso (`models/usuario.py` y `controllers/seguridad.py`):**
   * `encriptar_credencial()` genera 16 bytes aleatorios (`os.urandom(16)`) como sal única y deriva el hash con `hashlib.scrypt()`, guardándolo en formato `scrypt$<sal_hex>$<digest_hex>`.
   * `verificar_credencial()` valida la contraseña usando `hmac.compare_digest()` para prevenir ataques de temporización (*timing attacks*).
   * Los guardias `exigir_sesion()` y `exigir_rol()` verifican antes de cada operación en los controladores que exista sesión activa, que la cuenta no esté bloqueada y que el rol tenga permiso.

---

## 3. Auditoría de Vulnerabilidades y Análisis Estático (Indicador 3.1.4.I.15)

Durante la revisión del código y el análisis estático con **Bandit** (`bandit -r . -x ./.venv`), se detectaron y corrigieron las siguientes vulnerabilidades:

1. **Hash criptográfico débil (`SHA-256` sin sal):** Vulnerable a tablas arcoíris y fuerza bruta.
2. **Credenciales fijas expuestas:** Existían contraseñas de prueba en el código / `.env.example`.
3. **Bloqueo de intentos solo en memoria (RAM):** Al cerrar `main.py` se perdía el conteo de intentos fallidos.
4. **Uso inseguro de `.isdigit()` en validaciones:** Caracteres Unicode como `"²"` devolvían `True` y provocaban errores al convertir a entero.
5. **Imprecisión financiera con `float` y valores `NaN`/`Inf`:** Riesgo de redondeos incorrectos en montos monetarios y aceptación de números no finitos.
6. **Guardado de tasas de contingencia en BD:** El flujo inicial permitía guardar pagos calculados sin conexión usando tasas referenciales.
7. **Captura genérica `except Exception:`:** Mezclaba errores de red con errores internos del programa.

---

## 4. Refactorizaciones Aplicadas y Justificación Técnica (Indicador 3.1.4.I.16)

| Hallazgo Detectado | Refactorización Implementada | Justificación de Ingeniería de Software |
| :--- | :--- | :--- |
| `SHA-256` sin sal | Migración a `hashlib.scrypt` con sal aleatoria de 16 bytes por usuario y `hmac.compare_digest`. | Función resistente a fuerza bruta por hardware que garantiza hashes únicos por usuario. |
| Contraseñas en duro y entrada visible | Eliminación de claves en `.env.example`, creación interactiva del `Administrador` inicial y lectura con `getpass.getpass()`. | Evita exponer credenciales en el repositorio o en pantalla durante el ingreso. |
| Bloqueo volátil en RAM | Columnas `intentos_fallidos` y `bloqueado_hasta` persistidas en SQLite. | Mantiene el bloqueo de 5 minutos tras 3 intentos fallidos incluso si se reinicia la aplicación. |
| Uso de `.isdigit()` | Conversión controlada `int(texto)` dentro de `try/except ValueError` con validación `valor > 0`. | Asegura que solo se acepten números enteros positivos válidos sin falsos positivos Unicode. |
| `float` en dinero y `NaN`/`Inf` | Validación `math.isfinite()` en entradas y cálculo monetario con `decimal.Decimal` (`ROUND_HALF_UP`). | Garantiza exactitud contable y rechaza valores numéricos inválidos. |
| Guardado de tasas offline en BD | Bloqueo en `PagoController` cuando el origen del cálculo es `"contingencia"`. | Permite consultar valores referenciales sin internet sin contaminar los registros contables en SQLite. |
| `except Exception:` genérico | Excepciones específicas en `exceptions.py` (`ApiTimeoutError`, `ApiConexionError`, `ApiHttpError`, `ValidacionError`, `AccesoDenegadoError`) y registro en `logs/ecotech.log`. | Permite manejar cada error de forma controlada y mostrar mensajes claros sin exponer detalles técnicos. |