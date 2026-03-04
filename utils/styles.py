import streamlit as st

def apply_custom_styles():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
        
        /* Main background & smooth transitions */
        .stApp {
            background: radial-gradient(circle at top left, #1a1c23, #0e1117);
            color: #e6edf3;
            font-family: 'Inter', sans-serif;
        }
        
        /* Premium Glassmorphism Cards */
        .card, div[data-testid="stMetricValue"] {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            margin-bottom: 20px;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        
        .card:hover {
            transform: scale(1.02);
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
        }
        
        /* Modern Metric Styling */
        div[data-testid="stMetricLabel"] {
            font-weight: 300;
            color: #8b949e;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 0.8rem !important;
        }
        
        div[data-testid="stMetricValue"] {
            background: none;
            padding: 0;
            border: none;
            box-shadow: none;
            font-weight: 600;
            font-size: 1.8rem !important;
            color: #58a6ff;
        }

        /* Sidebar Elegance */
        section[data-testid="stSidebar"] {
            background-color: rgba(22, 27, 34, 0.95);
            backdrop-filter: blur(15px);
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        /* Headers & Typography */
        h1, h2, h3 {
            background: linear-gradient(90deg, #58a6ff, #bc8cff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 600;
            margin-bottom: 25px !important;
        }
        
        /* Sidebar Buttons Modernization */
        .stButton>button {
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            background: rgba(255, 255, 255, 0.03);
            color: #e6edf3;
            transition: all 0.3s ease;
            width: 100%;
        }
        
        .stButton>button:hover {
            background: #58a6ff;
            color: white;
            border: none;
            box-shadow: 0 0 20px rgba(88, 166, 255, 0.4);
        }

        /* Custom scrollbar */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.2); }
        </style>
    """, unsafe_allow_html=True)
