import streamlit as st
import streamlit_authenticator as stauth
import os
import yaml
from yaml.loader import SafeLoader
from dotenv import load_dotenv
from utils.styles import apply_custom_styles
from services.github_service import get_latest_repos, check_vps_health
from services.finance_service import get_market_data, get_realtime_price, create_stock_chart
from services.news_service import get_tech_news
from services.mail_service import get_inbox_summary

# Load config
load_dotenv()

# Authentication Setup
config = {
    "credentials": {
        "usernames": {
            os.getenv("ADMIN_USER", "Miguel"): {
                "name": "Miguel",
                "password": stauth.Hasher([os.getenv("ADMIN_PASS", "Miguel_Navacedon26_Az")]).generate()[0]
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
    authenticator.logout('Logout', 'main')

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
    st.subheader("📊 Módulo Financiero")
    
    # BTC Price
    btc_data = get_realtime_price("BTC-USD")
    if btc_data:
        st.metric("BTC-USD (Bitcoin)", f"${btc_data['price']:,.2f}")
    
    # S&P 500 Chart
    sp500_df = get_market_data("^GSPC")
    if sp500_df is not None:
        fig = create_stock_chart(sp500_df, "S&P 500 Performance (1 Month)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No se pudo cargar los datos del S&P 500")

st.markdown("___")
col3, col4 = st.columns(2)

# --- Módulo de Información ---
with col3:
    st.subheader("📰 Tech News")
    news = get_tech_news(3)
    if isinstance(news, list):
        for item in news:
            st.markdown(f"""
            <div class="card">
                <a href="{item['link']}" target="_blank" style="text-decoration: none; color: #ffffff;">
                    <b>{item['title']}</b>
                </a><br>
                <small>Source: {item['source']}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error(f"News Error: {news.get('error')}")

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
