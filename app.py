import streamlit as st
import io
from datetime import date, timedelta
from reportes.generador import generar_excel

import yaml
from pathlib import Path
import streamlit_authenticator as stauth

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Interbanking · Reportes",
    page_icon="📊",
    layout="centered",
)

# ─────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────

ruta_yaml = Path(__file__).parent / "usuarios.yaml"

with open(ruta_yaml) as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    cookie_expiry_days=config['cookie']['expiry_days']
)

# Render login
authenticator.login()

name = st.session_state.get("name")
authentication_status = st.session_state.get("authentication_status")
username = st.session_state.get("username")

# Control acceso
if authentication_status is False:
    st.error("❌ Usuario o contraseña incorrectos")
    st.stop()

if authentication_status is None:
    st.warning("🔐 Ingresá tus credenciales")
    st.stop()

# Usuario logueado
st.success(f"Bienvenido {name} 👋")

# Logout
authenticator.logout("Cerrar sesión", "sidebar")

# ─────────────────────────────────────────────
# ESTILOS
# ─────────────────────────────────────────────

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=IBM+Plex+Mono:wght@400;500&display=swap');

  .block-container { max-width: 680px; padding-top: 2.5rem; }

  h1 {
    font-family: 'Syne', sans-serif !important;
    font-size: 2.4rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em !important;
    line-height: 1.1 !important;
  }

  .tag {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #2d6348;
    background: #e8f5ee;
    border: 1px solid #b8ddc8;
    padding: 4px 12px;
    border-radius: 100px;
    margin-bottom: 16px;
  }

  .desc {
    font-size: 15px;
    color: #7a7870;
    line-height: 1.7;
    margin-bottom: 8px;
  }

  .divider {
    border: none;
    border-top: 1.5px solid #e0ddd6;
    margin: 28px 0;
  }

  .footer-note {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: #aaa;
    text-align: center;
    margin-top: 32px;
    letter-spacing: 0.05em;
  }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────

st.markdown('<div class="tag">📊 Sistema de Reportes Financieros</div>', unsafe_allow_html=True)
st.title("Extractos bancarios en segundos.")
st.markdown('<p class="desc">Seleccioná la empresa y el período para descargar el Excel con todos los movimientos y saldos.</p>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FORMULARIO
# ─────────────────────────────────────────────

empresa = st.selectbox(
    "Empresa",
    options=["eliantus", "elementa", "integra"],
    format_func=lambda x: x.capitalize(),
)

col1, col2 = st.columns(2)
with col1:
    desde = st.date_input("Desde", value=date.today() - timedelta(days=7))
with col2:
    hasta = st.date_input("Hasta", value=date.today())

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GENERAR
# ─────────────────────────────────────────────

if st.button("⬇ Descargar Excel", use_container_width=True, type="primary"):

    if desde > hasta:
        st.error("⚠ La fecha 'Desde' no puede ser mayor que 'Hasta'.")
    else:
        with st.spinner("Conectando con Interbanking y generando el reporte..."):
            try:
                excel_bytes = generar_excel(
                    empresa=empresa,
                    desde=str(desde),
                    hasta=str(hasta),
                )
                nombre = f"reporte_{empresa}_{desde}_{hasta}.xlsx"

                st.success("✓ Reporte generado correctamente.")

                st.download_button(
                    label="📥 Hacer click para descargar",
                    data=excel_bytes,
                    file_name=nombre,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

            except Exception as e:
                st.error(f"✗ Error al generar el reporte: {e}")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────

st.markdown('<p class="footer-note">Sistema interno · No compartir fuera de la organización</p>', unsafe_allow_html=True)