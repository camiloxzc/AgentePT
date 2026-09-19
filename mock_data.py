"""
Acá guardo toda la data de prueba que usa el agente durante la demo.
Son diccionarios en memoria — no hay base de datos,
todo se pierde cuando se reinicia la app.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GUÍA DE CAMBIOS EN SESIÓN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ PUEDE MODIFICARSE EN MEMORIA DURANTE LA SESIÓN:
   - CLIENTES_REGISTRADOS → el agente agrega entradas nuevas cuando registra
     un cliente nuevo con registrar_cliente_nuevo(). Esos clientes existen
     solo mientras la app esté abierta.
   - PEDIDOS              → el agente puede cambiar la dirección de entrega
     de un pedido usando actualizar_direccion_entrega(). El cambio vive en RAM.
   - _contador_tickets    → sube en 1 cada vez que se abre un ticket de garantía
     con registrar_solicitud_garantia(). Se reinicia al cerrar la app.

❌ SOLO LECTURA — el agente NO puede agregar ni modificar estos datos:
   - PRODUCTOS  → el catálogo es fijo. No hay herramienta para agregar productos.
                  En un sistema real vendría de una base de datos de inventario.
   - GARANTIAS  → las coberturas están hardcodeadas. No se pueden crear garantías
                  nuevas desde el agente.

    TODO se pierde al reiniciar la app porque no hay persistencia real.
    Eso es intencional — este código es solo para demostración técnica.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# SOLO LECTURA
PRODUCTOS = [
    {
        "id": "PROD-001",
        "nombre": "Dell XPS 15",
        "categoria": "portátiles",
        "precio": 4800000,
        "especificaciones": "Intel Core i7-13700H, 16GB RAM DDR5, NVIDIA RTX 3050 4GB, 512GB NVMe SSD, pantalla OLED 3.5K",
        "uso_recomendado": "diseño gráfico, edición de video, fotografía profesional",
        "disponible": True,
        "meses_garantia": 12,
    },
    {
        "id": "PROD-002",
        "nombre": "MacBook Air M2",
        "categoria": "portátiles",
        "precio": 4350000,
        "especificaciones": "Apple M2 8 núcleos CPU, GPU 8 núcleos, 8GB RAM unificada, 256GB SSD, pantalla Liquid Retina",
        "uso_recomendado": "diseño gráfico, edición creativa, ecosistema Apple",
        "disponible": True,
        "meses_garantia": 12,
    },
    {
        "id": "PROD-003",
        "nombre": "Lenovo IdeaPad 5 Pro",
        "categoria": "portátiles",
        "precio": 3100000,
        "especificaciones": "AMD Ryzen 7 6800H, 16GB RAM, Radeon integrada, 512GB SSD, pantalla 2.8K 90Hz",
        "uso_recomendado": "diseño básico, multitarea, estudiantes y oficina",
        "disponible": True,
        "meses_garantia": 12,
    },
    {
        "id": "PROD-004",
        "nombre": "ASUS ProArt Studiobook",
        "categoria": "portátiles",
        "precio": 7200000,
        "especificaciones": "Intel Core i9-13980HX, 32GB RAM, NVIDIA RTX 4070 8GB, 1TB SSD, pantalla OLED 4K calibrada",
        "uso_recomendado": "diseño gráfico profesional, renderizado 3D, animación",
        "disponible": False,
        "meses_garantia": 24,
    },
    {
        "id": "PROD-005",
        "nombre": "Samsung Galaxy S24",
        "categoria": "celulares",
        "precio": 3800000,
        "especificaciones": "Snapdragon 8 Gen 3, 8GB RAM, 256GB, cámara 50MP + teleobjetivo 10x, Galaxy AI",
        "uso_recomendado": "uso diario, fotografía, productividad",
        "disponible": True,
        "meses_garantia": 12,
    },
    {
        "id": "PROD-006",
        "nombre": "iPhone 15 Pro",
        "categoria": "celulares",
        "precio": 6200000,
        "especificaciones": "Apple A17 Pro, 8GB RAM, 256GB, sistema de cámara pro 48MP, titanio",
        "uso_recomendado": "fotografía y video profesional, ecosistema Apple",
        "disponible": True,
        "meses_garantia": 12,
    },
    {
        "id": "PROD-007",
        "nombre": "Samsung 65\" QLED 4K",
        "categoria": "televisores",
        "precio": 4200000,
        "especificaciones": "65 pulgadas, 4K UHD, QLED, 120Hz, Smart TV Tizen, HDMI 2.1, Dolby Atmos",
        "uso_recomendado": "gaming, entretenimiento familiar, deportes",
        "disponible": True,
        "meses_garantia": 12,
    },
    {
        "id": "PROD-008",
        "nombre": "LG OLED C3 55\"",
        "categoria": "televisores",
        "precio": 5500000,
        "especificaciones": "55 pulgadas, 4K OLED evo, 120Hz, webOS 23, Dolby Vision IQ + Atmos, G-Sync",
        "uso_recomendado": "cine en casa, calidad de imagen premium, gaming avanzado",
        "disponible": True,
        "meses_garantia": 12,
    },
    {
        "id": "PROD-009",
        "nombre": "Mouse Logitech MX Master 3S",
        "categoria": "accesorios",
        "precio": 420000,
        "especificaciones": "Inalámbrico Bluetooth/USB-C, 8000DPI, scroll MagSpeed, carga rápida, compatible Mac/Windows",
        "uso_recomendado": "productividad, diseño gráfico, trabajo profesional",
        "disponible": True,
        "meses_garantia": 24,
    },
    {
        "id": "PROD-010",
        "nombre": "Monitor Samsung 27\" QHD",
        "categoria": "accesorios",
        "precio": 1200000,
        "especificaciones": "27 pulgadas, 2560x1440 QHD, 165Hz, IPS, 1ms, HDR400, HDMI 2.0 + DisplayPort",
        "uso_recomendado": "diseño gráfico, gaming, trabajo dual monitor",
        "disponible": True,
        "meses_garantia": 12,
    },
]

# ✅ MODIFICABLE EN SESIÓN — actualizar_direccion_entrega() puede cambiar
# el campo "direccion" de cualquier pedido en memoria mientras la app esté abierta.
# ❌ No se pueden agregar pedidos nuevos.
PEDIDOS = {
    "PED-1024": {
        "estado": "En reparto",
        "producto": "Samsung Galaxy S24",
        "fecha_estimada": "2026-09-20",
        "direccion": "Cra 7 # 45-32, Bogotá",
        "cedula_cliente": "12345678",
    },
    "PED-1025": {
        "estado": "Entregado",
        "producto": "Dell XPS 15",
        "fecha_estimada": "2026-09-15",
        "direccion": "Av El Dorado # 68-50, Bogotá",
        "cedula_cliente": "87654321",
    },
    "PED-1026": {
        "estado": "En preparación",
        "producto": "LG OLED C3 55\"",
        "fecha_estimada": "2026-09-23",
        "direccion": "Cll 100 # 15-20, Medellín",
        "cedula_cliente": "11223344",
    },
}

# ❌ SOLO LECTURA — las garantías son fijas. No hay herramienta para crear ni editar coberturas.
GARANTIAS = {
    "PED-1025": {
        "producto": "Dell XPS 15",
        "vigente": True,
        "fecha_vencimiento": "2027-09-15",
        "tipo": "Garantía de fábrica 12 meses",
        "cobertura": "Defectos de fabricación y fallas de hardware",
    },
    "PED-1024": {
        "producto": "Samsung Galaxy S24",
        "vigente": True,
        "fecha_vencimiento": "2027-09-20",
        "tipo": "Garantía de fábrica 12 meses",
        "cobertura": "Defectos de fabricación",
    },
    "PED-1023": {
        "producto": "iPhone 14 Pro",
        "vigente": False,
        "fecha_vencimiento": "2025-08-10",
        "tipo": "Garantía de fábrica 12 meses",
        "cobertura": "Garantía expirada",
    },
    "PED-1026": {
        "producto": "LG OLED C3 55\"",
        "vigente": True,
        "fecha_vencimiento": "2027-09-23",
        "tipo": "Garantía de fábrica 12 meses",
        "cobertura": "Defectos de fabricación y panel",
    },
}

# Clientes que ya están en el sistema para poder probar el flujo de cliente frecuente
# ✅ MODIFICABLE EN SESIÓN — registrar_cliente_nuevo() agrega entradas aquí en tiempo real.
# Los clientes nuevos quedan disponibles para el resto de la sesión pero desaparecen
# al reiniciar la app. En producción esto iría a una base de datos real.
CLIENTES_REGISTRADOS = {
    "12345678": {
        "nombre": "Carlos Rodríguez",
        "telefono": "3201234567",
        "correo": "c.rodriguez@gmail.com",
    },
    "87654321": {
        "nombre": "María García",
        "telefono": "3109876543",
        "correo": "m.garcia@gmail.com",
    },
    "11223344": {
        "nombre": "Luis Martínez",
        "telefono": "3155678901",
        "correo": "l.martinez@gmail.com",
    },
}

# ✅ MODIFICABLE EN SESIÓN — sube en 1 cada vez que se genera un ticket de garantía.
# Se reinicia a 9000 cada vez que se cierra y vuelve a abrir la app.
_contador_tickets = 9000

# ✅ MODIFICABLE EN SESIÓN — sube en 1 cada vez que se crea un pedido nuevo con crear_pedido().
# Arranca en 2000 para no chocar con los pedidos de prueba (PED-1024, PED-1025, PED-1026).
_contador_pedidos = 2000
