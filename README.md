# Prueba Técnica — Agente de Atención al Cliente

Agente inteligente de atención al cliente para retail de electrónica, desarrollado como prueba técnica.

---

## Stack tecnológico

### Lenguaje
| Herramienta | Versión | Para qué se usa |
|---|---|---|
| Python | 3.13.3 | Lenguaje base del proyecto |

### Dependencias Python (instaladas con pip)
| Librería | Versión instalada | Para qué se usa |
|---|---|---|
| `streamlit` | 1.64.0 | Interfaz web de chat — genera la UI sin necesidad de HTML/CSS/JS |
| `groq` | 1.7.0 | SDK oficial para conectarse a la API de Groq y usar el modelo de lenguaje |
| `python-dotenv` | 1.2.3 | Lee la clave GROQ_API_KEY desde el archivo `.env` sin exponerla en el código |

### Modelo de lenguaje (IA)
| Componente | Detalle |
|---|---|
| Proveedor | [Groq](https://groq.com) — inferencia ultrarrápida en hardware LPU |
| Modelo activo | `openai/gpt-oss-20b` |
| Tipo de uso | Chat con funcion de llamada (tool calling) |
| Costo | Gratuito en el tier básico de Groq |
| API Key | Gratuita en [console.groq.com/keys](https://console.groq.com/keys) |

### Herramientas del agente (Functions / Tools)
El agente decide cuándo invocar cada una según el contexto de la conversación:

| Herramienta | Qué hace |
|---|---|
| `consultar_catalogo` | Filtra productos por categoría o presupuesto |
| `recomendar_productos` | Sugiere el top 3 según necesidad y presupuesto |
| `comparar_productos` | Pone dos productos lado a lado con specs y precio |
| `consultar_estado_pedido` | Busca un pedido por número o por cédula |
| `actualizar_direccion_entrega` | Cambia la dirección de entrega de un pedido pendiente |
| `consultar_garantia` | Verifica si hay garantía activa y qué cubre |
| `registrar_solicitud_garantia` | Abre un ticket de soporte y detecta si hay que escalar |
| `validar_cliente_existente` | Busca la cédula en el sistema |
| `registrar_cliente_nuevo` | Valida y registra un cliente nuevo en memoria |

### Persistencia de datos
| Tipo | Mecanismo | Persiste entre sesiones |
|---|---|---|
| Catálogo de productos | Diccionario Python en RAM | ❌ No |
| Pedidos | Diccionario Python en RAM | ❌ No |
| Garantías | Diccionario Python en RAM | ❌ No |
| Clientes registrados | Diccionario Python en RAM | ❌ No |
| Tickets de soporte | Contador entero en RAM | ❌ No |

> **Nota:** Todo el almacenamiento es en memoria volátil (RAM). No se usa ninguna base de datos,
> archivo ni servicio externo de persistencia. Al reiniciar la app, todo vuelve al estado inicial.
> Esto es intencional para efectos de demostración.

---

## Requisitos previos

- Python 3.10 o superior (probado en 3.13.3)
- Cuenta de Google o GitHub para crear la API Key de Groq

---

## Instalación

### 1. Descomprimir o clonar el proyecto

```bash
cd Agente
```

### 2. Crear entorno virtual (recomendado pero opcional)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar la API Key de Groq (gratis, sin tarjeta)

1. Ve a [https://console.groq.com/keys](https://console.groq.com/keys)
2. Inicia sesión con Google o GitHub
3. Haz clic en **"Create API Key"** y copia la clave (empieza por `gsk_...`)
4. Crea el archivo `.env` en la carpeta `Agente`:

```
GROQ_API_KEY=gsk_tu_clave_aqui
```

### 5. Ejecutar la app

```bash
streamlit run app.py
```

La interfaz se abre automáticamente en `http://localhost:8501`

---

## Escenarios de demo

El sidebar de la aplicación incluye guía para cada escenario.

### Escenario 1 — Venta consultiva
> *"Necesito un portátil para diseño gráfico por menos de 5 millones"*

Cédula de cliente frecuente: **12345678** — o usa una cédula inventada para probar el registro.

### Escenario 2 — Seguimiento de pedido
> *"Quiero saber dónde está mi pedido"*

Número de pedido: **PED-1024**

### Escenario 3 — Garantía y soporte
> *"Mi televisor dejó de encender y tiene garantía"*

Número de pedido: **PED-1026**

---

## Clientes de prueba precargados

| Cédula | Nombre |
|--------|--------|
| 12345678 | Carlos Rodríguez |
| 87654321 | María García |
| 11223344 | Luis Martínez |

Para probar el flujo de registro, usa cualquier cédula diferente a las anteriores.

---

## Estructura del proyecto

```
Agente/
├── app.py          → Interfaz web Streamlit (chat UI)
├── agent.py        → Configuración del agente, model y ciclo de tool calling
├── tools.py        → 9 herramientas mock disponibles para el agente
├── mock_data.py    → Datos de catálogo, pedidos, garantías y clientes
├── validators.py   → Validaciones de datos de clientes nuevos
├── requirements.txt
├── .env.example    → Plantilla del archivo de configuración
└── README.md
```

---

## Cómo desinstalar y liberar espacio

```bash
pip uninstall -r requirements.txt -y
pip cache purge
```

---

## Licencia

Este código es exclusivo para fines de evaluación técnica.
Ver archivo `LICENSE` para más detalles.
