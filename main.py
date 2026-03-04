import streamlit as st
import streamlit_authenticator as stauth
import os
import yaml
from yaml.loader import SafeLoader
from dotenv import load_dotenv
from utils.styles import apply_custom_styles
from services.github_service import get_latest_repos, check_vps_health
from services.finance_service import get_market_data, get_realtime_price, create_stock_chart, get_spanish_stocks
from services.news_service import get_tech_news_es, get_economic_news_es
from services.mail_service import get_inbox_summary

# Load config
load_dotenv()

# Authentication Setup
config = {
    "credentials": {
        "usernames": {
            os.getenv("ADMIN_USER", "Miguel"): {
                "name": "Miguel",
                "password": os.getenv("ADMIN_PASS_HASH", "$2b$12$b/47AVG6wiq6BkrzfDoEoes.yfhqzxAoqUMfc05EgelCpNYa9rbTu")
            }
        }
    },
    "cookie": {
        "expiry_days": 30,
        "key": os.getenv("COOKIE_KEY", "signature_key"),
        "name": "dashboard_cookie"
    }
}

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Page config
st.set_page_config(page_title="Personal Dashboard", layout="wide", initial_sidebar_state="collapsed")
apply_custom_styles()

# Login Logic
name, authentication_status, username = authenticator.login('main')

if authentication_status is False:
    st.error('Username/password is incorrect')
    st.stop()
elif authentication_status is None:
    st.warning('Please enter your username and password')
    st.stop()

# --- Authenticated App ---
with st.sidebar:
    st.subheader(f"Bienvenido, {name}")
    authenticator.logout('Cerrar Sesión', 'main')
    
    st.markdown("---")
    with st.expander("🛠️ Estado de Configuración"):
        required_vars = ["GITHUB_TOKEN", "VPS_IP", "IMAP_SERVER", "IMAP_USER", "IMAP_PASS"]
        for var in required_vars:
            exists = os.getenv(var) is not None
            st.write(f"{'✅' if exists else '❌'} {var}")
        
        if not all(os.getenv(v) for v in required_vars):
            st.info("Añade las variables faltantes en la pestaña 'Environment Variables' de tu proyecto en Coolify.")
            
    st.markdown("---")
    st.subheader("🚀 Mis Aplicaciones")
    vps_base = f"http://{os.getenv('VPS_IP', '212.227.104.207')}"
    
    # List of apps based on previous work
    apps = [
        {"name": "📝 QuizMaster", "url": f"{vps_base}:8001"},
        {"name": "🚗 Mantenimiento Vehículos", "url": f"{vps_base}:8002"},
        {"name": "📊 Dashboard Financiero", "url": f"{vps_base}:8003"},
        {"name": "📂 Gestión Documental V3", "url": f"{vps_base}:8004"}
    ]
    
    for app in apps:
        st.markdown(f"""
        <div style="margin-bottom: 10px;">
            <a href="{app['url']}" target="_blank" style="text-decoration: none;">
                <button style="width: 100%; padding: 10px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); background: rgba(255,255,255,0.05); color: white; cursor: pointer; text-align: left;">
                    {app['name']}
                </a>
            </button>
        </div>
        """, unsafe_allow_html=True)

# Header
col_title, col_refresh = st.columns([0.8, 0.2])
with col_title:
    st.title("🚀 Personal Operations Dashboard")
    st.markdown("___")

with col_refresh:
    if st.button("🔄 Refrescar Datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Layout
col1, col2 = st.columns(2)

# --- Módulo GitHub & Infraestructura ---
with col1:
    st.subheader("💻 GitHub & Infraestructura")
    
    # VPS Status
    vps_ip = os.getenv("VPS_IP", "212.227.104.207")
    health = check_vps_health(vps_ip)
    
    st.markdown(f"""
    <div class="card">
        <h4>Status VPS ({vps_ip})</h4>
        <p>Overall Status: <b>{'🟢 ONLINE' if health['status'] == 'Healthy' else '🔴 UNREACHABLE'}</b></p>
        <p>Port 80: {'✅' if health['details'].get(80) == 'Online' else '❌'}</p>
        <p>Port 443: {'✅' if health['details'].get(443) == 'Online' else '❌'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # GitHub Repos
    repos = get_latest_repos(5)
    st.markdown("#### Últimos 5 Repositorios Activos")
    if isinstance(repos, list):
        for repo in repos:
            st.markdown(f"""
            <div class="card">
                <a href="{repo['url']}" target="_blank" style="text-decoration: none; color: #58a6ff;">
                    <b>{repo['name']}</b>
                </a><br>
                <small>Language: {repo['language'] or 'N/A'} | Updated: {repo['pushed_at'][:10]}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error(f"GitHub Error: {repos.get('error')}")

# --- Módulo Financiero ---
with col2:
    st.subheader("📊 Mercados (España & Global)")
    
    # Financial Row 1: BTC & IBEX
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        btc_data = get_realtime_price("BTC-USD")
        if btc_data:
            st.metric("BTC-USD", f"${btc_data['price']:,.2f}")
    with fcol2:
        ibex_data = get_realtime_price("^IBEX")
        if ibex_data:
            st.metric("IBEX 35", f"{ibex_data['price']:,.2f}")

    # Spanish Stocks Summary
    st.markdown("#### Cotizaciones IBEX & Oro")
    spanish_stocks = get_spanish_stocks()
    scol1, scol2 = st.columns(2)
    
    # Split list for two columns
    items = list(spanish_stocks.items())
    for i, (name, data) in enumerate(items):
        target_col = scol1 if i % 2 == 0 else scol2
        with target_col:
            st.markdown(f"""
            <div class="card" style="padding: 10px; margin-bottom: 10px;">
                <small>{name}</small><br>
                <b>{data['price']:,.2f}</b>
            </div>
            """, unsafe_allow_html=True)
    
    # S&P 500 Chart (Main Reference)
    sp500_df = get_market_data("^GSPC")
    if sp500_df is not None:
        fig = create_stock_chart(sp500_df, "S&P 500 (Referencia Global)")
        st.plotly_chart(fig, use_container_width=True)

st.markdown("___")
col3, col4 = st.columns(2)

# --- Módulo de Información ---
with col3:
    tab_tech, tab_eco = st.tabs(["💻 Tecnología (Xataka)", "📈 Economía (Expansión)"])
    
    with tab_tech:
        news_tech = get_tech_news_es(4)
        if isinstance(news_tech, list):
            for item in news_tech:
                st.markdown(f"""
                <div class="card">
                    <a href="{item['link']}" target="_blank" style="text-decoration: none; color: #ffffff;">
                        <b>{item['title']}</b>
                    </a>
                </div>
                """, unsafe_allow_html=True)
    
    with tab_eco:
        news_eco = get_economic_news_es(4)
        if isinstance(news_eco, list):
            for item in news_eco:
                st.markdown(f"""
                <div class="card">
                    <a href="{item['link']}" target="_blank" style="text-decoration: none; color: #ffffff;">
                        <b>{item['title']}</b>
                    </a>
                </div>
                """, unsafe_allow_html=True)

# --- Módulo de Comunicación ---
with col4:
    st.subheader("📧 Inbox Summary")
    emails = get_inbox_summary(3)
    if isinstance(emails, list):
        for email in emails:
            st.markdown(f"""
            <div class="card">
                <b>From:</b> {email['from']}<br>
                <b>Subject:</b> {email['subject']}
            </div>
            """, unsafe_allow_html=True)
    elif "error" in emails:
        st.info("Configura las credenciales IMAP para ver tu bandeja de entrada.")
    else:
        st.warning("No se encontraron correos recientes.")
