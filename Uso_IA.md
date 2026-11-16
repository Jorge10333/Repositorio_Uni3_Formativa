# Documentación de Uso Crítico de Herramientas de IA (Criterio 3.1.4)

Asignatura: Programación Orientada a Objeto Seguro  
Proyecto: EcoTech Solutions (Unidad 3)  
Integrante: Jorge Lagos y Sebastian san Martin

---

## 1. Evidencia de Prompts y Componentes Generados (Indicador 3.1.4.I.13)

### Metodología de Trabajo con IA

1. Diagnóstico inicial: Comparación del proyecto base (EF2) con los estándares de la Unidad 3 (APIs seguras, cifrado, validación y excepciones).
2. Integración de APIs: Implementación comentada de Open-Meteo y Frankfurter API con `requests.Session`, reintentos, timeouts y validación JSON.
3. Refactorización por fases: Corrección paso a paso de vulnerabilidades (scrypt, bloqueo persistente en SQLite, `getpass`, `Decimal`, RBAC y `logging`) verificada con Bandit.

---

### Registro de Interacciones con IA (Capturas en `docs/evidencias_ia/`)

#### Interacción 1 — Diagnóstico Inicial
* Fecha: 15/11/2026 | Herramienta: Google Gemini
* Prompt:
  > "para comensar con nuestro proyecto quiero que analizes el el material de estudio de la unidad 3 para definir una configuracion inicial y la evaluscion poo 2 para usarla de vase"
* Respuesta: Definió variables de entorno en `config/settings.py`, cliente HTTP y estructura RBAC sobre la base EF2.
* Archivos: `config/settings.py`, `config/logging_config.py`, `exceptions.py`, `.env.example`
* Decisión: Modificado — Eliminé valores por defecto sensibles y exigí variables obligatorias con `_requerida()`.
* Captura: [evidencia_01_diagnostico.png](docs/evidencias_ia/evidencia_01_diagnostico.png)

#### Interacción 2 — Integración de APIs
* Fecha: 15/11/2026 | Herramienta: Google Gemini
* Prompt:
  > "tomando como base a la eva poo 2 nececito que me ayudes a integrar las api de Open-Meteo y Frankfuster API, apegandoce a la estructura del ejemplo de la unidad 3 con validacion de JSON, con comentarios detallados en cada parte del codigo para entender lo que esta pasando"
* Respuesta: Entregó `http_client.py` (`Session` + `Retry` + timeouts) y los servicios comentados para Open-Meteo y Frankfurter API.
* Archivos: `services/http_client.py`, `services/clima_service.py`, `services/divisa_service.py`, `models/reporte_clima.py`, `models/pago_internacional.py`
* Decisión: Modificado — Marqué respaldos offline como `"contingencia"` y bloqueé su guardado en BD.
* Captura: [evidencia_02_apis_modelos.png](docs/evidencias_ia/evidencia_02_apis_modelos.png)

#### Interacción 3 — Correcciones por Fases
* Fecha: 15/11/2026 | Herramienta: Google Gemini
* Prompt:
  > "quiero que con las deficiencias que encontro mi compañero me ayudes a corregir el codigo paso a paso para no perderme"
* Respuesta: Ordenó las mejoras en 9 fases: `getpass`, `scrypt` con sal, `hmac.compare_digest`, bloqueo persistente en SQLite, RBAC y validación de entradas.
* Archivos: `models/usuario.py`, `models/usuario_dao.py`, `models/*_dao.py`, `controllers/seguridad.py`, `views/*.py`, `main.py`
* Decisión: Modificado — Implementé `scrypt`, estandaricé excepciones `sqlite3.Error` en los DAO y reemplacé `.isdigit()` por `try/int`.
* Captura: [evidencia_03_seguridad_dao.png](docs/evidencias_ia/evidencia_03_seguridad_dao.png)

#### Interacción 4 — Auditoría con Bandit
- Fecha: 15/11/2026 | Herramienta: Google Gemini
- Prompt:
  > "quiero que me ayudes a escaner todo el codigo en busca de errores y señalamelos, para corregirlos y comprovar con un bandit"
