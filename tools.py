# tools.py
# todas las funciones que el agente puede llamar
# son mocks, simulan lo que haria un sistema real pero con datos en ram
import mock_data
from mock_data import PRODUCTOS, PEDIDOS, GARANTIAS, CLIENTES_REGISTRADOS
from validators import (
    validar_identificacion,
    validar_nombre,
    validar_telefono,
    validar_correo,
)

# --- VENTAS ---

def consultar_catalogo(categoria: str = "", presupuesto_maximo: int = 0) -> dict:
    # Busco en el listado de productos. Si me pasan categoría o presupuesto, filtro.
    # Si no encuentro nada en stock con esos filtros, aviso que no hay disponibles.
    lista_productos = PRODUCTOS

    if categoria:
        lista_productos = [p for p in lista_productos if categoria.lower() in p["categoria"].lower()]

    if presupuesto_maximo > 0:
        lista_productos = [p for p in lista_productos if p["precio"] <= presupuesto_maximo]

    productos_en_stock = [p for p in lista_productos if p["disponible"]]

    if not productos_en_stock:
        return {
            "encontrados": 0,
            "mensaje": "No hay productos en stock con esos filtros.",
            "productos": [],
        }

    return {
        "encontrados": len(productos_en_stock),
        "productos": [
            {
                "id": p["id"],
                "nombre": p["nombre"],
                "precio_cop": f"${p['precio']:,}",
                "especificaciones": p["especificaciones"],
                "uso_recomendado": p["uso_recomendado"],
                "garantia": f"{p['meses_garantia']} meses",
                "disponible": "En stock",
            }
            for p in productos_en_stock
        ],
    }


def recomendar_productos(necesidad: str, presupuesto: int, categoria: str = "") -> dict:
    # Busco los productos que más encajen con lo que el cliente me describió.
    # Le doy puntaje a cada uno según cuántas palabras clave de la necesidad aparecen
    # en las specs o en el uso recomendado. Devuelvo el top 3.
    lista_base = PRODUCTOS

    if categoria:
        lista_base = [p for p in lista_base if categoria.lower() in p["categoria"].lower()]

    if presupuesto > 0:
        lista_base = [p for p in lista_base if p["precio"] <= presupuesto and p["disponible"]]
    else:
        lista_base = [p for p in lista_base if p["disponible"]]

    puntuados = []
    palabras_clave = necesidad.lower().split()

    for producto in lista_base:
        puntaje = 0
        texto_buscable = (
            producto["uso_recomendado"].lower()
            + " "
            + producto["nombre"].lower()
            + " "
            + producto["especificaciones"].lower()
        )
        for palabra in palabras_clave:
            if len(palabra) > 2 and palabra in texto_buscable:
                puntaje += 1
        puntuados.append((puntaje, producto))

    # Ordeno por puntaje desc, luego por precio asc si hay empate
    puntuados.sort(key=lambda x: (-x[0], x[1]["precio"]))
    mejores = puntuados[:3]

    if not mejores:
        return {
            "mensaje": "No encontré productos que encajen con esos filtros.",
            "recomendaciones": [],
        }

    return {
        "necesidad_detectada": necesidad,
        "presupuesto": f"${presupuesto:,}" if presupuesto > 0 else "No especificado",
        "total_opciones": len(mejores),
        "recomendaciones": [
            {
                "posicion": indice + 1,
                "nombre": producto["nombre"],
                "precio_cop": f"${producto['precio']:,}",
                "precio_numerico": producto["precio"],
                "especificaciones": producto["especificaciones"],
                "por_que_recomendado": producto["uso_recomendado"],
                "garantia": f"{producto['meses_garantia']} meses",
            }
            for indice, (puntaje, producto) in enumerate(mejores)
        ],
    }


