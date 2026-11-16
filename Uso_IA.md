# Registro de Uso de Inteligencia Artificial y Auditoría de Código
**Proyecto:** Sistema de Gestión EcoTech Solutions (Evaluación Unidad 3 — POO)  
**Autores:** Jorge Lagos y Sebastián San Martín  

---

## 1. Propósito y Metodología de Uso de IA
Durante el desarrollo y endurecimiento (hardening) del sistema **EcoTech Solutions**, se empleó asistencia de Inteligencia Artificial como herramienta de revisión técnica, auditoría de seguridad estática/lógica y apoyo en refactorización bajo arquitectura **MVC + DAO + Services**, siguiendo lineamientos **OWASP**.

Toda sugerencia generada por IA fue sometida a validación manual, pruebas de compilación (`py_compile`), ejecución funcional y análisis estático con **Bandit** antes de integrarse al código fuente.

---

## 2. Bitácora de Decisiones y Refactorización (Criterio 16)

| ID | Hallazgo / Problema Detectado | Archivos Afectados | Decisión Técnica y Solución Aplicada | Validación |
| :--- | :--- | :--- | :--- | :--- |
| **DEC-01** | Uso de `.isdigit()` en entradas opcionales de ID numérico (acepta caracteres Unicode como superíndices `²` o fracciones `½`, provocando fallos al castear con `int()`). | `views/empleado_view.py`, `views/departamento_view.py`, `views/utils.py` | Se creó la utilidad centralizada `leer_id_opcional()` con manejo explícito `try/except ValueError` y validación de enteros positivos, reemplazando las 4 ocurrencias de `.isdigit()`. | Búsqueda estática (`Select-String`) sin coincidencias activas y pruebas de entrada vacía/inválida. |
| **DEC-02** | Política de contraseñas débil o desalineada con estándares actuales. | `models/usuario.py`, `services/auth_service.py` | Se estandarizó la longitud válida de contraseñas entre **8 y 128 caracteres**, alineando validación en modelo, servicio y comentarios técnicos. | Pruebas unitarias de registro y cambio de clave. |
| **DEC-03** | Almacenamiento seguro de credenciales y prevención de ataques de diccionario/rainbow tables. | `models/usuario.py`, `services/auth_service.py` | Implementación de derivación de claves mediante **`hashlib.scrypt`** con `salt` criptográfico aleatorio por usuario (`os.urandom`) y comparación en tiempo constante (`hmac.compare_digest`). | Auditoría manual y verificación en base de datos SQLite. |
| **DEC-04** | Riesgo de Inyección SQL (SQLi) en consultas CRUD y filtros. | `models/*_dao.py` | Uso estricto de consultas parametrizadas (`?`) en el driver `sqlite3`, prohibiendo concatenación o f-strings en sentencias SQL. | Escaneo Bandit (0 alertas B608) y revisión manual de DAOs. |
| **DEC-05** | Imprecisión binaria en cálculos financieros y salarios (`float`). | `models/empleado.py`, `services/empleado_service.py` | Adopción del tipo **`decimal.Decimal`** para operaciones monetarias y validaciones de montos positivos. | Pruebas de cálculo salarial y persistencia. |
| **DEC-06** | Manejo genérico de errores y exposición de trazas internas al usuario final. | `exceptions.py`, `controllers/*.py` | Jerarquía de excepciones de dominio heredando de `EcoTechError` (incluyendo `ApiDatosInvalidosError`, errores de autenticación y autorización RBAC) capturadas limpiamente en controladores. | Pruebas de flujo ante entradas erróneas y fallos de red/API. |
| **DEC-07** | Control de acceso insuficiente entre roles administrativos y operativos. | `services/auth_service.py`, `controllers/*.py` | Aplicación de control de acceso basado en roles (**RBAC**), restringiendo operaciones críticas de gestión de usuarios y configuración según perfil autenticado. | Pruebas funcionales por rol. |

---

## 3. Resultados de Auditoría Estática (Bandit) y Revisión Manual