- Respuesta: Se ejecutó Bandit sobre la versión base (EF2) y sobre la versión refactorizada (EF3). En ambos reportes (`bandit_antes.txt` y `bandit_despues.txt`) Bandit arrojó **0 incidencias estáticas** (0 Low, 0 Medium, 0 High), ya que la base EF2 no contenía patrones inseguros detectables por AST (como `eval`, `exec` o SQL concatenado). Sin embargo, la auditoría lógica asistida sí identificó 16 vulnerabilidades de diseño y seguridad de negocio (uso de `SHA-256` sin sal, secreto inicial en código, falta de RBAC, cálculos con `float` y uso de `.isdigit()`), las cuales fueron corregidas y verificadas manteniendo 0 alertas en Bandit.
- Archivos: `docs/bandit_antes.txt`, `docs/bandit_despues.txt`, `Uso_IA.md`, `README.md`
- Decisión: Usado — Adjunté ambos reportes reales en `docs/` y documenté los 16 hallazgos lógicos/arquitectónicos en la Sección 3.2.
- Captura: [evidencia_04_bandit.png](docs/evidencias_ia/evidencia_04_bandit.png)

---

## 2. Análisis Técnico del Código (Indicador 3.1.4.I.14)

### 2.1. `config/settings.py`
* Función: Carga variables desde `.env` (`load_dotenv()`) y valida las obligatorias con `_requerida()`.
* Dependencias: `os`, `python-dotenv`.
* Fallo: Detiene el arranque con error claro si falta una URL o parámetro obligatorio.

### 2.2. `services/http_client.py`
* Función: Centraliza peticiones HTTP con `requests.Session`, reintentos (`Retry` en 429/5xx para `GET`) y timeout `(3.05, timeout)`.
* Dependencias: `requests`, `urllib3`, `exceptions.py`.
* Fallo: Convierte errores de red, JSON inválido o códigos `4xx`/`5xx` en excepciones propias, usando una única `requests.Session` compartida (no `requests.get`) (`ApiTimeoutError`, `ApiConexionError`, `ApiHttpError`, `ApiDatosInvalidosError`).

### 2.3. `services/clima_service.py` y `services/divisa_service.py`
* Función: Consumen `obtener_json()`. Clima geocodifica la ciudad y extrae temperatura, humedad, viento y `weather_code`; divisas valida ISO 4217 y obtiene la tasa en Frankfurter API.
* Dependencias: `http_client.py`, `reporte_clima.py`, `pago_internacional.py`, `settings.py`, `exceptions.py`.
* Fallo: Activan respaldo marcado como `origen = "contingencia"` y registran el fallo en el log.

### 2.4. `models/reporte_clima.py` y `models/pago_internacional.py`
* Función: Validan rangos físicos y finitud (`math.isfinite()`), generan alertas climáticas (`evaluar_condiciones()`) y calculan divisas con `Decimal` (`ROUND_HALF_UP`).
* Dependencias: `decimal`, `math`, `re`, `exceptions.py`.
* Fallo: Rechazan `NaN`, `Inf` o valores fuera de rango lanzando `ValidacionError`.

### 2.5. `models/usuario.py`, `controllers/seguridad.py` y `models/usuario_dao.py`
* Función: Cifran claves con `hashlib.scrypt` + sal de 16 bytes, comparan con `hmac.compare_digest()`, exigen sesión/rol (`exigir_sesion`, `exigir_rol`) y ejecutan SQL parametrizado (`?`) en SQLite.
* Dependencias: `hashlib`, `hmac`, `os`, `sqlite3`, `datetime`, `logging`, `database.py`.
* Fallo: Bloquean la cuenta por 5 minutos tras 3 intentos fallidos (persistido en BD) y capturan `sqlite3.Error` sin exponer trazas.

### 2.6. `exceptions.py`, `config/logging_config.py` y `main.py`
* Función: Separan excepciones de negocio (`EcoTechError`) de detalles técnicos guardados en `logs/ecotech.log` mediante `RotatingFileHandler`.
* Dependencias: `logging`, `main_controller.py`, `seguridad.py`, `getpass`.
* Fallo: `main.py` captura `KeyboardInterrupt`, `EOFError` y errores inesperados cerrando de forma segura.

