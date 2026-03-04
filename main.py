import streamlit as st
import streamlit_authenticator as stauth
import os
import yaml
from yaml.loader import SafeLoader
from dotenv import load_dotenv
from utils.styles import apply_custom_styles
from services.github_service import get_latest_repos, check_vps_health
from services.finance_service import get_realtime_price, get_spanish_stocks
from services.news_service import get_tech_news_es, get_economic_news_es

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
    
    # List of apps with specific user-provided URLs
    apps = [
        {"name": "📝 QUIZ", "url": "http://212.227.104.207/"},
        {"name": "🚗 VOLVO (Mantenimiento)", "url": "http://v84cks44c8wg0c0g4oc48sk8.212.227.104.207.sslip.io/pages/dashboard.php"},
        {"name": "📂 HISTÓRICO (Documental)", "url": "http://k84sgso8wgkgkow4kookkowg.212.227.104.207.sslip.io/"},
        {"name": "📊 FINANCIERO", "url": "http://k8c4co8gw8ggoco0w0w0w8kg.212.227.104.207.sslip.io/"}
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
col_left, col_right = st.columns([0.45, 0.55], gap="large")

# --- Left Column: Tech & Infra ---
with col_left:
    st.markdown("### 🛠️ Infraestructura")
    
    # VPS Status Card
    vps_ip = os.getenv("VPS_IP", "212.227.104.207")
    vps_status = check_vps_health(vps_ip)
    status_color = "#238636" if vps_status.get("status") == "Healthy" else "#da3633"
    
    st.markdown(f"""
    <div class="card" style="border-left: 5px solid {status_color};">
        <small style="color: #8b949e; text-transform: uppercase;">Estado del VPS</small><br>
        <span style="font-size: 1.2rem; font-weight: 600; color: #e6edf3;">{vps_ip}</span><br>
        <span style="color: {status_color}; font-size: 0.9rem;">● {'OPERATIVO' if vps_status.get('status') == 'Healthy' else 'INALCANZABLE'}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # GitHub Repos
    st.markdown("#### 🐙 Repositorios Recientes")
    repos = get_latest_repos(5)
    if isinstance(repos, list):
        for repo in repos:
            st.markdown(f"""
            <div class="card" style="padding: 15px; margin-bottom: 10px;">
                <a href="{repo['url']}" target="_blank" style="text-decoration: none; color: #58a6ff; font-weight: 600; font-size: 1rem;">
                    {repo['name']}
                </a><br>
                <small style="color: #8b949e;">{repo['language'] or 'Python'} • {repo['pushed_at'][:10]}</small>
            </div>
            """, unsafe_allow_html=True)

# --- Right Column: Finance ---
with col_right:
    st.markdown("### 📈 Mercados Españoles")
    
    # Financial Row 1: IBEX & BTC
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        ibex_data = get_realtime_price("^IBEX")
        if ibex_data:
            st.metric("IBEX 35", f"{ibex_data['price']:,.2f}")
    with fcol2:
        btc_data = get_realtime_price("BTC-USD")
        if btc_data:
            st.metric("Bitcoin (USD)", f"${btc_data['price']:,.2f}")

    # Spanish Stocks Grid
    st.markdown("#### Cotizaciones Selectas & Oro")
    spanish_stocks = get_spanish_stocks()
    scol1, scol2 = st.columns(2)
    
    items = list(spanish_stocks.items())
    for i, (name, data) in enumerate(items):
        target_col = scol1 if i % 2 == 0 else scol2
        with target_col:
            st.markdown(f"""
            <div class="card" style="padding: 18px; margin-bottom: 12px; text-align: center;">
                <div style="color: #8b949e; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px;">{name}</div>
                <div style="font-size: 1.4rem; font-weight: 600; color: #e6edf3; margin-top: 5px;">{data['price']:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("___")

# --- Bottom: News Full Width ---
st.markdown("### 📰 Actualidad y Economía")
tab_tech, tab_eco = st.tabs(["💻 Tecnología (Xataka)", "📉 Economía (Expansión)"])

with tab_tech:
    news_tech = get_tech_news_es(6)
    if isinstance(news_tech, list):
        # Create a cleaner grid for news
        for i in range(0, len(news_tech), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(news_tech):
                    item = news_tech[i+j]
                    with cols[j]:
                        st.markdown(f"""
                        <div class="card" style="height: 120px; display: flex; align-items: center; justify-content: center; text-align: center; padding: 15px;">
                            <a href="{item['link']}" target="_blank" style="text-decoration: none; color: #e6edf3; font-weight: 400; font-size: 0.9rem; line-height: 1.4;">
                                {item['title']}
                            </a>
                        </div>
                        """, unsafe_allow_html=True)

with tab_eco:
    news_eco = get_economic_news_es(6)
    if isinstance(news_eco, list):
        for i in range(0, len(news_eco), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(news_eco):
                    item = news_eco[i+j]
                    with cols[j]:
                        st.markdown(f"""
                        <div class="card" style="height: 120px; display: flex; align-items: center; justify-content: center; text-align: center; padding: 15px;">
                            <a href="{item['link']}" target="_blank" style="text-decoration: none; color: #e6edf3; font-weight: 400; font-size: 0.9rem; line-height: 1.4;">
                                {item['title']}
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
