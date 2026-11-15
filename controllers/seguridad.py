from exceptions import AccesoDenegadoError  # Error propio cuando falta sesión o permisos
from models.usuario import Usuario  # Modelo de dominio del usuario autenticado


def exigir_sesion(usuario: Usuario | None) -> Usuario:  # Frena el acceso si no hay sesión activa
    if usuario is None or not isinstance(usuario, Usuario):  # Verifica que exista un Usuario válido
        raise AccesoDenegadoError("Debe iniciar sesión para entrar a este módulo.")
    return usuario  # Devuelve el usuario validado


def exigir_rol(usuario: Usuario | None, *roles_permitidos: str) -> Usuario:  # Exige sesión y rol autorizado
    user = exigir_sesion(usuario)  # Primero asegura que haya sesión activa
    if user.rol not in roles_permitidos:  # Revisa si su rol está dentro de los permitidos
        raise AccesoDenegadoError(f"Su rol '{user.rol}' no tiene permisos para realizar esta acción.")
    return user  # Devuelve el usuario autorizado