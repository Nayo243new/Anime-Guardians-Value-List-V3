import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from PIL import Image
import io
import base64

from database import DatabaseManager
from auth import AuthManager
from tier_data import TierListManager
from trading import TradingManager
from admin import AdminManager
from achievements import AchievementManager
from utils import Utils

# Initialize managers
db = DatabaseManager()
auth_manager = AuthManager(db)
tier_manager = TierListManager(db)
trading_manager = TradingManager(db)
admin_manager = AdminManager(db)
achievement_manager = AchievementManager(db)
utils = Utils()

# Page configuration
st.set_page_config(
    page_title="Gaming Tier List Platform",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'virtual_currency' not in st.session_state:
        st.session_state.virtual_currency = 10000
    if 'selected_tier' not in st.session_state:
        st.session_state.selected_tier = "All"
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ""
    if 'admin_mode_enabled' not in st.session_state:
        st.session_state.admin_mode_enabled = False
    if 'remember_me' not in st.session_state:
        st.session_state.remember_me = False
    if 'visual_effects_enabled' not in st.session_state:
        st.session_state.visual_effects_enabled = True
    if 'current_theme' not in st.session_state:
        st.session_state.current_theme = "Futuristic"

def apply_visual_effects():
    """Apply custom CSS for visual effects"""
    if st.session_state.visual_effects_enabled:
        theme = st.session_state.current_theme
        
        if theme == "Futuristic":
            css_styles = """
            <style>
            /* Futuristic Glitch Effects */
            @keyframes glitch {
                0% { transform: translate(0); }
                20% { transform: translate(-3px, 3px); text-shadow: 3px 0 #ff0000, -3px 0 #00ffff; }
                40% { transform: translate(-3px, -3px); text-shadow: -3px 0 #ff0000, 3px 0 #00ffff; }
                60% { transform: translate(3px, 3px); text-shadow: 3px 0 #00ffff, -3px 0 #ff0000; }
                80% { transform: translate(3px, -3px); text-shadow: -3px 0 #00ffff, 3px 0 #ff0000; }
                100% { transform: translate(0); text-shadow: none; }
            }
            
            @keyframes cyber-scan {
                0% { background-position: 0% 0%; }
                100% { background-position: 100% 100%; }
            }
            
            @keyframes matrix-rain {
                0% { transform: translateY(-100vh); opacity: 0; }
                10% { opacity: 1; }
                90% { opacity: 1; }
                100% { transform: translateY(100vh); opacity: 0; }
            }
            
            @keyframes cyber-pulse {
                0% { 
                    box-shadow: 0 0 10px #00ffff, 0 0 20px #00ffff, 0 0 30px #00ffff, inset 0 0 30px rgba(0, 255, 255, 0.1);
                    border-color: #00ffff;
                }
                50% { 
                    box-shadow: 0 0 20px #00ffff, 0 0 40px #00ffff, 0 0 60px #00ffff, inset 0 0 50px rgba(0, 255, 255, 0.2);
                    border-color: #66ffff;
                }
                100% { 
                    box-shadow: 0 0 10px #00ffff, 0 0 20px #00ffff, 0 0 30px #00ffff, inset 0 0 30px rgba(0, 255, 255, 0.1);
                    border-color: #00ffff;
                }
            }
            
            /* Enhanced background with moving grid */
            body, .main {
                background: 
                    linear-gradient(90deg, rgba(0, 255, 255, 0.1) 1px, transparent 1px),
                    linear-gradient(rgba(0, 255, 255, 0.1) 1px, transparent 1px),
                    linear-gradient(135deg, #000000 0%, #001122 25%, #000033 50%, #001122 75%, #000000 100%);
                background-size: 50px 50px, 50px 50px, 100% 100%;
                animation: cyber-scan 20s linear infinite;
            }
            
            /* Main container */
            .main .block-container {
                background: 
                    linear-gradient(135deg, rgba(0, 0, 0, 0.9) 0%, rgba(26, 0, 51, 0.9) 50%, rgba(0, 0, 0, 0.9) 100%);
                border: 3px solid #00ffff;
                border-radius: 10px;
                animation: cyber-pulse 3s ease-in-out infinite;
                backdrop-filter: blur(10px);
                position: relative;
                overflow: hidden;
            }
            
            .main .block-container::before {
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: repeating-linear-gradient(
                    0deg,
                    transparent,
                    transparent 2px,
                    rgba(0, 255, 255, 0.03) 2px,
                    rgba(0, 255, 255, 0.03) 4px
                );
                animation: cyber-scan 10s linear infinite;
                pointer-events: none;
            }
            
            /* Enhanced glitch buttons */
            .stButton > button {
                background: linear-gradient(45deg, #000033 0%, #003366 50%, #000033 100%);
                border: 2px solid #00ffff;
                color: #00ffff;
                font-family: 'Courier New', monospace;
                text-transform: uppercase;
                letter-spacing: 3px;
                font-weight: bold;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .stButton > button::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(0, 255, 255, 0.3), transparent);
                transition: left 0.5s;
            }
            
            .stButton > button:hover {
                animation: glitch 0.5s ease-in-out infinite;
                background: linear-gradient(45deg, #003366 0%, #0066cc 50%, #003366 100%);
                text-shadow: 0 0 15px #00ffff, 2px 0 #ff0000, -2px 0 #00ff00;
                box-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
                transform: scale(1.05);
            }
            
            .stButton > button:hover::before {
                left: 100%;
            }
            """
        
        elif theme == "Aquatic":
            css_styles = """
            <style>
            /* Enhanced Aquatic Wave Effects */
            @keyframes wave {
                0% { transform: translateY(0px) rotateZ(0deg); }
                25% { transform: translateY(-8px) rotateZ(1deg); }
                50% { transform: translateY(-15px) rotateZ(0deg); }
                75% { transform: translateY(-8px) rotateZ(-1deg); }
                100% { transform: translateY(0px) rotateZ(0deg); }
            }
            
            @keyframes bubble-float {
                0% { transform: translateY(100vh) scale(0) rotate(0deg); opacity: 0; }
                10% { opacity: 0.8; }
                50% { opacity: 1; transform: translateY(50vh) scale(1) rotate(180deg); }
                90% { opacity: 0.8; }
                100% { transform: translateY(-10vh) scale(1.2) rotate(360deg); opacity: 0; }
            }
            
            @keyframes ocean-wave {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            
            @keyframes underwater-glow {
                0% { 
                    box-shadow: 0 0 30px rgba(0, 150, 255, 0.4), inset 0 0 50px rgba(0, 200, 255, 0.1);
                    border-color: #0096ff;
                }
                50% { 
                    box-shadow: 0 0 60px rgba(0, 200, 255, 0.7), inset 0 0 80px rgba(0, 220, 255, 0.2);
                    border-color: #00aaff;
                }
                100% { 
                    box-shadow: 0 0 30px rgba(0, 150, 255, 0.4), inset 0 0 50px rgba(0, 200, 255, 0.1);
                    border-color: #0096ff;
                }
            }
            
            /* Enhanced underwater background */
            body, .main {
                background: 
                    radial-gradient(ellipse at center, rgba(0, 150, 255, 0.1) 0%, transparent 50%),
                    linear-gradient(180deg, #000811 0%, #001122 20%, #002244 40%, #003366 60%, #002244 80%, #001122 100%);
                animation: ocean-wave 15s ease-in-out infinite;
            }
            
            /* Main container with water effects */
            .main .block-container {
                background: 
                    linear-gradient(135deg, rgba(0, 20, 40, 0.95) 0%, rgba(0, 40, 80, 0.9) 30%, rgba(0, 60, 120, 0.9) 70%, rgba(0, 40, 80, 0.95) 100%);
                border: 3px solid #00aaff;
                border-radius: 25px;
                animation: underwater-glow 4s ease-in-out infinite;
                backdrop-filter: blur(15px);
                position: relative;
                overflow: hidden;
            }
            
            .main .block-container::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 200%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(0, 170, 255, 0.1), transparent);
                animation: ocean-wave 8s linear infinite;
                pointer-events: none;
            }
            
            /* Enhanced aquatic buttons */
            .stButton > button {
                background: linear-gradient(45deg, #004466 0%, #0088cc 50%, #0066aa 100%);
                border: 2px solid #00aaff;
                border-radius: 30px;
                color: #ffffff;
                font-weight: bold;
                transition: all 0.4s ease;
                position: relative;
                overflow: hidden;
                animation: wave 3s ease-in-out infinite;
            }
            
            .stButton > button::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
                transition: left 0.6s;
            }
            
            .stButton > button:hover {
                transform: scale(1.1) translateY(-5px);
                box-shadow: 0 10px 40px rgba(0, 170, 255, 0.6), 0 0 20px rgba(0, 200, 255, 0.4);
                background: linear-gradient(45deg, #0066aa 0%, #00aaff 50%, #0088cc 100%);
                text-shadow: 0 0 10px rgba(255, 255, 255, 0.8);
            }
            
            .stButton > button:hover::before {
                left: 100%;
            }
            
            /* Enhanced bubble effects */
            .bubble {
                position: absolute;
                background: radial-gradient(circle, rgba(0, 170, 255, 0.4) 0%, rgba(0, 200, 255, 0.2) 50%, transparent 100%);
                border: 1px solid rgba(0, 170, 255, 0.3);
                border-radius: 50%;
                animation: bubble-float 12s infinite linear;
            }
            """
        
        elif theme == "Heavenly":
            css_styles = """
            <style>
            /* Enhanced Heavenly Divine Effects */
            @keyframes divine-glow {
                0% { 
                    box-shadow: 0 0 30px rgba(255, 215, 0, 0.4), 0 0 60px rgba(255, 255, 255, 0.3), inset 0 0 40px rgba(255, 215, 0, 0.1);
                    border-color: #ffd700;
                }
                50% { 
                    box-shadow: 0 0 60px rgba(255, 215, 0, 0.8), 0 0 100px rgba(255, 255, 255, 0.6), inset 0 0 80px rgba(255, 215, 0, 0.2);
                    border-color: #ffed4e;
                }
                100% { 
                    box-shadow: 0 0 30px rgba(255, 215, 0, 0.4), 0 0 60px rgba(255, 255, 255, 0.3), inset 0 0 40px rgba(255, 215, 0, 0.1);
                    border-color: #ffd700;
                }
            }
            
            @keyframes float-heaven {
                0% { transform: translateY(0px) scale(1); }
                25% { transform: translateY(-3px) scale(1.01); }
                50% { transform: translateY(-8px) scale(1.02); }
                75% { transform: translateY(-3px) scale(1.01); }
                100% { transform: translateY(0px) scale(1); }
            }
            
            @keyframes light-beam {
                0% { 
                    opacity: 0.3; 
                    transform: rotate(0deg) scale(1); 
                    filter: brightness(1);
                }
                50% { 
                    opacity: 0.9; 
                    transform: rotate(180deg) scale(1.2); 
                    filter: brightness(1.5);
                }
                100% { 
                    opacity: 0.3; 
                    transform: rotate(360deg) scale(1); 
                    filter: brightness(1);
                }
            }
            
            @keyframes celestial-shimmer {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            
            /* Enhanced heavenly background */
            body, .main {
                background: 
                    radial-gradient(ellipse at top, rgba(255, 215, 0, 0.1) 0%, transparent 60%),
                    radial-gradient(ellipse at bottom, rgba(255, 255, 255, 0.1) 0%, transparent 60%),
                    linear-gradient(135deg, #f8f9fa 0%, #fff8dc 25%, #f0f8ff 50%, #fff8dc 75%, #f8f9fa 100%);
                animation: celestial-shimmer 20s ease-in-out infinite;
            }
            
            /* Enhanced main container */
            .main .block-container {
                background: 
                    linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 248, 220, 0.9) 30%, rgba(240, 248, 255, 0.9) 70%, rgba(255, 255, 255, 0.95) 100%);
                border: 4px solid #ffd700;
                border-radius: 20px;
                animation: divine-glow 5s ease-in-out infinite;
                color: #333333;
                backdrop-filter: blur(10px);
                position: relative;
                overflow: hidden;
            }
            
            .main .block-container::before {
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: 
                    radial-gradient(circle, rgba(255, 215, 0, 0.05) 0%, transparent 30%),
                    linear-gradient(45deg, transparent 40%, rgba(255, 255, 255, 0.1) 50%, transparent 60%);
                animation: light-beam 12s linear infinite;
                pointer-events: none;
            }
            
            /* Enhanced divine buttons */
            .stButton > button {
                background: linear-gradient(45deg, #ffd700 0%, #ffffff 30%, #ffed4e 70%, #ffd700 100%);
                border: 3px solid #ffd700;
                border-radius: 35px;
                color: #333333;
                font-weight: bold;
                font-size: 1.1em;
                transition: all 0.4s ease;
                position: relative;
                overflow: hidden;
                animation: float-heaven 4s ease-in-out infinite;
                text-shadow: 0 0 5px rgba(255, 255, 255, 0.8);
            }
            
            .stButton > button::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6), transparent);
                transition: left 0.8s;
            }
            
            .stButton > button:hover {
                box-shadow: 0 0 40px rgba(255, 215, 0, 0.9), 0 15px 25px rgba(255, 215, 0, 0.3);
                transform: scale(1.15) translateY(-8px);
                background: linear-gradient(45deg, #ffed4e 0%, #ffffff 30%, #ffd700 70%, #ffed4e 100%);
                text-shadow: 0 0 15px rgba(255, 255, 255, 1), 0 0 25px rgba(255, 215, 0, 0.8);
            }
            
            .stButton > button:hover::before {
                left: 100%;
            }
            
            /* Enhanced light rays */
            .light-ray {
                position: absolute;
                background: linear-gradient(90deg, transparent, rgba(255, 215, 0, 0.4), rgba(255, 255, 255, 0.3), rgba(255, 215, 0, 0.4), transparent);
                animation: light-beam 15s linear infinite;
                filter: blur(1px);
            }
            """
        
        else:  # Default futuristic theme
            css_styles = """
            <style>
            @keyframes glow {
                0% { box-shadow: 0 0 5px #00ff88; }
                50% { box-shadow: 0 0 20px #00ff88, 0 0 30px #00ff88; }
                100% { box-shadow: 0 0 5px #00ff88; }
            }
            
            .main .block-container {
                background: linear-gradient(135deg, #1e1e1e 0%, #2d1b69 50%, #1e1e1e 100%);
                border-radius: 15px;
                padding: 2rem;
            }
            """
        
        # Common styles for all themes
        common_styles = """
        
        /* Sidebar styling */
        .css-1d391kg {
            background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
            border-right: 2px solid currentColor;
        }
        
        /* Metric styling */
        .metric-container {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid currentColor;
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
        }
        
        /* Text glow effects */
        .glow-text {
            text-shadow: 0 0 10px currentColor, 0 0 20px currentColor;
        }
        
        /* Enhanced Card hover effects */
        .character-card {
            background: rgba(255, 255, 255, 0.05);
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            padding: 1.5rem;
            margin: 0.8rem 0;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            cursor: pointer;
        }
        
        .character-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
            transition: left 0.6s;
        }
        
        .character-card:hover {
            border-color: currentColor;
            box-shadow: 
                0 10px 40px rgba(255, 255, 255, 0.2),
                0 0 30px currentColor,
                inset 0 0 20px rgba(255, 255, 255, 0.1);
            transform: translateY(-8px) scale(1.02);
            background: rgba(255, 255, 255, 0.1);
        }
        
        .character-card:hover::before {
            left: 100%;
        }
        
        /* Enhanced form elements */
        .stSelectbox > div > div {
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            transition: all 0.3s ease;
        }
        
        .stSelectbox > div > div:hover {
            border-color: currentColor;
            box-shadow: 0 0 15px rgba(255, 255, 255, 0.2);
            transform: scale(1.02);
        }
        
        /* Enhanced metrics */
        .metric-container {
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid currentColor;
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .metric-container:hover {
            transform: scale(1.05);
            box-shadow: 0 0 25px currentColor;
            background: rgba(255, 255, 255, 0.15);
        }
        
        /* Tier colors with glow */
        .tier-sp { color: #ff6b6b; text-shadow: 0 0 10px #ff6b6b; }
        .tier-s { color: #ff8e53; text-shadow: 0 0 10px #ff8e53; }
        .tier-a-plus { color: #ffd93d; text-shadow: 0 0 10px #ffd93d; }
        .tier-a { color: #6bcf7f; text-shadow: 0 0 10px #6bcf7f; }
        .tier-a-minus { color: #4ecdc4; text-shadow: 0 0 10px #4ecdc4; }
        
        /* Form styling */
        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            color: white;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: currentColor;
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
        }
        
        /* Theme-specific particles */
        .particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
        }
        
        .particle {
            position: absolute;
            border-radius: 50%;
        }
        </style>
        """
        
        # Add theme-specific particle effects
        if theme == "Aquatic":
            particles_html = """
            <div class="particles">
                <div class="bubble" style="left: 10%; width: 8px; height: 8px; animation-delay: 0s;"></div>
                <div class="bubble" style="left: 20%; width: 12px; height: 12px; animation-delay: 2s;"></div>
                <div class="bubble" style="left: 30%; width: 6px; height: 6px; animation-delay: 4s;"></div>
                <div class="bubble" style="left: 40%; width: 10px; height: 10px; animation-delay: 6s;"></div>
                <div class="bubble" style="left: 50%; width: 8px; height: 8px; animation-delay: 8s;"></div>
                <div class="bubble" style="left: 60%; width: 14px; height: 14px; animation-delay: 10s;"></div>
                <div class="bubble" style="left: 70%; width: 6px; height: 6px; animation-delay: 12s;"></div>
                <div class="bubble" style="left: 80%; width: 10px; height: 10px; animation-delay: 14s;"></div>
                <div class="bubble" style="left: 90%; width: 8px; height: 8px; animation-delay: 16s;"></div>
            </div>
            """
        elif theme == "Heavenly":
            particles_html = """
            <div class="particles">
                <div class="light-ray" style="left: 10%; width: 2px; height: 100%; animation-delay: 0s;"></div>
                <div class="light-ray" style="left: 30%; width: 1px; height: 100%; animation-delay: 3s;"></div>
                <div class="light-ray" style="left: 50%; width: 3px; height: 100%; animation-delay: 6s;"></div>
                <div class="light-ray" style="left: 70%; width: 2px; height: 100%; animation-delay: 9s;"></div>
                <div class="light-ray" style="left: 90%; width: 1px; height: 100%; animation-delay: 12s;"></div>
            </div>
            """
        else:  # Futuristic or default
            particles_html = """
            <div class="particles">
                <div class="particle" style="left: 10%; width: 2px; height: 2px; background: #00ffff; animation: cyber-pulse 3s infinite;"></div>
                <div class="particle" style="left: 30%; width: 1px; height: 1px; background: #00ffff; animation: cyber-pulse 4s infinite;"></div>
                <div class="particle" style="left: 50%; width: 3px; height: 3px; background: #00ffff; animation: cyber-pulse 2s infinite;"></div>
                <div class="particle" style="left: 70%; width: 2px; height: 2px; background: #00ffff; animation: cyber-pulse 5s infinite;"></div>
                <div class="particle" style="left: 90%; width: 1px; height: 1px; background: #00ffff; animation: cyber-pulse 3s infinite;"></div>
            </div>
            """
        
        st.markdown(css_styles + common_styles, unsafe_allow_html=True)
        st.markdown(particles_html, unsafe_allow_html=True)

def main():
    initialize_session_state()
    apply_visual_effects()
    
    # Authentication check
    if not st.session_state.authenticated:
        show_auth_page()
        return
    
    # Main navigation
    st.sidebar.title(f"Welcome, {st.session_state.username}!")
    st.sidebar.write(f"Role: {st.session_state.user_role}")
    st.sidebar.write(f"Virtual Currency: 💰 {st.session_state.virtual_currency:,}")
    
    # Navigation menu
    pages = ["Tier Lists", "Trading Simulator", "W/L Tracking", "Profile", "Settings"]
    
    # Add admin page if user is admin or admin mode is enabled
    if st.session_state.user_role == "Admin" or st.session_state.admin_mode_enabled:
        pages.append("Admin Panel")
    
    selected_page = st.sidebar.selectbox("Navigation", pages)
    
    # Logout button
    if st.sidebar.button("Logout"):
        auth_manager.logout()
        st.rerun()
    
    # Route to selected page
    if selected_page == "Tier Lists":
        show_tier_lists()
    elif selected_page == "Trading Simulator":
        show_trading_simulator()
    elif selected_page == "W/L Tracking":
        show_wl_tracking()
    elif selected_page == "Profile":
        show_profile()
    elif selected_page == "Settings":
        show_settings()
    elif selected_page == "Admin Panel" and (st.session_state.user_role == "Admin" or st.session_state.admin_mode_enabled):
        show_admin_panel()

def show_auth_page():
    """Display authentication page"""
    # Enhanced title with glow effect
    if st.session_state.visual_effects_enabled:
        st.markdown('<h1 class="glow-text" style="text-align: center;">🎮 Gaming Tier List Platform</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; font-size: 1.2em; color: #00ff88;">Welcome to the ultimate gaming tier list and trading platform!</p>', unsafe_allow_html=True)
    else:
        st.title("🎮 Gaming Tier List Platform")
        st.write("Welcome to the ultimate gaming tier list and trading platform!")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            remember_me = st.checkbox("Remember me", value=st.session_state.remember_me)
            login_button = st.form_submit_button("Login")
            
            if login_button:
                st.session_state.remember_me = remember_me
                if auth_manager.login(username, password):
                    st.success("Login successful!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    with tab2:
        st.subheader("Sign Up")
        with st.form("signup_form"):
            new_username = st.text_input("Choose Username")
            email = st.text_input("Email")
            new_password = st.text_input("Choose Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            signup_button = st.form_submit_button("Sign Up")
            
            if signup_button:
                if new_password != confirm_password:
                    st.error("Passwords don't match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                elif auth_manager.register(new_username, email, new_password):
                    st.success("Account created successfully! You can now log in.")
                else:
                    st.error("Username or email already exists")

def show_tier_lists():
    """Display tier lists with filtering and search"""
    st.title("🏆 Character Tier Lists")
    
    # Get tier list data
    tier_data = tier_manager.get_tier_data()
    
    if tier_data.empty:
        st.error("No tier list data available")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tiers = ["All"] + sorted(tier_data['tier'].unique().tolist())
        selected_tier = st.selectbox("Filter by Tier", tiers, key="tier_filter")
    
    with col2:
        search_query = st.text_input("Search Characters", key="search_input")
    
    with col3:
        sort_options = ["Name", "Value", "Demand", "Tier"]
        sort_by = st.selectbox("Sort by", sort_options)
    
    # Apply filters
    filtered_data = tier_data.copy()
    
    if selected_tier != "All":
        filtered_data = filtered_data[filtered_data['tier'] == selected_tier]
    
    if search_query:
        filtered_data = filtered_data[
            filtered_data['name'].str.contains(search_query, case=False, na=False)
        ]
    
    # Sort data
    if sort_by == "Name":
        filtered_data = filtered_data.sort_values('name')
    elif sort_by == "Value":
        filtered_data = filtered_data.sort_values('value', ascending=False)
    elif sort_by == "Demand":
        filtered_data = filtered_data.sort_values('demand', ascending=False)
    elif sort_by == "Tier":
        tier_order = {"S+": 0, "S": 1, "A+": 2, "A": 3, "A-": 4}
        filtered_data['tier_order'] = filtered_data['tier'].map(tier_order)
        filtered_data = filtered_data.sort_values('tier_order')
        filtered_data = filtered_data.drop('tier_order', axis=1)
    
    # Display tier list
    if not filtered_data.empty:
        st.subheader(f"Showing {len(filtered_data)} characters")
        
        # Group by tier for better display
        for tier in ["S+", "S", "A+", "A", "A-"]:
            tier_data_subset = filtered_data[filtered_data['tier'] == tier]
            if not tier_data_subset.empty:
                # Color coding for tiers
                tier_colors = {
                    "S+": "#FF6B6B",  # Red
                    "S": "#FF8E53",   # Orange
                    "A+": "#FFD93D",  # Yellow
                    "A": "#6BCF7F",   # Green
                    "A-": "#4ECDC4"   # Teal
                }
                
                st.markdown(f"### {tier} Tier")
                
                # Display as enhanced cards with hover effects
                for idx, row in tier_data_subset.iterrows():
                    tier_class = f"tier-{tier.lower().replace('+', '-plus').replace('-', '-minus')}"
                    
                    if st.session_state.visual_effects_enabled:
                        card_html = f"""
                        <div class="character-card">
                            <div style="display: flex; align-items: center; gap: 1rem;">
                                <div style="flex: 2;">
                                    <h4 class="{tier_class}">{row['name']}</h4>
                                </div>
                                <div style="flex: 1; text-align: center;">
                                    <span style="color: #00ff88;">💰 {row['value']:,}</span>
                                </div>
                                <div style="flex: 1; text-align: center;">
                                    {"🔥" if row['demand'] >= 8 else "📈" if row['demand'] >= 5 else "📊"} {row['demand']}
                                </div>
                                <div style="flex: 1; text-align: center;">
                                    {"🔺" if row['trend'] == "Overpriced" else "⚖️" if row['trend'] == "Stable" else "🔻"} {row['trend']}
                                </div>
                                <div style="flex: 3;">
                                    <small>{row['information']}</small>
                                </div>
                            </div>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
                    else:
                        with st.container():
                            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 3])
                            
                            with col1:
                                st.markdown(f"**{row['name']}**")
                            with col2:
                                st.write(f"💰 {row['value']:,}")
                            with col3:
                                demand_emoji = "🔥" if row['demand'] >= 8 else "📈" if row['demand'] >= 5 else "📊"
                                st.write(f"{demand_emoji} {row['demand']}")
                            with col4:
                                trend_emoji = "🔺" if row['trend'] == "Overpriced" else "⚖️" if row['trend'] == "Stable" else "🔻"
                                st.write(f"{trend_emoji} {row['trend']}")
                            with col5:
                                st.write(row['information'])
                            
                            st.divider()
    else:
        st.info("No characters found matching your criteria")

def show_trading_simulator():
    """Display trading simulator"""
    st.title("💹 Trading Simulator")
    
    # Get user's portfolio
    portfolio = trading_manager.get_user_portfolio(st.session_state.user_id)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("💰 Your Portfolio")
        
        if st.session_state.visual_effects_enabled:
            st.markdown(f'<div class="metric-container"><h3 class="glow-text">Virtual Currency: ${st.session_state.virtual_currency:,}</h3></div>', unsafe_allow_html=True)
        else:
            st.metric("Virtual Currency", f"${st.session_state.virtual_currency:,}")
        
        if portfolio is not None and not portfolio.empty:
            total_value = 0
            for _, item in portfolio.iterrows():
                current_price = tier_manager.get_character_value(item['character_name'])
                item_value = current_price * item['quantity']
                total_value += item_value
                
                if st.session_state.visual_effects_enabled:
                    portfolio_card = f"""
                    <div class="character-card" style="margin: 0.5rem 0;">
                        <h4 style="color: #00ff88; margin: 0;">{item['character_name']}</h4>
                        <p style="margin: 0.2rem 0;">Quantity: {item['quantity']} | Value: ${item_value:,}</p>
                    </div>
                    """
                    st.markdown(portfolio_card, unsafe_allow_html=True)
                else:
                    st.write(f"**{item['character_name']}**")
                    st.write(f"Quantity: {item['quantity']} | Value: ${item_value:,}")
                    st.divider()
            
            if st.session_state.visual_effects_enabled:
                st.markdown(f'<div class="metric-container"><h4>Portfolio Value: ${total_value:,}</h4></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-container"><h4 class="glow-text">Total Assets: ${st.session_state.virtual_currency + total_value:,}</h4></div>', unsafe_allow_html=True)
            else:
                st.metric("Portfolio Value", f"${total_value:,}")
                st.metric("Total Assets", f"${st.session_state.virtual_currency + total_value:,}")
        else:
            st.info("Your portfolio is empty. Start trading to build your collection!")
    
    with col2:
        st.subheader("🛒 Trading Market")
        
        # Get available characters for trading
        tier_data = tier_manager.get_tier_data()
        
        if not tier_data.empty:
            character_names = tier_data['name'].tolist()
            selected_character = st.selectbox("Select Character", character_names)
            
            if selected_character:
                char_data = tier_data[tier_data['name'] == selected_character].iloc[0]
                
                st.write(f"**{char_data['name']}**")
                st.write(f"Tier: {char_data['tier']}")
                st.write(f"Current Price: ${char_data['value']:,}")
                st.write(f"Demand: {char_data['demand']}/10")
                st.write(f"Trend: {char_data['trend']}")
                
                # Trading actions
                action = st.radio("Action", ["Buy", "Sell"])
                quantity = st.number_input("Quantity", min_value=1, value=1)
                
                total_cost = char_data['value'] * quantity
                
                if action == "Buy":
                    st.write(f"Total Cost: ${total_cost:,}")
                    if st.button("Execute Buy Order"):
                        if trading_manager.buy_character(
                            st.session_state.user_id, 
                            selected_character, 
                            quantity, 
                            char_data['value']
                        ):
                            st.success(f"Successfully bought {quantity}x {selected_character}!")
                            # Update virtual currency
                            st.session_state.virtual_currency -= total_cost
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Insufficient funds!")
                
                else:  # Sell
                    # Check if user owns this character
                    owned_quantity = trading_manager.get_owned_quantity(
                        st.session_state.user_id, selected_character
                    )
                    
                    if owned_quantity >= quantity:
                        total_value = char_data['value'] * quantity
                        st.write(f"Total Value: ${total_value:,}")
                        
                        if st.button("Execute Sell Order"):
                            if trading_manager.sell_character(
                                st.session_state.user_id, 
                                selected_character, 
                                quantity, 
                                char_data['value']
                            ):
                                st.success(f"Successfully sold {quantity}x {selected_character}!")
                                # Update virtual currency
                                st.session_state.virtual_currency += total_value
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Error executing sell order!")
                    else:
                        st.error(f"You only own {owned_quantity}x {selected_character}")

def show_wl_tracking():
    """Display Win/Loss tracking"""
    st.title("📊 Win/Loss Tracking")
    
    # Get user's trading history
    trades = trading_manager.get_user_trades(st.session_state.user_id)
    
    if trades is None or trades.empty:
        st.info("No trading history available yet. Start trading to see your performance!")
        return
    
    # Calculate statistics
    total_trades = len(trades)
    profitable_trades = len(trades[trades['profit_loss'] > 0])
    losing_trades = len(trades[trades['profit_loss'] < 0])
    total_profit_loss = trades['profit_loss'].sum()
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Trades", total_trades)
    with col2:
        st.metric("Profitable Trades", profitable_trades)
    with col3:
        st.metric("Losing Trades", losing_trades)
    with col4:
        win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
        st.metric("Win Rate", f"{win_rate:.1f}%")
    
    # Profit/Loss over time chart
    st.subheader("📈 Performance Over Time")
    
    trades_sorted = trades.sort_values('trade_date')
    trades_sorted['cumulative_pl'] = trades_sorted['profit_loss'].cumsum()
    
    fig = px.line(
        trades_sorted, 
        x='trade_date', 
        y='cumulative_pl',
        title='Cumulative Profit/Loss Over Time',
        labels={'cumulative_pl': 'Cumulative P&L ($)', 'trade_date': 'Date'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Trading history table
    st.subheader("📋 Recent Trades")
    
    display_trades = trades.head(20).copy()
    display_trades['profit_loss'] = display_trades['profit_loss'].apply(lambda x: f"${x:,.2f}")
    display_trades['total_value'] = display_trades['total_value'].apply(lambda x: f"${x:,.2f}")
    
    st.dataframe(
        display_trades[['trade_date', 'character_name', 'action', 'quantity', 'price', 'total_value', 'profit_loss']],
        use_container_width=True
    )

def show_profile():
    """Display user profile with achievement system"""
    if not st.session_state.logged_in:
        st.warning("Please log in to view your profile.")
        return
    
    st.title("👤 Profile")
    
    user_id = st.session_state.user_id
    profile_data = auth_manager.get_user_profile(user_id)
    
    if not profile_data:
        st.error("Failed to load profile data.")
        return
    
    # Check for new achievements
    newly_earned = achievement_manager.check_and_award_achievements(user_id)
    if newly_earned:
        for ach_id in newly_earned:
            ach_config = achievement_manager.achievements_config[ach_id]
            st.success(f"🏆 Achievement Unlocked: **{ach_config['name']}** - {ach_config['description']}")
    
    # Create tabs for profile sections
    tab1, tab2, tab3, tab4 = st.tabs(["Profile Info", "Achievements", "Trading Stats", "Portfolio"])
    
    with tab1:
        # Profile header
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Profile Photo")
            
            # Display current profile photo
            if profile_data.get('profile_photo'):
                try:
                    # Decode base64 image
                    image_data = base64.b64decode(profile_data['profile_photo'])
                    image = Image.open(io.BytesIO(image_data))
                    st.image(image, width=200)
                except:
                    st.write("📷 No photo")
            else:
                st.write("📷 No photo uploaded")
            
            # Photo upload
            uploaded_file = st.file_uploader("Upload Profile Photo", type=['jpg', 'jpeg', 'png'])
            if uploaded_file is not None:
                # Process and save image
                image = Image.open(uploaded_file)
                # Resize image
                image.thumbnail((300, 300), Image.Resampling.LANCZOS)
                
                # Convert to base64
                buffer = io.BytesIO()
                image.save(buffer, format="PNG")
                img_str = base64.b64encode(buffer.getvalue()).decode()
                
                if st.button("Save Photo"):
                    if auth_manager.update_profile_photo(user_id, img_str):
                        st.success("Profile photo updated!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to update photo")
        
        with col2:
            st.subheader("Profile Information")
            
            with st.form("profile_form"):
                display_name = st.text_input(
                    "Display Name", 
                    value=profile_data.get('display_name', st.session_state.username)
                )
                bio = st.text_area("Bio", value=profile_data.get('bio', ''))
                
                # Profile stats (read-only)
                st.write("**Account Statistics:**")
                st.write(f"Username: {st.session_state.username}")
                st.write(f"Role: {st.session_state.user_role}")
                st.write(f"Virtual Currency: {utils.format_currency(profile_data['virtual_currency'])}")
                st.write(f"Member since: {profile_data.get('created_at', 'Unknown')}")
                
                if st.form_submit_button("Update Profile"):
                    if auth_manager.update_profile(user_id, display_name, bio):
                        st.success("Profile updated successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to update profile")
    
    with tab2:
        # Achievement System
        st.markdown("### 🏆 Achievement System")
        
        # Get achievement stats
        achievement_stats = achievement_manager.get_achievement_stats(user_id)
        
        # Achievement overview
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Points", achievement_stats['total_points'])
        
        with col2:
            completion = achievement_stats['completion_percentage']
            st.metric("Completion", f"{completion:.1f}%")
        
        with col3:
            earned = achievement_stats['earned_achievements']
            total = achievement_stats['total_achievements']
            st.metric("Achievements", f"{earned}/{total}")
        
        # Progress bar
        progress = achievement_stats['completion_percentage'] / 100
        st.progress(progress)
        
        # Rarity breakdown
        if achievement_stats['rarity_breakdown']:
            st.markdown("#### Badge Collection")
            rarity_cols = st.columns(len(achievement_stats['rarity_breakdown']))
            
            rarity_colors = {
                'Common': '#28a745',
                'Rare': '#007bff', 
                'Epic': '#6f42c1',
                'Legendary': '#ffc107'
            }
            
            for i, (rarity, count) in enumerate(achievement_stats['rarity_breakdown'].items()):
                with rarity_cols[i]:
                    color = rarity_colors.get(rarity, '#6c757d')
                    st.markdown(f"""
                    <div style="text-align: center; padding: 10px; border-radius: 10px; 
                                background: linear-gradient(135deg, {color}22, {color}11); 
                                border: 2px solid {color};">
                        <h4 style="color: {color}; margin: 0;">{count}</h4>
                        <p style="margin: 0; font-size: 0.9em;">{rarity}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Recent achievements
        if achievement_stats['recent_achievements']:
            st.markdown("#### Recent Achievements")
            for ach in achievement_stats['recent_achievements'][:3]:
                rarity_color = {'Common': '#28a745', 'Rare': '#007bff', 'Epic': '#6f42c1', 'Legendary': '#ffc107'}.get(ach['rarity'], '#6c757d')
                
                with st.container():
                    st.markdown(f"""
                    <div style="padding: 15px; margin: 10px 0; border-radius: 15px; 
                                background: linear-gradient(135deg, {rarity_color}22, {rarity_color}11); 
                                border-left: 4px solid {rarity_color};">
                        <div style="display: flex; align-items: center; gap: 15px;">
                            <span style="font-size: 2em;">{ach['icon']}</span>
                            <div>
                                <h4 style="margin: 0; color: {rarity_color};">{ach['name']}</h4>
                                <p style="margin: 5px 0; opacity: 0.8;">{ach['description']}</p>
                                <small style="opacity: 0.6;">
                                    {ach['rarity']} • {ach['points']} points • 
                                    {utils.format_time_ago(ach['earned_date'])}
                                </small>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # All achievements
        st.markdown("---")
        st.markdown("#### All Achievements")
        
        # Filter achievements
        filter_option = st.selectbox("Filter by:", ["All", "Earned", "Not Earned", "Common", "Rare", "Epic", "Legendary"])
        
        achievements = achievement_manager.get_user_achievements(user_id)
        
        if filter_option != "All":
            if filter_option == "Earned":
                achievements = [a for a in achievements if a['earned']]
            elif filter_option == "Not Earned":
                achievements = [a for a in achievements if not a['earned']]
            else:
                achievements = [a for a in achievements if a['rarity'] == filter_option]
        
        # Display achievements in a grid
        cols = st.columns(2)
        
        for i, ach in enumerate(achievements):
            with cols[i % 2]:
                rarity_color = {'Common': '#28a745', 'Rare': '#007bff', 'Epic': '#6f42c1', 'Legendary': '#ffc107'}.get(ach['rarity'], '#6c757d')
                opacity = "1" if ach['earned'] else "0.5"
                
                progress_bar = ""
                if not ach['earned'] and ach['progress'].get('percentage', 0) > 0:
                    progress_bar = f"""
                    <div style="margin-top: 8px;">
                        <small>Progress: {ach["progress"].get("current", 0)}/{ach["progress"].get("target", 1)} ({ach["progress"].get("percentage", 0):.1f}%)</small>
                        <div style="background: rgba(255,255,255,0.2); border-radius: 10px; height: 6px; margin-top: 3px;">
                            <div style="background: {rarity_color}; height: 6px; border-radius: 10px; width: {ach["progress"].get("percentage", 0)}%;"></div>
                        </div>
                    </div>
                    """
                
                st.markdown(f"""
                <div style="padding: 15px; margin: 10px 0; border-radius: 15px; 
                            background: linear-gradient(135deg, {rarity_color}22, {rarity_color}11); 
                            border: 2px solid {rarity_color}; opacity: {opacity};">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <span style="font-size: 2.5em;">{ach['icon']}</span>
                        <div style="flex: 1;">
                            <h4 style="margin: 0; color: {rarity_color};">{ach['name']}</h4>
                            <p style="margin: 5px 0; opacity: 0.8;">{ach['description']}</p>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <small style="opacity: 0.6;">{ach['rarity']} • {ach['points']} points</small>
                                {"✅" if ach['earned'] else ""}
                            </div>
                            {progress_bar}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with tab3:
        # Trading Statistics
        st.markdown("### 📊 Trading Statistics")
        
        trading_stats = trading_manager.get_trading_statistics(user_id)
        portfolio_value = trading_manager.get_portfolio_value(user_id)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Trades", trading_stats.get('total_trades', 0))
        
        with col2:
            profit_loss = trading_stats.get('total_profit_loss', 0)
            st.metric("Total P&L", utils.format_currency(profit_loss), 
                     delta=utils.format_currency(profit_loss) if profit_loss != 0 else None)
        
        with col3:
            win_rate = trading_stats.get('win_rate', 0)
            st.metric("Win Rate", f"{win_rate:.1f}%")
        
        with col4:
            st.metric("Portfolio Value", utils.format_currency(portfolio_value))
        
        # Recent Trades
        st.markdown("### 📈 Recent Trades")
        
        recent_trades = trading_manager.get_user_trades(user_id, limit=10)
        
        if recent_trades:
            trades_df = pd.DataFrame(recent_trades)
            trades_df['price'] = trades_df['price'].apply(lambda x: utils.format_currency(x))
            trades_df['total_amount'] = trades_df['total_amount'].apply(lambda x: utils.format_currency(x))
            trades_df['trade_date'] = pd.to_datetime(trades_df['trade_date']).dt.strftime('%Y-%m-%d %H:%M')
            
            st.dataframe(trades_df[['character_name', 'trade_type', 'quantity', 'price', 'total_amount', 'trade_date']], 
                        use_container_width=True)
        else:
            st.info("No trading history available.")
    
    with tab4:
        # Portfolio Overview
        st.markdown("### 💼 Portfolio Overview")
        
        portfolio = trading_manager.get_user_portfolio(user_id)
        
        if portfolio:
            # Create portfolio chart
            tier_data = tier_manager.get_tier_data()
            chart = utils.create_portfolio_pie_chart(portfolio, tier_data)
            if chart:
                st.plotly_chart(chart, use_container_width=True)
            
            # Portfolio table
            portfolio_df = pd.DataFrame(portfolio)
            portfolio_df['Total Value'] = portfolio_df['quantity'] * portfolio_df['current_price']
            portfolio_df['Total Value'] = portfolio_df['Total Value'].apply(lambda x: utils.format_currency(x))
            portfolio_df['Current Price'] = portfolio_df['current_price'].apply(lambda x: utils.format_currency(x))
            
            st.dataframe(portfolio_df[['character_name', 'quantity', 'Current Price', 'Total Value']], 
                        use_container_width=True)
        else:
            st.info("No portfolio data available. Start trading to build your portfolio!")

def show_settings():
    """Display settings page"""
    st.title("⚙️ Settings")
    
    # Theme settings
    st.subheader("🎨 Appearance")
    theme_options = ["Futuristic", "Aquatic", "Heavenly"]
    current_theme = st.selectbox(
        "Visual Theme", 
        theme_options,
        index=theme_options.index(st.session_state.current_theme),
        help="Choose your visual theme style"
    )
    
    # Update theme if changed
    if current_theme != st.session_state.current_theme:
        st.session_state.current_theme = current_theme
        st.rerun()
    
    # Display settings
    st.subheader("📱 Display")
    visual_effects = st.checkbox("Enable Visual Effects & Animations", value=st.session_state.visual_effects_enabled)
    compact_mode = st.checkbox("Compact mode", value=False)
    
    # Update visual effects setting
    if visual_effects != st.session_state.visual_effects_enabled:
        st.session_state.visual_effects_enabled = visual_effects
        st.rerun()
    
    # Trading settings
    st.subheader("💹 Trading")
    auto_refresh = st.checkbox("Auto-refresh prices", value=True)
    confirmation_dialogs = st.checkbox("Show confirmation dialogs", value=True)
    
    # Notification settings
    st.subheader("🔔 Notifications")
    price_alerts = st.checkbox("Price change alerts", value=False)
    trade_notifications = st.checkbox("Trade notifications", value=True)
    
    # Privacy settings
    st.subheader("🔒 Privacy")
    public_profile = st.checkbox("Public profile", value=True)
    show_trading_stats = st.checkbox("Show trading statistics", value=True)
    
    # Account settings
    st.subheader("👤 Account")
    
    with st.expander("Change Password"):
        with st.form("password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_new_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Change Password"):
                if new_password != confirm_new_password:
                    st.error("New passwords don't match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                elif auth_manager.change_password(st.session_state.user_id, current_password, new_password):
                    st.success("Password changed successfully!")
                else:
                    st.error("Current password is incorrect")
    
    # Admin Mode Section
    st.subheader("🔐 Admin Mode")
    
    if not st.session_state.admin_mode_enabled:
        with st.expander("Enter Admin Mode"):
            with st.form("admin_code_form"):
                secret_code = st.text_input("Enter Secret Code", type="password", help="Admin access code required")
                
                if st.form_submit_button("Enable Admin Mode"):
                    if secret_code == "0202024":
                        st.session_state.admin_mode_enabled = True
                        st.success("Admin mode enabled! You now have access to the Admin Panel.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Invalid secret code")
    else:
        st.success("Admin mode is currently enabled")
        if st.button("Disable Admin Mode"):
            st.session_state.admin_mode_enabled = False
            st.success("Admin mode disabled")
            time.sleep(1)
            st.rerun()
    
    # Save settings
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")

def show_admin_panel():
    """Display admin panel (Admin only)"""
    if st.session_state.user_role != "Admin" and not st.session_state.admin_mode_enabled:
        st.error("Access denied. Admin privileges required.")
        return
    
    st.title("🛠️ Admin Panel")
    
    admin_tabs = st.tabs([
        "User Management", 
        "Data Analytics", 
        "Tier List Editor", 
        "Trading Monitor", 
        "System Settings"
    ])
    
    with admin_tabs[0]:  # User Management
        st.subheader("👥 User Management")
        
        # Get all users
        users = admin_manager.get_all_users()
        
        if not users.empty:
            st.write(f"Total Users: {len(users)}")
            
            # User table with role management
            for _, user in users.iterrows():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    st.write(f"**{user['username']}** ({user['email']})")
                with col2:
                    st.write(user['role'])
                with col3:
                    new_role = st.selectbox(
                        "Role", 
                        ["Regular", "Tester", "Admin"],
                        index=["Regular", "Tester", "Admin"].index(user['role']),
                        key=f"role_{user['user_id']}"
                    )
                with col4:
                    if st.button("Update", key=f"update_{user['user_id']}"):
                        if admin_manager.update_user_role(user['user_id'], new_role):
                            st.success(f"Updated {user['username']} to {new_role}")
                            time.sleep(1)
                            st.rerun()
                
                st.divider()
        else:
            st.info("No users found")
    
    with admin_tabs[1]:  # Data Analytics
        st.subheader("📊 Data Analytics")
        
        # User statistics
        user_stats = admin_manager.get_user_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Users", user_stats.get('total_users', 0))
        with col2:
            st.metric("Active Today", user_stats.get('active_today', 0))
        with col3:
            st.metric("Total Trades", user_stats.get('total_trades', 0))
        with col4:
            st.metric("Total Volume", f"${user_stats.get('total_volume', 0):,}")
        
        # Trading activity chart
        trading_data = admin_manager.get_trading_activity()
        if not trading_data.empty:
            fig = px.bar(
                trading_data,
                x='date',
                y='trade_count',
                title='Daily Trading Activity'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with admin_tabs[2]:  # Tier List Editor
        st.subheader("✏️ Tier List Editor")
        
        # Get current tier data
        tier_data = tier_manager.get_tier_data()
        
        if not tier_data.empty:
            # Select character to edit
            character_names = tier_data['name'].tolist()
            selected_char = st.selectbox("Select Character to Edit", character_names)
            
            if selected_char:
                char_data = tier_data[tier_data['name'] == selected_char].iloc[0]
                
                with st.form("edit_character"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_value = st.number_input("Value", value=int(char_data['value']))
                        new_demand = st.number_input("Demand", value=int(char_data['demand']), min_value=1, max_value=10)
                    
                    with col2:
                        new_tier = st.selectbox("Tier", ["S+", "S", "A+", "A", "A-"], index=["S+", "S", "A+", "A", "A-"].index(char_data['tier']))
                        new_trend = st.selectbox("Trend", ["Overpriced", "Stable", "Underpriced"], index=["Overpriced", "Stable", "Underpriced"].index(char_data['trend']))
                    
                    new_info = st.text_area("Information", value=char_data['information'])
                    
                    if st.form_submit_button("Update Character"):
                        if tier_manager.update_character(
                            selected_char, new_value, new_demand, 
                            new_tier, new_trend, new_info
                        ):
                            st.success(f"Updated {selected_char} successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Failed to update character")
        
        # Add new character
        st.subheader("➕ Add New Character")
        with st.form("add_character"):
            col1, col2 = st.columns(2)
            
            with col1:
                char_name = st.text_input("Character Name")
                char_value = st.number_input("Value", min_value=1)
                char_demand = st.number_input("Demand", min_value=1, max_value=10)
            
            with col2:
                char_tier = st.selectbox("Tier", ["S+", "S", "A+", "A", "A-"])
                char_trend = st.selectbox("Trend", ["Overpriced", "Stable", "Underpriced"])
            
            char_info = st.text_area("Information")
            
            if st.form_submit_button("Add Character"):
                if char_name and tier_manager.add_character(
                    char_name, char_value, char_demand, 
                    char_tier, char_trend, char_info
                ):
                    st.success(f"Added {char_name} successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Failed to add character or character already exists")
    
    with admin_tabs[3]:  # Trading Monitor
        st.subheader("📈 Trading Monitor")
        
        # Recent trades
        recent_trades = admin_manager.get_recent_trades(limit=50)
        
        if not recent_trades.empty:
            st.write("Recent Trading Activity:")
            st.dataframe(
                recent_trades[['trade_date', 'username', 'character_name', 'action', 'quantity', 'price', 'total_value']],
                use_container_width=True
            )
        else:
            st.info("No recent trades")
        
        # Top traders
        top_traders = admin_manager.get_top_traders()
        if not top_traders.empty:
            st.subheader("🏆 Top Traders")
            for i, trader in top_traders.iterrows():
                st.write(f"{i+1}. **{trader['username']}** - ${trader['total_profit']:,.2f} profit")
    
    with admin_tabs[4]:  # System Settings
        st.subheader("🔧 System Settings")
        
        # Database management
        st.write("**Database Management:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Backup Database"):
                st.info("Database backup initiated...")
        
        with col2:
            if st.button("Clear Trade History"):
                if st.checkbox("Confirm clear trade history"):
                    st.warning("This will permanently delete all trade history!")
        
        with col3:
            if st.button("Reset User Currencies"):
                if st.checkbox("Confirm reset currencies"):
                    st.warning("This will reset all user virtual currencies to 10,000!")
        
        # System statistics
        st.write("**System Statistics:**")
        db_stats = admin_manager.get_database_stats()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Characters", db_stats.get('total_characters', 0))
        with col2:
            st.metric("Database Size", f"{db_stats.get('db_size_mb', 0):.1f} MB")
        with col3:
            st.metric("Uptime", "24/7")

if __name__ == "__main__":
    main()