def comparar_productos(producto_1: str, producto_2: str) -> dict:
    # Busco los dos productos por nombre o ID y los pongo lado a lado para que el cliente
    # pueda ver de un vistazo cuál le conviene más según precio, specs y garantía.
    def buscar_por_nombre_o_id(consulta: str):
        texto = consulta.lower().strip()
        for p in PRODUCTOS:
            if p["id"].lower() == texto or texto in p["nombre"].lower():
                return p
        return None

    primer_producto = buscar_por_nombre_o_id(producto_1)
    segundo_producto = buscar_por_nombre_o_id(producto_2)

    if not primer_producto:
        return {"error": f"No encontré '{producto_1}' en el catálogo."}
    if not segundo_producto:
        return {"error": f"No encontré '{producto_2}' en el catálogo."}

    diferencia_precio = abs(primer_producto["precio"] - segundo_producto["precio"])

    return {
        "comparacion": {
            primer_producto["nombre"]: {
                "precio_cop": f"${primer_producto['precio']:,}",
                "especificaciones": primer_producto["especificaciones"],
                "uso_ideal": primer_producto["uso_recomendado"],
                "garantia": f"{primer_producto['meses_garantia']} meses",
                "disponible": "✅ En stock" if primer_producto["disponible"] else "❌ Agotado",
            },
            segundo_producto["nombre"]: {
                "precio_cop": f"${segundo_producto['precio']:,}",
                "especificaciones": segundo_producto["especificaciones"],
                "uso_ideal": segundo_producto["uso_recomendado"],
                "garantia": f"{segundo_producto['meses_garantia']} meses",
                "disponible": "✅ En stock" if segundo_producto["disponible"] else "❌ Agotado",
            },
        },
        "diferencia_precio": f"${diferencia_precio:,}",
        "mas_economico": primer_producto["nombre"] if primer_producto["precio"] < segundo_producto["precio"] else segundo_producto["nombre"],
        "mayor_garantia": (
            primer_producto["nombre"]
            if primer_producto["meses_garantia"] >= segundo_producto["meses_garantia"]
            else segundo_producto["nombre"]
        ),
    }

# --- PEDIDOS ---

def consultar_estado_pedido(numero_pedido: str = "", cedula_cliente: str = "") -> dict:
    # Si me dan el número de pedido lo busco directo. Si no, busco por cédula del cliente
    # y devuelvo el primer pedido que encuentre asociado a esa cédula.
    if numero_pedido:
        clave = numero_pedido.upper().strip()
        if not clave.startswith("PED-"):
            clave = f"PED-{clave}"

        if clave in PEDIDOS:
            datos = PEDIDOS[clave]
            return {
                "pedido": clave,
                "estado": datos["estado"],
                "producto": datos["producto"],
                "fecha_estimada_entrega": datos["fecha_estimada"],
                "direccion_envio": datos["direccion"],
            }
        return {"error": f"No encontré el pedido {clave}. Verifica el número e intenta de nuevo."}

    if cedula_cliente:
        # junto todos los pedidos de este cliente para mostrarlos
        pedidos_del_cliente = [
            (clave, datos)
            for clave, datos in PEDIDOS.items()
            if datos["cedula_cliente"] == str(cedula_cliente).strip()
        ]
        if pedidos_del_cliente:
            clave, datos = pedidos_del_cliente[0]
            return {
                "pedido": clave,
                "estado": datos["estado"],
                "producto": datos["producto"],
                "fecha_estimada_entrega": datos["fecha_estimada"],
                "direccion_envio": datos["direccion"],
            }
        return {"mensaje": "No encontré pedidos registrados con esa identificación."}

    return {"error": "Necesito el número de pedido o la cédula del cliente para buscar."}


