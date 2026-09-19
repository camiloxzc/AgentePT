# validators.py
# funciones pa verificar los datos del cliente antes de guardarlo
# usa regex basicas y devuelve (True/False, motivo)

import re


def validar_identificacion(identificacion: str) -> tuple[bool, str]:
    # la cedula tiene que ser puro numero, minimo 4 digitos maximo 11
    cedula_limpia = str(identificacion).strip()
    if not re.fullmatch(r"\d{4,11}", cedula_limpia):
        return False, "La identificación debe tener entre 4 y 11 dígitos numéricos."
    return True, "OK"


def validar_nombre(nombre: str) -> tuple[bool, str]:
    nombre_limpio = nombre.strip()
    # chequeo longitud primero pa no gastar regex en vano
    if not (1 <= len(nombre_limpio) <= 100):
        return False, "El nombre debe tener entre 1 y 100 caracteres."
    # solo letras del español, nada de numeros ni simbolos raros
    if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ ]+", nombre_limpio):
        return False, "El nombre solo puede contener letras, espacios y tildes."
    return True, "OK"


def validar_telefono(telefono: str) -> tuple[bool, str]:
    # quito espacios y guiones que a veces la gente mete
    numero_limpio = str(telefono).strip().replace(" ", "").replace("-", "")
    if not re.fullmatch(r"\d{10}", numero_limpio):
        return False, "El teléfono debe tener exactamente 10 dígitos."
    # en colombia cel empieza en 3 y fijo en 6
    if numero_limpio[0] not in ("3", "6"):
        return False, "El teléfono debe iniciar con 3 (celular) o 6 (fijo)."
    return True, "OK"


def validar_correo(correo: str) -> tuple[bool, str]:
    correo_limpio = correo.strip().lower()
    # validacion basica, no es la mejor del mundo pero funciona pa demo
    if "@" not in correo_limpio:
        return False, "El correo debe contener @."
    if not re.fullmatch(
        r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", correo_limpio
    ):
        return False, "El formato del correo no es válido."
    return True, "OK"
