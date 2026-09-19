# app.py - interfaz del chat con streamlit
# pa correrlo: streamlit run app.py
import streamlit as st
from dotenv import load_dotenv
from agent import procesar_mensaje, crear_cliente

load_dotenv()

# ── config de pagina ──
st.set_page_config(
    page_title="Prueba Técnica — PT",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)

# css pa que el sidebar no se vea tan gordo y no genere scroll
st.markdown(
    """
    <style>
        /* Reducir padding superior e interior del sidebar */
        [data-testid="stSidebar"] {
            padding-top: 0.5rem !important;
        }
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        [data-testid="stSidebar"] .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 0.5rem !important;
        }
        /* Ajustar espaciado de divisores, títulos y texto */
        [data-testid="stSidebar"] hr {
            margin: 0.4rem 0 !important;
        }
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] li {
            font-size: 0.82rem !important;
            margin-bottom: 0.2rem !important;
        }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            font-size: 0.95rem !important;
            margin-top: 0.2rem !important;
            margin-bottom: 0.2rem !important;
        }
        /* Compactar expanders */
        [data-testid="stSidebar"] .streamlit-expanderHeader {
            padding-top: 0.25rem !important;
            padding-bottom: 0.25rem !important;
            font-size: 0.82rem !important;
        }
        [data-testid="stSidebar"] .streamlit-expanderContent {
            padding: 0.4rem 0.5rem !important;
        }
        /* Botón de reinicio compacto */
        [data-testid="stSidebar"] .stButton button {
            padding: 0.3rem 0.6rem !important;
            font-size: 0.82rem !important;
            margin-top: 0.3rem !important;
        }
        .stChatMessage { border-radius: 10px; margin-bottom: 3px; }
        .stChatInput textarea { border-radius: 10px !important; }
        .block-container { padding-top: 1.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# estado de sesion (el historial del chat vive aca)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat" not in st.session_state:
    st.session_state.chat = None

# sidebar con la guia de escenarios
with st.sidebar:
    c_img, c_txt = st.columns([1, 3])
    with c_img:
        st.image("https://img.icons8.com/fluency/96/robot-2.png", width=44)
    with c_txt:
        st.markdown("**Prueba Técnica**")
        st.caption("Demo Agente Retail")

    st.markdown("---")
    st.markdown("**🎬 Guía de Escenarios**")

    with st.expander("🛒 1. Venta consultiva", expanded=False):
        st.markdown(
            "💬 *'Necesito un portátil para diseño gráfico por menos de 5 millones'*\n\n"
            "✓ Filtra catálogo, compara y recomienda con justificación."
        )

    with st.expander("📦 2. Seguimiento pedido", expanded=False):
        st.markdown(
            "💬 *'Quiero saber dónde está mi pedido'*\n\n"
            "Usa pedido: **PED-1024** o cédula: **12345678**"
        )

    with st.expander("🛡️ 3. Garantía y soporte", expanded=False):
        st.markdown(
            "💬 *'Mi televisor dejó de encender y tiene garantía'*\n\n"
            "Usa pedido: **PED-1026** (genera ticket y soporte)."
        )

    st.markdown("---")
    with st.expander("👥 Clientes demo", expanded=False):
        st.markdown(
            "• `12345678` - Carlos Rodríguez\n"
            "• `87654321` - María García\n"
            "• `11223344` - Luis Martínez"
        )

    if st.button("🔄 Reiniciar chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat = None
        st.rerun()

# cabecera
col_icon, col_title = st.columns([1, 6])
with col_icon:
    st.markdown("# 🤖")
with col_title:
    st.markdown("## PT — Prueba Técnica")
    st.caption("Asistente virtual de electrónica · *Impulsado por Llama 3.3 (Groq)*")

st.divider()

# reviso que la api key este configurada
try:
    crear_cliente()
except ValueError as e:
    st.error(f"⚠️ **Error de configuración:** {e}")
    st.info(
        "**Pasos para solucionarlo:**\n"
        "1. Abre el archivo `.env` en la carpeta `Agente`\n"
        "2. Agrega: `GROQ_API_KEY=gsk_tu_clave_aqui`\n"
        "3. Obtén tu clave gratis en: https://console.groq.com/keys\n"
        "4. Recarga la página"
    )
    st.stop()

# mensaje de bienvenida, solo sale la primera vez
if not st.session_state.messages:
    mensaje_bienvenida = (
        "¡Hola! 👋 Soy **PT**, tu asistente virtual de **PRUEBA TÉCNICA**.\n\n"
        "Puedo ayudarte con:\n"
        "- 🛒 **Comprar** celulares, portátiles, televisores y accesorios\n"
        "- 📦 **Rastrear** el estado de tu pedido\n"
        "- 🛡️ **Gestionar** garantías y soporte técnico\n\n"
        "¿Con qué te puedo ayudar hoy?"
    )
    st.session_state.messages.append({"role": "assistant", "content": mensaje_bienvenida})

# pinto el historial
for mensaje in st.session_state.messages:
    with st.chat_message(mensaje["role"]):
        st.markdown(mensaje["content"])

# aca recibo lo que escribe el usuario y se lo mando al agente
if texto_usuario := st.chat_input("Escribe tu mensaje aquí..."):
    # Agrego el mensaje del usuario al historial y lo muestro
    st.session_state.messages.append({"role": "user", "content": texto_usuario})
    with st.chat_message("user"):
        st.markdown(texto_usuario)

    # Armo el historial limpio para mandarlo al modelo (solo role y content)
    historial_para_modelo = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    # Llamo al agente y muestro la respuesta
    with st.chat_message("assistant"):
        with st.spinner("PT está pensando..."):
            try:
                respuesta_agente = procesar_mensaje(historial_para_modelo)
            except Exception as error:
                respuesta_agente = f"⚠️ Ocurrió un error: {str(error)}"
        st.markdown(respuesta_agente)

    st.session_state.messages.append({"role": "assistant", "content": respuesta_agente})
