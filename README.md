# EcoTech Solutions - Avance Estructural (EF2)

Asignatura: TI3021 Programación Orientada a Objeto Seguro

Integrantes: Jorge Lagos, Sebastian San Martin.

## Descripción
Implementación en Python del diagrama UML del sistema de gestión interna de EcoTech Solutions.

## Estructura
- `models/`: clases del UML (Usuario, Empleado, Administrador, Departamento, Proyecto, RegistroDeTiempo)
- `config/database.py`: conexión a la base de datos con `sqlite3`
- `main.py`: prueba de conexión a la base de datos

## POO aplicada
- Encapsulamiento: atributos privados con getters y setters
- Herencia: Administrador → Empleado → Usuario
- Asociaciones: Departamento y Proyecto guardan listas de empleados; Empleado guarda sus registros de tiempo

## Cómo ejecutar
- Prueba de conexión: `python main.py`