### 3.1 Análisis Automatizado (`Bandit`)
* **Ejecución inicial (`docs/bandit_antes.txt`):** Se ejecutó análisis recursivo sobre el código fuente del proyecto para detectar patrones inseguros (hardcoded passwords, `eval`/`exec`, SQL injection, uso inseguro de `random` o `pickle`).
* **Ejecución posterior (`docs/bandit_despues.txt`):** Tras aplicar las correcciones y excluir el entorno virtual (`.venv`), el escaneo final reportó **0 vulnerabilidades** (0 Low, 0 Medium, 0 High) y **0 líneas omitidas (`#nosec`)**.

### 3.2 Auditoría Lógica Manual (Complementaria a Bandit)
Dado que las herramientas SAST no detectan errores de lógica de negocio, se realizó una revisión manual asistida verificando:
1. **Ausencia de secretos hardcodeados:** Credenciales y parámetros sensibles gestionados mediante variables de entorno (`.env` excluido del paquete de entrega, provisto `.env.example`).
2. **Integridad referencial y saneamiento de entradas:** Validación en capa de vista (`views/utils.py`) y refuerzo en capa de servicio (`services/`).
3. **Resiliencia en consumo de API externa:** Manejo de timeouts y validación de esquema mediante `ApiDatosInvalidosError` al consultar indicadores económicos.

---

## 4. Evidencias de Interacción y Validación
Las capturas de respaldo del proceso de auditoría, refactorización y ejecución de pruebas se encuentran almacenadas en la carpeta `docs/evidencias_ia/`:
* `evidencia_01_arquitectura_mvc.png` — Revisión estructural de capas MVC + DAO + Services.
* `evidencia_02_seguridad_scrypt_rbac.png` — Validación de hashing `scrypt` y control de acceso RBAC.
* `evidencia_03_refactorizacion_utils.png` — Refactorización de validaciones de entrada (`leer_id_opcional`) y excepciones `EcoTechError`.
* `evidencia_04_bandit.png` — Resultado limpio de auditoría estática Bandit (0 incidencias).

---

## 5. Refactorizaciones y Justificación (Indicador 3.1.4.I.16)

### Resumen por Fases
* Fases 0-1 (Criterios 7, 13, 15): Auditoría Bandit, `.env` sin secretos y creación de admin con `getpass` para evitar credenciales fijas.
* Fase 2 (Criterio 5): `hashlib.scrypt` con sal, `hmac.compare_digest` y bloqueo persistente en SQLite contra fuerza bruta.
* Fases 3-4 (Criterios 6, 8): Validación `try/int`, ISO 4217 y guardias RBAC para restringir acceso a APIs y usuarios.
* Fases 5-6 (Criterios 1, 3, 9, 11): Filtrado JSON, excepciones tipadas por código HTTP (`4xx`/`5xx`) y bitácora en `logs/ecotech.log`.
* Fases 7-9 (Criterios 4, 12, 13-16): Cálculos con `Decimal`, bloqueo de guardado en contingencia y mensajes seguros sin trazas.

### Decisiones sobre Código Asistido (USAR, MODIFICAR, DESCARTAR)

#### 5.1. Hash de contraseñas — MODIFICAR
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

#### 5.2. Cálculos de dinero — MODIFICAR
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

#### 5.3. Errores de API — MODIFICAR
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

#### 5.4. Pagos con tasa de respaldo — DESCARTAR el guardado
* DESPUÉS:
  ```python
  if pago.origen == "contingencia":
      mostrar_error("...no se guardan en BD.")
      return
  ```
* Por qué: Una tasa antigua escrita a mano en un registro contable rompe la integridad de los datos.
* Ref.: OWASP Top 10 (A08:2021 Software and Data Integrity Failures).

#### 5.5. SQL parametrizado — USAR
* Implementación:
  ```python
  cursor.execute("... WHERE nombreUsuario = ?", (valor,))
  ```
* Por qué: El valor viaja separado de la sentencia y evita inyección SQL.
* Ref.: OWASP SQL Injection Prevention Cheat Sheet; `sqlite3`.

#### 5.6. Validación de IDs numéricos opcionales en vistas — MODIFICAR
- ANTES:
  ```python
  id_gerente = int(gerente_input) if gerente_input.isdigit() else None
-DESPUES:
id_gerente = leer_id_opcional("ID del Gerente Asignado (Enter si no aplica): ")