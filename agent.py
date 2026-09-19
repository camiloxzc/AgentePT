# agent.py
# aca esta el nucleo del agente, la conexion con groq y el loop
# que va procesando las herramientas hasta tener una respuesta final
import os
import json
from groq import Groq
from tools import (
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
)

PROMPT_DEL_SISTEMA = """
Eres PT, asistente virtual de PRUEBA TÉCNICA, tienda de electrónica colombiana.

## REGLA NÚMERO UNO — LA MÁS IMPORTANTE:
NUNCA, BAJO NINGUNA CIRCUNSTANCIA, inventes nombres de productos, precios,
especificaciones ni disponibilidad. Si un cliente pregunta por productos,
SIEMPRE debes llamar primero a `recomendar_productos` o `consultar_catalogo`
y usar EXACTAMENTE los datos que esas funciones te devuelvan.
Usar nombres genéricos como "Portátil A", "Opción B" o inventar precios está
COMPLETAMENTE PROHIBIDO. Si la herramienta no devuelve resultados, dile al
cliente que no hay productos disponibles con esos filtros.

## Tu trabajo:
- Ayudar a encontrar el producto ideal según necesidades y presupuesto
- Consultar y rastrear pedidos
- Gestionar garantías y crear tickets de soporte técnico

## Cómo identificar al cliente:
- **Cliente frecuente**: pídele la cédula y llama `validar_cliente_existente`.
  Una vez validado, usa su nombre en toda la conversación.
- **Cliente nuevo**: recoge los datos de a uno de forma natural:
  1. Cédula (4 a 11 dígitos numéricos)
  2. Nombre completo (solo letras, espacios y tildes)
  3. Teléfono (10 dígitos, empieza en 3 o 6)
  4. Correo electrónico (debe tener @)
  Al final llama `registrar_cliente_nuevo` con todos los datos.

## Flujo para recomendaciones de productos:
1. Primero llama `recomendar_productos` con la necesidad y presupuesto del cliente.
2. Presenta los resultados usando el nombre exacto, precio y specs que devolvió la herramienta.
3. Ofrece llamar `comparar_productos` si el cliente quiere ver dos opciones en detalle.

## Flujo para compras:
1. Cuando el cliente diga que quiere comprar un producto, confírmale cuál producto quiere.
2. Pídele la dirección de entrega completa (con ciudad).
3. Llama `crear_pedido` con la cédula del cliente, el ID o nombre del producto y la dirección.
4. El pedido queda registrado y puede consultarse después con `consultar_estado_pedido`.

## Flujo para pedidos:
1. Pide el número de pedido o la cédula.
2. Llama `consultar_estado_pedido` y presenta el resultado exacto.

## Flujo para garantías:
1. Pide el número de pedido.
2. Llama `consultar_garantia` para verificar cobertura.
3. Si hay falla, llama `registrar_solicitud_garantia` para abrir el ticket.

## Escalar a asesor humano cuando:
- La herramienta de garantía devuelva `requiere_escalamiento: true`
- Haya daño físico, contacto con agua o robo
- El cliente pida hablar con una persona

Al escalar di: "Voy a conectarte con un asesor. 🔄 **[ESCALAMIENTO ACTIVADO]**"

## Estilo:
- Responde siempre en español colombiano, tono cálido y directo.
- Máximo 3 párrafos por respuesta.
- Usa el nombre del cliente cuando lo conozcas.
"""