def crear_pedido(cedula_cliente: str, producto_id: str, direccion_entrega: str) -> dict:
    # Cuando el cliente quiere comprar un producto, creo el pedido en memoria.
    # Le genero un número con el formato PED-XXXX usando el contador global.
    # Si el producto no existe o no tiene stock, aviso. También valido que el cliente
    # ya esté registrado antes de dejarlo pedir.
    from datetime import datetime, timedelta

    cedula = str(cedula_cliente).strip()
    if cedula not in CLIENTES_REGISTRADOS:
        return {"error": "El cliente debe estar registrado para hacer un pedido. Usa registrar_cliente_nuevo primero."}

    # busco el producto por ID o por nombre parcial
    producto_encontrado = None
    for p in PRODUCTOS:
        if p["id"].upper() == producto_id.upper().strip():
            producto_encontrado = p
            break
        elif producto_id.lower().strip() in p["nombre"].lower():
            producto_encontrado = p
            break

    if not producto_encontrado:
        return {"error": f"No encontré el producto '{producto_id}' en el catálogo."}

    if not producto_encontrado["disponible"]:
        return {"error": f"El producto {producto_encontrado['nombre']} está agotado en este momento."}

    # genero el numero de pedido incrementando el contador
    mock_data._contador_pedidos += 1
    numero_nuevo = f"PED-{mock_data._contador_pedidos}"

    # calculo una fecha estimada de entrega (5 dias habiles aprox)
    fecha_entrega = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")

    # guardo en el diccionario de pedidos para que sea consultable despues
    PEDIDOS[numero_nuevo] = {
        "estado": "En preparación",
        "producto": producto_encontrado["nombre"],
        "fecha_estimada": fecha_entrega,
        "direccion": direccion_entrega.strip(),
        "cedula_cliente": cedula,
    }

    # tambien creo la garantia automaticamente para que quede coherente
    GARANTIAS[numero_nuevo] = {
        "producto": producto_encontrado["nombre"],
        "vigente": True,
        "fecha_vencimiento": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
        "tipo": f"Garantía de fábrica {producto_encontrado['meses_garantia']} meses",
        "cobertura": "Defectos de fabricación y fallas de hardware",
    }

    nombre_cliente = CLIENTES_REGISTRADOS[cedula]["nombre"]

    return {
        "exito": True,
        "numero_pedido": numero_nuevo,
        "cliente": nombre_cliente,
        "producto": producto_encontrado["nombre"],
        "precio": f"${producto_encontrado['precio']:,}",
        "direccion": direccion_entrega.strip(),
        "fecha_estimada": fecha_entrega,
        "estado": "En preparación",
        "mensaje": f"✅ Pedido **{numero_nuevo}** creado exitosamente. {nombre_cliente}, tu {producto_encontrado['nombre']} llegará aproximadamente el {fecha_entrega}.",
    }


def actualizar_direccion_entrega(numero_pedido: str, nueva_direccion: str) -> dict:
    # Cambio la dirección de entrega siempre que el pedido no esté entregado ni en reparto.
    # Si ya salió a reparto, no puedo hacer nada desde acá.
    clave = numero_pedido.upper().strip()
    if not clave.startswith("PED-"):
        clave = f"PED-{clave}"

    if clave not in PEDIDOS:
        return {"error": f"No encontré el pedido {clave}."}

    datos_pedido = PEDIDOS[clave]

    if datos_pedido["estado"] == "Entregado":
        return {"error": "No se puede cambiar la dirección de un pedido ya entregado."}

    if datos_pedido["estado"] == "En reparto":
        return {"error": "El pedido ya está en reparto. Para cambios urgentes comunícate con la transportadora."}

    direccion_anterior = datos_pedido["direccion"]
    PEDIDOS[clave]["direccion"] = nueva_direccion

    return {
        "exito": True,
        "pedido": clave,
        "direccion_anterior": direccion_anterior,
        "nueva_direccion": nueva_direccion,
        "mensaje": f"✅ Dirección actualizada correctamente para el pedido {clave}.",
    }

# --- GARANTIAS Y SOPORTE ---

def consultar_garantia(numero_pedido: str) -> dict:
    # Verifico si el producto del pedido todavía tiene garantía activa y qué cubre.
    # Si no encuentro el pedido en la tabla de garantías, aviso que no hay registro.
    clave = numero_pedido.upper().strip()
    if not clave.startswith("PED-"):
        clave = f"PED-{clave}"

    if clave not in GARANTIAS:
        return {"error": f"No encontré información de garantía para el pedido {clave}. Verifica el número."}

    datos_garantia = GARANTIAS[clave]

    return {
        "pedido": clave,
        "producto": datos_garantia["producto"],
        "garantia_vigente": datos_garantia["vigente"],
        "estado": "✅ Garantía activa" if datos_garantia["vigente"] else "❌ Garantía expirada",
        "tipo_garantia": datos_garantia["tipo"],
        "fecha_vencimiento": datos_garantia["fecha_vencimiento"],
        "cobertura": datos_garantia["cobertura"],
    }