### 2.7. Dependencias
* Externas: `requests` (sesiones HTTP), `urllib3` (reintentos `Retry`), `python-dotenv` (lectura `.env`).
* Estándar: `hashlib`/`hmac` (scrypt), `decimal`/`math` (cálculo exacto), `sqlite3` (BD), `logging` (bitácora), `re`/`getpass` (validación y lectura oculta).

---

## 3. Hallazgos y Auditoría Estática (Indicador 3.1.4.I.15)

### 3.1. Resultados Bandit
### 3.1. Resultados Bandit
- Antes: [`docs/bandit_antes.txt`](docs/bandit_antes.txt) (0 incidencias estáticas en la base EF2; los problemas de la versión inicial eran de lógica de seguridad, detallados en 3.2).
- Después: [`docs/bandit_despues.txt`](docs/bandit_despues.txt) (0 vulnerabilidades detectadas tras aplicar las 16 correcciones).

### 3.2. Hallazgos Corregidos

1. Contraseña `admin1234` en código y pantalla (`settings.py` l.24, `auth_view.py` l.16) — Riesgo: Alto — Corregido con `.env` y `getpass`.
2. Hash `SHA-256` sin sal y clave de 4 caracteres (`usuario.py` l.69-91) — Riesgo: Alto — Corregido con `scrypt` + sal y política de 8-128 caracteres.
3. Gestión de usuarios sin RBAC (`main_controller.py` l.34-35) — Riesgo: Alto — Corregido con `exigir_rol("Administrador")`.
4. Controladores permitían `usuario=None` (`clima_controller.py` l.17, `pago_controller.py` l.18) — Riesgo: Medio — Corregido con `exigir_sesion`.
5. Bloqueo de intentos solo en RAM (`auth_controller.py` l.15-47) — Riesgo: Medio — Corregido persistiendo bloqueo en SQLite.
6. Aceptación de `nan` e `inf` en montos (`pago_view.py` l.49-52) — Riesgo: Medio — Corregido con `math.isfinite()` y `Decimal`.
7. Uso de `.isdigit()` + `int()` vulnerable a Unicode (`auth_view.py`, `pago_view.py`, `clima_view.py`, `empleado_view.py` l.34 y 93, `departamento_view.py` l.27 y 65) — Riesgo: Medio — Corregido con `try/int` y la función `leer_id_opcional()` (`views/utils.py` l.39).
8. Respaldos offline guardados como reales en BD (`divisa_service.py` l.129, `clima_service.py` l.128) — Riesgo: Alto — Corregido etiquetando `"contingencia"` y bloqueando guardado.
9. `except Exception` y `{e}` mostrados en consola (`controllers/`, `services/`, `*_dao.py`) — Riesgo: Medio — Corregido con jerarquía `EcoTechError` y `logging`.
10. Códigos HTTP sin diferenciar `4xx`/`5xx` (`clima_service.py`, `divisa_service.py`) — Riesgo: Medio — Corregido en `http_client.py`.
11. Clima sin humedad ni estado meteorológico (`clima_service.py` l.94-99) — Riesgo: Medio — Corregido extrayendo todos los campos requeridos.
12. Cálculos financieros con `float` (`pago_internacional.py`) — Riesgo: Medio — Corregido con `Decimal` (`ROUND_HALF_UP`).
13. Servicios retornaban tuplas `(dato, mensaje)` (`clima_service.py`, `divisa_service.py`) — Riesgo: Medio — Corregido retornando objetos o lanzando excepciones.
14. Peticiones HTTP sin `Session` y cabeceras duplicadas (`clima_service.py`, `divisa_service.py`) — Riesgo: Bajo — Corregido con `Session` compartida y `Retry`.
15. Arquitectura: los controladores de empleado, departamento, proyecto y registro_tiempo (`controllers/empleado_controller.py` l.10-33, entre otros) no reciben sesión ni rol; el control de acceso queda solo en el menú principal (`main_controller.py`) — Riesgo: Medio — Mitigado por el RBAC del menú; mejora propuesta: pasar `usuario` a cada subcontrolador y usar `exigir_rol`.
16. Optimización: cada servicio abría su propia conexión HTTP sin reutilización ni reintentos (`clima_service.py`, `divisa_service.py`) — Riesgo: Bajo — Corregido centralizando en `services/http_client.py` l.16-26 (`Session` compartida + `Retry` con backoff).

