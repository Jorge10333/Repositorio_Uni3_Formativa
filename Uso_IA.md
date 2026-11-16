# Documentación de Uso Crítico de Herramientas de IA (Criterio 3.1.4)

**Asignatura:** TI3021 — Programación Orientada a Objeto Seguro  
**Proyecto:** EcoTech Solutions (Unidad 3)  
**Integrantes:** Jorge Lagos, Sebastian San Martin.

---

## 1. Evidencia de Prompts y Componentes Generados (Indicador 3.1.4.I.13)

## Proceso de Colaboración con IA y Metodología de Trabajo

En el desarrollo de esta entrega (Unidad 3), la Inteligencia Artificial se utilizó como apoyo estructural y de aprendizaje guiado, siguiendo estas etapas:

1. **Diagnóstico inicial y alineación con la Unidad 3:**  
   Lo primero que se solicitó a la IA fue analizar nuestro proyecto base de la entrega anterior (EF2) y compararlo con los contenidos y estándares de la Unidad 3 (consumo seguro de APIs, cifrado de credenciales, validación de entradas y manejo de excepciones) para identificar qué módulos debíamos incorporar.

2. **Integración guiada de las APIs externas (`Open-Meteo` y `Frankfurter API`):**  
   Una vez seleccionada la API del clima (**Open-Meteo**), se pidió ayuda para integrarla respetando exactamente la estructura enseñada en la Unidad 3 (`requests.get`, *timeouts*, validación de JSON y bloques `try/except`), solicitando además comentarios y anotaciones detalladas en el código para comprender cada paso. Posteriormente, se replicó este mismo enfoque estructurado y comentado para integrar la segunda API de divisas (**Frankfurter API**).

3. **Iteración, corrección de errores y reconstrucción desde la base:**  
   Tras revisar el avance junto a mi compañero, elaboramos un listado de mejoras técnicas y de seguridad pendientes (reemplazar `SHA-256` por `scrypt` con sal, persistir el bloqueo de intentos fallidos en SQLite, ocultar contraseñas con `getpass`, usar `Decimal` en cálculos financieros y separar excepciones). En un primer intento de integración surgieron fallos de acoplamiento en el código, por lo que decidimos volver a partir desde la base limpia del proyecto e ir aplicando y probando cada mejora paso a paso hasta completar y auditar todo el sistema con Bandit.

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

## 3. Revisión por Rúbrica, Diagnóstico Inicial y Análisis Estático (Indicador 3.1.4.I.15)

Dado que cada módulo fue revisado y validado previamente con apoyo de IA antes de editar el código fuente, el análisis estático ejecutado con **Bandit** (`bandit -r . -x ./.venv`) **no arrojó vulnerabilidades ni alertas activas** en el repositorio. Sin embargo, al auditar la línea base del proyecto frente a los 16 indicadores de la rúbrica, se detectó una puntuación inicial de **60/100 puntos** (con insuficiencias en seguridad, validaciones, excepciones y ausencia de documentación de IA), identificándose las siguientes brechas a corregir:

1. **Criterios en nivel Elemental (3,6 pts — Indicadores 5 y 7):** El sistema utilizaba `SHA-256` sin sal para contraseñas, mantenía bloqueo de intentos solo en memoria RAM y exponía credenciales de ejemplo en `.env.example` junto con lectura visible en consola.
2. **Criterios en nivel Competente (4,8 a 5,6 pts — Indicadores 1, 3, 4, 6, 8, 9, 11 y 12):** Se detectaron oportunidades de mejora en la validación de entradas numéricas (`.isdigit()` vulnerable a caracteres Unicode), precisión financiera con `float`, persistencia de tasas de contingencia sin conexión, manejo genérico de excepciones y diferenciación de códigos de estado HTTP.
3. **Criterios en nivel Ausente (0/25 pts — Indicadores 13, 14, 15 y 16):** Faltaba la documentación formal del uso crítico de herramientas de IA, el análisis técnico del código asistido, el registro de correcciones y la justificación de refactorizaciones.

---

## 4. Refactorizaciones Aplicadas por Fases y Justificación Técnica (Indicador 3.1.4.I.16)

Para elevar todos los criterios al nivel **Experto (100/100 puntos)**, se ejecutó una refactorización ordenada por fases desde la base del proyecto:

| Fase | Área / Criterios | Corrección Implementada | Justificación de Ingeniería de Software |
| :--- | :--- | :--- | :--- |
| **Fase 0 - 1** | Línea base y datos sensibles (Criterios 7, 13, 15) | Auditoría con **Bandit**, limpieza de `.env.example`, carga segura en `config/settings.py` y creación interactiva del `Administrador` inicial con `getpass` (`views/auth_view.py`). | Elimina credenciales fijas en el repositorio y evita la exposición visual de contraseñas en consola. |
| **Fase 2** | Autenticación y BD (Criterio 5) | Migración a `hashlib.scrypt` con sal aleatoria de 16 bytes (`models/usuario.py`), verificación `hmac.compare_digest` y bloqueo persistente en SQLite (`models/usuario_dao.py`, `config/database.py`). | Protege las credenciales frente a ataques de fuerza bruta y mantiene el bloqueo de 3 intentos / 5 minutos tras reiniciar el sistema. |
| **Fase 3 - 4** | Validación y acceso (Criterios 6, 8) | Reemplazo de `.isdigit()` por `int()` en `try/except ValueError` (`views/utils.py`), validación ISO 4217 y guardias RBAC (`controllers/seguridad.py`, `controllers/auth_controller.py`). | Previene falsos positivos Unicode y garantiza que solo usuarios autenticados con el rol autorizado consuman las APIs. |
| **Fase 5 - 6** | Cliente HTTP y excepciones (Criterios 1, 3, 9, 11) | Extracción filtrada en `services/clima_service.py` y `services/divisa_service.py`, jerarquía propia en `exceptions.py`, diferenciación de códigos HTTP (`4xx`/`5xx`) y bitácora en `config/logging_config.py`. | Aísla fallos de red, *timeouts* y respuestas HTTP inválidas sin mezclar errores técnicos con la lógica de negocio. |
| **Fase 7 - 9** | Integración, mensajes y entrega (Criterios 4, 12, 13-16) | Cálculos exactos con `decimal.Decimal` (`models/pago_internacional.py`), bloqueo de guardado en modo contingencia offline, mensajes seguros en consola y documentación en `README.md` y `Uso_IA.md`. | Garantiza exactitud contable, continuidad operativa sin contaminar la base de datos y trazabilidad completa de la entrega. |