def registrar_solicitud_garantia(
    numero_pedido: str,
    descripcion_problema: str,
    tipo_falla: str = "hardware",
) -> dict:
    # Abro un ticket de soporte para el cliente. Si la falla es física o por líquido,
    # marco que requiere escalar a un asesor porque eso no lo cubre la garantía de fábrica.
    # Genero un número de ticket único incrementando el contador global.
    clave = numero_pedido.upper().strip()
    if not clave.startswith("PED-"):
        clave = f"PED-{clave}"

    if clave not in GARANTIAS:
        return {"error": f"No se encontró garantía para el pedido {clave}."}

    datos_garantia = GARANTIAS[clave]

    if not datos_garantia["vigente"]:
        return {
            "garantia_expirada": True,
            "fecha_vencimiento": datos_garantia["fecha_vencimiento"],
            "mensaje": "La garantía de este producto está vencida. El servicio técnico tendría costo.",
            "requiere_escalamiento": True,
        }

    # Daño físico y por líquidos no están cubiertos — hay que escalar
    fallas_sin_cobertura = ["fisica", "liquido"]
    requiere_escalar = tipo_falla.lower() in fallas_sin_cobertura

    mock_data._contador_tickets += 1
    numero_ticket = f"TICK-{mock_data._contador_tickets}"

    return {
        "ticket_generado": numero_ticket,
        "producto": datos_garantia["producto"],
        "pedido": clave,
        "tipo_falla": tipo_falla,
        "descripcion": descripcion_problema,
        "estado_ticket": "Abierto",
        "tiempo_respuesta": "24 a 48 horas hábiles",
        "cubierto_por_garantia": not requiere_escalar,
        "requiere_escalamiento": requiere_escalar,
        "razon_escalamiento": (
            "Daño físico o por líquidos — no cubierto por garantía de fábrica"
            if requiere_escalar
            else None
        ),
        "mensaje": f"✅ Ticket **{numero_ticket}** creado. Un técnico revisará tu caso en 24-48 horas hábiles.",
    }

# --- CLIENTES ---

def validar_cliente_existente(identificacion: str) -> dict:
    # Busco la cédula en los clientes registrados. Si existe, saludo al cliente por su nombre.
    # Si no, le propongo que se registre como cliente nuevo.
    cedula = str(identificacion).strip()

    if cedula in CLIENTES_REGISTRADOS:
        datos_cliente = CLIENTES_REGISTRADOS[cedula]
        return {
            "registrado": True,
            "cedula_cliente": cedula,
            "nombre": datos_cliente["nombre"],
            "mensaje": f"¡Bienvenido de nuevo, {datos_cliente['nombre']}! 👋",
        }

    return {
        "registrado": False,
        "mensaje": "No encontré una cuenta con esa identificación. ¿Deseas registrarte como cliente nuevo?",
    }


def registrar_cliente_nuevo(
    identificacion: str,
    nombre_completo: str,
    telefono: str,
    correo: str,
) -> dict:
    # Valido uno a uno los campos del cliente nuevo antes de guardarlo.
    # Si algún campo no cumple las reglas, devuelvo el error específico para que el agente
    # le pida al cliente que corrija ese dato en particular.
    es_valido, mensaje_error = validar_identificacion(identificacion)
    if not es_valido:
        return {"error": f"Identificación inválida: {mensaje_error}"}

    es_valido, mensaje_error = validar_nombre(nombre_completo)
    if not es_valido:
        return {"error": f"Nombre inválido: {mensaje_error}"}

    es_valido, mensaje_error = validar_telefono(telefono)
    if not es_valido:
        return {"error": f"Teléfono inválido: {mensaje_error}"}

    es_valido, mensaje_error = validar_correo(correo)
    if not es_valido:
        return {"error": f"Correo inválido: {mensaje_error}"}

    if str(identificacion).strip() in CLIENTES_REGISTRADOS:
        return {"error": "Este número de identificación ya está registrado en el sistema."}

    # Guardo en el diccionario en memoria. Desaparece al reiniciar — eso es intencional.
    CLIENTES_REGISTRADOS[str(identificacion).strip()] = {
        "nombre": nombre_completo.strip(),
        "telefono": str(telefono).strip(),
        "correo": correo.strip().lower(),
    }

    return {
        "exito": True,
        "cedula_cliente": str(identificacion).strip(),
        "mensaje": f"✅ ¡Bienvenido, {nombre_completo}! Tu cuenta fue creada exitosamente.",
        "datos_registrados": {
            "nombre": nombre_completo,
            "telefono": telefono,
            "correo": correo,
        },
    }


# pa tener la lista completa de todo lo que el agente puede hacer
HERRAMIENTAS = [
    consultar_catalogo,
    recomendar_productos,
    comparar_productos,
    consultar_estado_pedido,
    crear_pedido,
    actualizar_direccion_entrega,
    consultar_garantia,
    registrar_solicitud_garantia,
    validar_cliente_existente,
    registrar_cliente_nuevo,
]