---

## 4. Refactorizaciones y Justificación (Indicador 3.1.4.I.16)

### Resumen por Fases
* Fases 0-1 (Criterios 7, 13, 15): Auditoría Bandit, `.env` sin secretos y creación de admin con `getpass` para evitar credenciales fijas.
* Fase 2 (Criterio 5): `hashlib.scrypt` con sal, `hmac.compare_digest` y bloqueo persistente en SQLite contra fuerza bruta.
* Fases 3-4 (Criterios 6, 8): Validación `try/int`, ISO 4217 y guardias RBAC para restringir acceso a APIs y usuarios.
* Fases 5-6 (Criterios 1, 3, 9, 11): Filtrado JSON, excepciones tipadas por código HTTP (`4xx`/`5xx`) y bitácora en `logs/ecotech.log`.
* Fases 7-9 (Criterios 4, 12, 13-16): Cálculos con `Decimal`, bloqueo de guardado en contingencia y mensajes seguros sin trazas.

### Decisiones sobre Código Asistido (USAR, MODIFICAR, DESCARTAR)

#### 4.1. Hash de contraseñas — MODIFICAR
* ANTES:
  ```python
  return hashlib.sha256(clave_limpia.encode("utf-8")).hexdigest()
  ```
* DESPUÉS:
  ```python
  digest = hashlib.scrypt(clave.encode("utf-8"), salt=os.urandom(16), n=2**14, r=8, p=1, dklen=32)
  ```
* Por qué: SHA-256 es rápido y sin sal (hashes iguales para claves iguales); scrypt exige memoria/tiempo y la sal hace único cada hash.
* Ref.: OWASP Password Storage Cheat Sheet; `hashlib.scrypt`.

#### 4.2. Cálculos de dinero — MODIFICAR
* ANTES:
  ```python
  round(self._monto_base * self._tasa_cambio, 2)
  ```
* DESPUÉS:
  ```python
  (Decimal(str(monto)) * Decimal(str(tasa))).quantize(cuanto, rounding=ROUND_HALF_UP)
  ```
* Por qué: `float` no representa decimales exactos; `Decimal` da resultados contables previsibles.
* Ref.: Documentación oficial de Python — Módulo `decimal`.

#### 4.3. Errores de API — MODIFICAR
* ANTES:
  ```python
  return (None, "", f"Servicio no disponible (HTTP {respuesta.status_code}).")
  ```
* DESPUÉS:
  ```python
  raise ApiHttpError(resp.status_code, "El servicio externo no está disponible por ahora.")
  ```
* Por qué: Separa éxito y fallo, permite capturar por tipo y registrar el detalle en el log.
* Ref.: OWASP Top 10 (A09:2021 Security Logging and Monitoring Failures).

#### 4.4. Pagos con tasa de respaldo — DESCARTAR el guardado
* DESPUÉS:
  ```python
  if pago.origen == "contingencia":
      mostrar_error("...no se guardan en BD.")
      return
  ```
* Por qué: Una tasa antigua escrita a mano en un registro contable rompe la integridad de los datos.
* Ref.: OWASP Top 10 (A08:2021 Software and Data Integrity Failures).

#### 4.5. SQL parametrizado — USAR
* Implementación:
  ```python
  cursor.execute("... WHERE nombreUsuario = ?", (valor,))
  ```
* Por qué: El valor viaja separado de la sentencia y evita inyección SQL.
* Ref.: OWASP SQL Injection Prevention Cheat Sheet; `sqlite3`.

#### 4.6. Validación de IDs opcionales en vistas — MODIFICAR
* ANTES:
  ```python
  id_gerente = int(gerente_input) if gerente_input.isdigit() else None
  ```
* DESPUÉS:
  ```python
  id_gerente = leer_id_opcional("ID del Gerente Asignado (Enter si no aplica): ")
  ```
* Por qué: `.isdigit()` acepta caracteres Unicode (por ejemplo `²`) que hacen fallar `int()`; `leer_id_opcional()` usa `try/except ValueError` y exige un entero positivo.
* Ref.: Documentación oficial de Python — `str.isdigit()` y `int()`.