# Definición de las herramientas en el formato que entiende Groq
DEFINICION_HERRAMIENTAS = [
    {
        "type": "function",
        "function": {
            "name": "consultar_catalogo",
            "description": "Busca en el catálogo de productos. Filtra por categoría o presupuesto máximo si se indican.",
            "parameters": {
                "type": "object",
                "properties": {
                    "categoria": {
                        "type": "string",
                        "description": "Categoría del producto: portátiles, celulares, televisores, accesorios. Vacío para ver todos.",
                    },
                    "presupuesto_maximo": {
                        "type": "integer",
                        "description": "Precio máximo en pesos colombianos (COP). 0 para no filtrar.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recomendar_productos",
            "description": "Recomienda los mejores productos según lo que el cliente necesita y cuánto puede gastar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "necesidad": {
                        "type": "string",
                        "description": "Para qué va a usar el producto (ej: diseño gráfico, gaming, ver series).",
                    },
                    "presupuesto": {
                        "type": "integer",
                        "description": "Presupuesto máximo en COP. 0 si no lo mencionó.",
                    },
                    "categoria": {
                        "type": "string",
                        "description": "Categoría si ya la especificó (portátiles, celulares, televisores, accesorios).",
                    },
                },
                "required": ["necesidad", "presupuesto"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "comparar_productos",
            "description": "Pone dos productos lado a lado para que el cliente vea las diferencias.",
            "parameters": {
                "type": "object",
                "properties": {
                    "producto_1": {"type": "string", "description": "Nombre o ID del primer producto"},
                    "producto_2": {"type": "string", "description": "Nombre o ID del segundo producto"},
                },
                "required": ["producto_1", "producto_2"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_estado_pedido",
            "description": "Consulta en qué estado está un pedido. Se puede buscar por número de pedido o por cédula del cliente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "numero_pedido": {"type": "string", "description": "Código del pedido, por ejemplo PED-1024."},
                    "cedula_cliente": {"type": "string", "description": "Cédula del cliente si no tiene el número de pedido."},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "crear_pedido",
            "description": "Registra un pedido nuevo para un cliente registrado. Requiere la cédula, el producto y la dirección de entrega.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cedula_cliente": {"type": "string", "description": "Cédula del cliente que hace la compra (debe estar registrado)."},
                    "producto_id": {"type": "string", "description": "ID o nombre del producto que quiere comprar (ej: PROD-001 o Dell XPS 15)."},
                    "direccion_entrega": {"type": "string", "description": "Dirección completa de entrega incluyendo ciudad."},
                },
                "required": ["cedula_cliente", "producto_id", "direccion_entrega"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "actualizar_direccion_entrega",
            "description": "Cambia la dirección de entrega de un pedido que aún no ha salido.",
            "parameters": {
                "type": "object",
                "properties": {
                    "numero_pedido": {"type": "string", "description": "Código del pedido (ej: PED-1024)"},
                    "nueva_direccion": {"type": "string", "description": "Nueva dirección de entrega completa con ciudad"},
                },
                "required": ["numero_pedido", "nueva_direccion"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "consultar_garantia",
            "description": "Revisa si un producto tiene garantía activa y qué cubre.",
            "parameters": {
                "type": "object",
                "properties": {
                    "numero_pedido": {"type": "string", "description": "Número del pedido asociado al producto (ej: PED-1025)"},
                },
                "required": ["numero_pedido"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "registrar_solicitud_garantia",
            "description": "Abre un ticket de soporte técnico por garantía. Si es daño físico o por líquido, marca para escalar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "numero_pedido": {"type": "string", "description": "Número del pedido del producto con falla"},
                    "descripcion_problema": {"type": "string", "description": "Descripción del problema que reporta el cliente"},
                    "tipo_falla": {
                        "type": "string",
                        "enum": ["hardware", "software", "fisica", "liquido"],
                        "description": "Tipo de falla del producto",
                    },
                },
                "required": ["numero_pedido", "descripcion_problema"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "validar_cliente_existente",
            "description": "Revisa si la cédula del cliente ya está registrada en el sistema.",
            "parameters": {
                "type": "object",
                "properties": {
                    "identificacion": {"type": "string", "description": "Número de cédula o documento"},
                },
                "required": ["identificacion"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "registrar_cliente_nuevo",
            "description": "Crea la cuenta de un cliente nuevo después de validar todos sus datos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "identificacion": {"type": "string", "description": "Cédula (4 a 11 dígitos)"},
                    "nombre_completo": {"type": "string", "description": "Nombre y apellidos completos"},
                    "telefono": {"type": "string", "description": "Teléfono de 10 dígitos que empieza en 3 o 6"},
                    "correo": {"type": "string", "description": "Correo electrónico válido con @"},
                },
                "required": ["identificacion", "nombre_completo", "telefono", "correo"],
            },
        },
    },
]

# aca relaciono el nombre de cada funcion con la funcion real de python
# asi cuando el modelo me dice "llama tal", yo busco aca y la ejecuto
MAPA_HERRAMIENTAS = {
    "consultar_catalogo": consultar_catalogo,
    "recomendar_productos": recomendar_productos,
    "comparar_productos": comparar_productos,
    "consultar_estado_pedido": consultar_estado_pedido,
    "crear_pedido": crear_pedido,
    "actualizar_direccion_entrega": actualizar_direccion_entrega,
    "consultar_garantia": consultar_garantia,
    "registrar_solicitud_garantia": registrar_solicitud_garantia,
    "validar_cliente_existente": validar_cliente_existente,
    "registrar_cliente_nuevo": registrar_cliente_nuevo,
}


def crear_cliente():
    # saco la key del .env y creo el cliente de groq
    # si no esta la key tiro error pa que el usuario sepa que le falta
    clave_api = os.getenv("GROQ_API_KEY")
    if not clave_api:
        raise ValueError(
            "No se encontró GROQ_API_KEY. "
            "Agrega tu clave gratuita de https://console.groq.com/keys en el archivo .env"
        )
    return Groq(api_key=clave_api)


def procesar_mensaje(historial_mensajes: list) -> str:
    # este es el loop principal del agente
    # mando el historial al modelo, si me pide ejecutar herramientas las ejecuto
    # y le devuelvo los resultados, hasta que responda en texto (o se pasen 4 vueltas)
    cliente_groq = crear_cliente()
    nombre_modelo = "openai/gpt-oss-20b"

    mensajes_completos = [{"role": "system", "content": PROMPT_DEL_SISTEMA}] + historial_mensajes

    for iteracion in range(4):
        # le paso todo al modelo y veo que me devuelve
        respuesta_modelo = cliente_groq.chat.completions.create(
            model=nombre_modelo,
            messages=mensajes_completos,
            tools=DEFINICION_HERRAMIENTAS,
            tool_choice="auto",
            temperature=0.1,
        )

        mensaje_respuesta = respuesta_modelo.choices[0].message
        mensajes_completos.append(mensaje_respuesta)

        # si no pidio llamar nada, ya tenemos respuesta en texto
        if not mensaje_respuesta.tool_calls:
            return mensaje_respuesta.content or ""

        # si pidio herramientas, las ejecuto una por una
        for llamada in mensaje_respuesta.tool_calls:
            nombre_funcion = llamada.function.name
            try:
                argumentos = json.loads(llamada.function.arguments)
            except Exception:
                argumentos = {}

            # busco la funcion en el mapa y la corro con los args
            if nombre_funcion in MAPA_HERRAMIENTAS:
                resultado = MAPA_HERRAMIENTAS[nombre_funcion](**argumentos)
            else:
                resultado = {"error": f"Herramienta '{nombre_funcion}' no reconocida."}

            # meto el resultado como mensaje con rol "tool" pa que el modelo lo lea
            mensajes_completos.append(
                {
                    "tool_call_id": llamada.id,
                    "role": "tool",
                    "name": nombre_funcion,
                    "content": json.dumps(resultado, ensure_ascii=False),
                }
            )

    # si despues de 4 vueltas no sale, devuelvo algo genérico
    return "Procesé tu solicitud. ¿Hay algo más en lo que te pueda ayudar?"
