import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random

# Import custom modules
from database import DatabaseManager
from auth import AuthManager  
from tier_data import TierListManager
from trading import TradingManager
from achievements import AchievementManager
from admin import AdminManager
from analytics_fixed import AdvancedAnalytics
from social import SocialManager
from notifications_fixed import NotificationManager
from themes import ThemeManager
from guest_trading import GuestTradingManager

# Page configuration
st.set_page_config(
    page_title="Gaming Tier List Platform",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Remove duplicate CSS - will be handled in main()

def initialize_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = 'Regular'
    if 'guest_mode' not in st.session_state:
        st.session_state.guest_mode = False
    if 'visual_effects_enabled' not in st.session_state:
        st.session_state.visual_effects_enabled = True
    if 'current_theme' not in st.session_state:
        st.session_state.current_theme = "Dark"
    if 'theme_transition_active' not in st.session_state:
        st.session_state.theme_transition_active = False
    if 'available_themes' not in st.session_state:
        st.session_state.available_themes = {
            'Dark': {
                'name': 'Dark Galaxy',
                'primary': '#667eea',
                'secondary': '#764ba2',
                'background': 'linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #533483 100%)',
                'accent': '#120119',
                'text': '#ffffff',
                'icon': '🌌'
            },
            'Ocean': {
                'name': 'Ocean Depths',
                'primary': '#00d2ff',
                'secondary': '#3a7bd5',
                'background': 'linear-gradient(135deg, #001f3f 0%, #003f7f 25%, #005f9f 50%, #007fbf 75%, #009fdf 100%)',
                'accent': '#002040',
                'text': '#ffffff',
                'icon': '🌊'
            },
            'Sunset': {
                'name': 'Sunset Glow',
                'primary': '#ff7e5f',
                'secondary': '#feb47b',
                'background': 'linear-gradient(135deg, #2d1b69 0%, #11998e 25%, #38ef7d 50%, #ff7e5f 75%, #feb47b 100%)',
                'accent': '#1a0f3d',
                'text': '#ffffff',
                'icon': '🌅'
            },
            'Forest': {
                'name': 'Mystic Forest',
                'primary': '#56ab2f',
                'secondary': '#a8e6cf',
                'background': 'linear-gradient(135deg, #0f2027 0%, #203a43 25%, #2c5364 50%, #56ab2f 75%, #a8e6cf 100%)',
                'accent': '#0a1a20',
                'text': '#ffffff',
                'icon': '🌲'
            },
            'Cyberpunk': {
                'name': 'Cyberpunk Neon',
                'primary': '#ff0080',
                'secondary': '#00ffff',
                'background': 'linear-gradient(135deg, #000000 0%, #1a0033 25%, #330066 50%, #660099 75%, #9900cc 100%)',
                'accent': '#000015',
                'text': '#ffffff',
                'icon': '🤖'
            },
            'Royal': {
                'name': 'Royal Purple',
                'primary': '#8e2de2',
                'secondary': '#4a00e0',
                'background': 'linear-gradient(135deg, #1e3c72 0%, #2a5298 25%, #8e2de2 50%, #4a00e0 75%, #6a4c93 100%)',
                'accent': '#15254d',
                'text': '#ffffff',
                'icon': '👑'
            }
        }

def apply_dynamic_theme(theme_key):
    """Apply dynamic theme with smooth transitions"""
    if theme_key not in st.session_state.available_themes:
        return
        
    theme = st.session_state.available_themes[theme_key]
    
    st.markdown(f"""
    <style>
    /* Main app background */
    .stApp {{
        background: {theme['background']} !important;
        background-size: 400% 400% !important;
        background-attachment: fixed !important;
        animation: gradientShift 15s ease infinite !important;
        min-height: 100vh !important;
    }}
    
    @keyframes gradientShift {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    
    /* Container styling */
    .main, .block-container {{
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 20px !important;
        margin: 1rem !important;
        padding: 2rem !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3) !important;
    }}
    
    /* Text styling */
    h1, h2, h3, h4, h5, h6, p, div, span, label {{
        color: {theme['text']} !important;
    }}
    
    /* Button styling */
    .stButton > button {{
        background: linear-gradient(135deg, {theme['primary']}80, {theme['secondary']}60) !important;
        backdrop-filter: blur(15px) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 15px !important;
        color: {theme['text']} !important;
        transition: all 0.3s ease !important;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

def render_theme_switcher():
    """Render the adaptive theme switcher"""
    current = st.session_state.available_themes[st.session_state.current_theme]
    
    st.markdown(f"""
    <div style="position: fixed; top: 20px; right: 20px; z-index: 9999;">
        <div style="
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 15px;
            padding: 8px 12px;
            font-size: 14px;
            color: white;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        ">
            {current['icon']} {current['name']}
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    initialize_session_state()
    
    # Enhanced animated gradient background
    st.markdown("""
    <style>
    /* Target every possible Streamlit container with animated gradient */
    .stApp,
    .stApp > div,
    .stApp > div > div,
    div[data-testid="stAppViewContainer"],
    div[data-testid="stAppViewContainer"] > div,
    section[data-testid="stMain"],
    section[data-testid="stMain"] > div,
    .main,
    .main > div,
    body,
    html,
    #root {
        background: linear-gradient(45deg, #1a0033, #2d1b69, #4a148c, #6a1b9a, #8e24aa, #9c27b0, #673ab7, #3f51b5) !important;
        background-size: 800% 800% !important;
        animation: gradientMove 8s ease infinite !important;
        background-attachment: fixed !important;
    }
    
    /* Enhanced gradient animation */
    @keyframes gradientMove {
        0% { background-position: 0% 50%; }
        25% { background-position: 100% 50%; }
        50% { background-position: 100% 100%; }
        75% { background-position: 0% 100%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Force override with highest specificity */
    .stApp.stApp.stApp {
        background: linear-gradient(45deg, #1a0033, #2d1b69, #4a148c, #6a1b9a, #8e24aa, #9c27b0, #673ab7, #3f51b5) !important;
        background-size: 800% 800% !important;
        animation: gradientMove 8s ease infinite !important;
    }
    
    /* Override any theme classes */
    .stApp[class*="theme"],
    .stApp[data-theme] {
        background: linear-gradient(45deg, #1a0033, #2d1b69, #4a148c, #6a1b9a, #8e24aa, #9c27b0, #673ab7, #3f51b5) !important;
        background-size: 800% 800% !important;
        animation: gradientMove 8s ease infinite !important;
    }
    
    /* Enhanced glass containers with subtle animation */
    .main .block-container {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 20px !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4) !important;
        animation: containerGlow 4s ease-in-out infinite alternate !important;
    }
    
    @keyframes containerGlow {
        from { box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 0 0 20px rgba(255, 255, 255, 0.1); }
        to { box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6), 0 0 30px rgba(255, 255, 255, 0.2); }
    }
    
    /* Gradient Background Crawler Elements */
    .gradient-crawler {
        position: fixed;
        pointer-events: none;
        z-index: -1;
        border-radius: 50%;
        filter: blur(40px);
        opacity: 0.6;
    }
    
    .crawler-1 {
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, #ff6b6b, #4ecdc4, #45b7d1);
        animation: crawl-1 20s linear infinite;
    }
    
    .crawler-2 {
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, #96ceb4, #ffeaa7, #dda0dd);
        animation: crawl-2 25s linear infinite;
    }
    
    .crawler-3 {
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, #a29bfe, #fd79a8, #fdcb6e);
        animation: crawl-3 30s linear infinite;
    }
    
    .crawler-4 {
        width: 150px;
        height: 150px;
        background: radial-gradient(circle, #6c5ce7, #a29bfe, #74b9ff);
        animation: crawl-4 18s linear infinite;
    }
    
    .crawler-5 {
        width: 250px;
        height: 250px;
        background: radial-gradient(circle, #fd79a8, #fdcb6e, #e17055);
        animation: crawl-5 22s linear infinite;
    }
    
    @keyframes crawl-1 {
        0% { transform: translate(-100px, 100vh) rotate(0deg); }
        25% { transform: translate(50vw, 50vh) rotate(90deg); }
        50% { transform: translate(100vw, -100px) rotate(180deg); }
        75% { transform: translate(30vw, 100vh) rotate(270deg); }
        100% { transform: translate(-100px, 100vh) rotate(360deg); }
    }
    
    @keyframes crawl-2 {
        0% { transform: translate(100vw, -100px) rotate(0deg); }
        25% { transform: translate(20vw, 80vh) rotate(90deg); }
        50% { transform: translate(-100px, 30vh) rotate(180deg); }
        75% { transform: translate(80vw, -100px) rotate(270deg); }
        100% { transform: translate(100vw, -100px) rotate(360deg); }
    }
    
    @keyframes crawl-3 {
        0% { transform: translate(50vw, 100vh) rotate(0deg); }
        33% { transform: translate(-100px, 60vh) rotate(120deg); }
        66% { transform: translate(100vw, 20vh) rotate(240deg); }
        100% { transform: translate(50vw, 100vh) rotate(360deg); }
    }
    
    @keyframes crawl-4 {
        0% { transform: translate(-100px, 20vh) rotate(0deg); }
        20% { transform: translate(80vw, 10vh) rotate(72deg); }
        40% { transform: translate(90vw, 90vh) rotate(144deg); }
        60% { transform: translate(10vw, 100vh) rotate(216deg); }
        80% { transform: translate(-50px, 60vh) rotate(288deg); }
        100% { transform: translate(-100px, 20vh) rotate(360deg); }
    }
    
    @keyframes crawl-5 {
        0% { transform: translate(100vw, 80vh) rotate(0deg); }
        30% { transform: translate(60vw, -100px) rotate(108deg); }
        60% { transform: translate(-100px, 40vh) rotate(216deg); }
        100% { transform: translate(100vw, 80vh) rotate(360deg); }
    }
    
    /* Interactive Hover Effects for UI Elements */
    
    /* Button Hover Effects */
    .stButton > button {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        overflow: hidden !important;
        transform: translateZ(0) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3), 0 0 20px rgba(139, 69, 19, 0.4) !important;
        background: linear-gradient(45deg, #667eea, #764ba2) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px) scale(0.98) !important;
        transition: all 0.1s !important;
    }
    
    /* Button Ripple Effect */
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
        z-index: 0;
    }
    
    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    /* Input Field Hover Effects */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        transition: all 0.3s ease !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        background: rgba(255, 255, 255, 0.1) !important;
    }
    
    .stTextInput > div > div > input:hover,
    .stTextArea > div > div > textarea:hover {
        border-color: rgba(102, 126, 234, 0.5) !important;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.3) !important;
        transform: scale(1.02) !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 25px rgba(102, 126, 234, 0.5) !important;
        transform: scale(1.02) !important;
        background: rgba(255, 255, 255, 0.15) !important;
    }
    
    /* Selectbox Hover Effects */
    .stSelectbox > div > div {
        transition: all 0.3s ease !important;
    }
    
    .stSelectbox > div > div:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Sidebar Hover Effects */
    .css-1d391kg {
        transition: all 0.3s ease !important;
    }
    
    .css-1d391kg:hover {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(25px) !important;
    }
    
    /* Container Hover Effects */
    .main .block-container:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5), 0 0 40px rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Tab Hover Effects */
    .stTabs [data-baseweb="tab-list"] button {
        transition: all 0.3s ease !important;
        position: relative !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button:hover {
        transform: translateY(-2px) !important;
        background: rgba(102, 126, 234, 0.2) !important;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button:hover::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        animation: tabGlow 0.3s ease;
    }
    
    @keyframes tabGlow {
        from { opacity: 0; transform: scaleX(0); }
        to { opacity: 1; transform: scaleX(1); }
    }
    
    /* Card/Metric Hover Effects */
    .metric-card {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
    }
    
    .metric-card:hover {
        transform: translateY(-5px) rotate(1deg) !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4) !important;
        background: rgba(255, 255, 255, 0.15) !important;
    }
    
    /* Text Hover Effects */
    h1, h2, h3 {
        transition: all 0.3s ease !important;
        cursor: default !important;
    }
    
    h1:hover, h2:hover, h3:hover {
        text-shadow: 0 0 20px rgba(102, 126, 234, 0.6) !important;
        transform: scale(1.02) !important;
    }
    
    /* Interactive Floating Elements */
    .floating-element {
        animation: float 3s ease-in-out infinite !important;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    /* Hover Pulse Animation */
    .pulse-hover:hover {
        animation: pulse 1s infinite !important;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    /* Interactive Background Elements */
    .interactive-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -2;
        overflow: hidden;
    }
    
    .mouse-follower {
        position: absolute;
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, rgba(102, 126, 234, 0.3), transparent);
        border-radius: 50%;
        filter: blur(30px);
        pointer-events: none;
        transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        z-index: -1;
    }
    
    .particle {
        position: absolute;
        width: 4px;
        height: 4px;
        background: rgba(255, 255, 255, 0.8);
        border-radius: 50%;
        pointer-events: none;
        animation: particleFloat 15s linear infinite;
    }
    
    @keyframes particleFloat {
        0% {
            transform: translateY(100vh) translateX(0) rotate(0deg);
            opacity: 0;
        }
        10% {
            opacity: 1;
        }
        90% {
            opacity: 1;
        }
        100% {
            transform: translateY(-100px) translateX(200px) rotate(360deg);
            opacity: 0;
        }
    }
    
    .wave-effect {
        position: absolute;
        border-radius: 50%;
        background: rgba(102, 126, 234, 0.1);
        pointer-events: none;
        animation: waveExpand 2s ease-out;
    }
    
    @keyframes waveExpand {
        0% {
            width: 0;
            height: 0;
            opacity: 0.8;
        }
        50% {
            opacity: 0.4;
        }
        100% {
            width: 300px;
            height: 300px;
            opacity: 0;
        }
    }
    
    .glow-orb {
        position: absolute;
        width: 100px;
        height: 100px;
        background: radial-gradient(circle, rgba(138, 43, 226, 0.4), rgba(75, 0, 130, 0.2), transparent);
        border-radius: 50%;
        filter: blur(20px);
        animation: orbFloat 20s ease-in-out infinite;
    }
    
    @keyframes orbFloat {
        0%, 100% { transform: translate(0, 0) scale(1); }
        25% { transform: translate(50px, -30px) scale(1.2); }
        50% { transform: translate(-30px, 40px) scale(0.8); }
        75% { transform: translate(40px, 20px) scale(1.1); }
    }
    </style>
    
    <script>
    // Force animated gradient background with JavaScript
    function forceAnimatedBackground() {
        const gradient = 'linear-gradient(45deg, #1a0033, #2d1b69, #4a148c, #6a1b9a, #8e24aa, #9c27b0, #673ab7, #3f51b5)';
        
        // Target all possible elements
        const selectors = [
            '.stApp',
            'div[data-testid="stAppViewContainer"]',
            'section[data-testid="stMain"]',
            '.main',
            'body',
            'html'
        ];
        
        selectors.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                if (el) {
                    el.style.setProperty('background', gradient, 'important');
                    el.style.setProperty('background-size', '800% 800%', 'important');
                    el.style.setProperty('animation', 'gradientMove 8s ease infinite', 'important');
                    el.style.setProperty('background-attachment', 'fixed', 'important');
                }
            });
        });
    }
    
    // Apply immediately and repeatedly
    forceAnimatedBackground();
    setTimeout(forceAnimatedBackground, 100);
    setTimeout(forceAnimatedBackground, 500);
    setTimeout(forceAnimatedBackground, 1000);
    
    // Apply when DOM changes
    const observer = new MutationObserver(forceAnimatedBackground);
    observer.observe(document.body, { childList: true, subtree: true });
    
    // Create gradient crawler elements
    function createGradientCrawlers() {
        // Remove existing crawlers to avoid duplicates
        document.querySelectorAll('.gradient-crawler').forEach(el => el.remove());
        
        // Create 5 crawler elements
        for (let i = 1; i <= 5; i++) {
            const crawler = document.createElement('div');
            crawler.className = `gradient-crawler crawler-${i}`;
            document.body.appendChild(crawler);
        }
    }
    
    // Initialize crawlers
    createGradientCrawlers();
    setTimeout(createGradientCrawlers, 1000);
    
    // Enhanced Interactive Hover Effects
    function initializeHoverEffects() {
        // Add floating animation to titles
        const titles = document.querySelectorAll('h1, h2, h3');
        titles.forEach(title => {
            title.classList.add('floating-element');
        });
        
        // Add pulse effect to buttons on long hover
        const buttons = document.querySelectorAll('.stButton > button');
        buttons.forEach(button => {
            let hoverTimeout;
            
            button.addEventListener('mouseenter', () => {
                hoverTimeout = setTimeout(() => {
                    button.classList.add('pulse-hover');
                }, 1000);
            });
            
            button.addEventListener('mouseleave', () => {
                clearTimeout(hoverTimeout);
                button.classList.remove('pulse-hover');
            });
        });
        
        // Add sparkle effect on click
        document.addEventListener('click', (e) => {
            createSparkleEffect(e.clientX, e.clientY);
        });
        
        // Add metric card hover effects
        const metrics = document.querySelectorAll('[data-testid="metric-container"]');
        metrics.forEach(metric => {
            metric.classList.add('metric-card');
        });
    }
    
    // Create sparkle effect on click
    function createSparkleEffect(x, y) {
        const sparkle = document.createElement('div');
        sparkle.style.position = 'fixed';
        sparkle.style.left = x + 'px';
        sparkle.style.top = y + 'px';
        sparkle.style.width = '10px';
        sparkle.style.height = '10px';
        sparkle.style.background = 'radial-gradient(circle, #667eea, #764ba2)';
        sparkle.style.borderRadius = '50%';
        sparkle.style.pointerEvents = 'none';
        sparkle.style.zIndex = '1000';
        sparkle.style.animation = 'sparkle 0.6s ease-out forwards';
        
        document.body.appendChild(sparkle);
        
        setTimeout(() => {
            sparkle.remove();
        }, 600);
    }
    
    // Add sparkle animation
    const sparkleStyle = document.createElement('style');
    sparkleStyle.textContent = `
        @keyframes sparkle {
            0% { 
                transform: scale(0) rotate(0deg); 
                opacity: 1; 
            }
            50% { 
                transform: scale(1.5) rotate(180deg); 
                opacity: 0.8; 
            }
            100% { 
                transform: scale(0) rotate(360deg); 
                opacity: 0; 
            }
        }
    `;
    document.head.appendChild(sparkleStyle);
    
    // Initialize hover effects
    initializeHoverEffects();
    setTimeout(initializeHoverEffects, 2000);
    
    // Interactive Background System
    function createInteractiveBackground() {
        // Remove existing interactive background to avoid duplicates
        const existing = document.querySelector('.interactive-bg');
        if (existing) existing.remove();
        
        // Create interactive background container
        const interactiveBg = document.createElement('div');
        interactiveBg.className = 'interactive-bg';
        interactiveBg.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            pointer-events: none;
            z-index: 9999;
            overflow: hidden;
            background: rgba(255, 0, 0, 0.1);
        `;
        document.body.appendChild(interactiveBg);
        
        // Create mouse follower with inline styles
        const mouseFollower = document.createElement('div');
        mouseFollower.className = 'mouse-follower';
        mouseFollower.style.cssText = `
            position: absolute;
            width: 200px;
            height: 200px;
            background: radial-gradient(circle, rgba(102, 126, 234, 0.8), transparent);
            border-radius: 50%;
            filter: blur(30px);
            pointer-events: none;
            transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            z-index: 1000;
        `;
        interactiveBg.appendChild(mouseFollower);
        
        // Create floating orbs with inline styles
        for (let i = 0; i < 5; i++) {
            const orb = document.createElement('div');
            orb.className = 'glow-orb';
            orb.style.cssText = `
                position: absolute;
                width: 100px;
                height: 100px;
                background: radial-gradient(circle, rgba(138, 43, 226, 0.4), rgba(75, 0, 130, 0.2), transparent);
                border-radius: 50%;
                filter: blur(20px);
                animation: orbFloat 20s ease-in-out infinite;
                left: ${Math.random() * 80 + 10}%;
                top: ${Math.random() * 80 + 10}%;
                animation-delay: ${Math.random() * 20}s;
            `;
            interactiveBg.appendChild(orb);
        }
        
        // Mouse movement tracking
        let mouseX = 0, mouseY = 0;
        
        document.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
            
            // Update mouse follower position
            mouseFollower.style.left = (mouseX - 100) + 'px';
            mouseFollower.style.top = (mouseY - 100) + 'px';
            
            // Create particle trail occasionally
            if (Math.random() < 0.1) {
                createParticle(mouseX, mouseY);
            }
        });
        
        // Click wave effect
        document.addEventListener('click', (e) => {
            createWaveEffect(e.clientX, e.clientY);
        });
        
        // Continuous particle system
        setInterval(createRandomParticle, 2000);
    }
    
    // Create particle at specific position
    function createParticle(x, y) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = x + 'px';
        particle.style.top = y + 'px';
        particle.style.animationDelay = Math.random() * 2 + 's';
        
        const interactiveBg = document.querySelector('.interactive-bg');
        if (interactiveBg) {
            interactiveBg.appendChild(particle);
            
            setTimeout(() => {
                particle.remove();
            }, 15000);
        }
    }
    
    // Create random particles
    function createRandomParticle() {
        const x = Math.random() * window.innerWidth;
        const y = window.innerHeight + 50;
        createParticle(x, y);
    }
    
    // Create wave effect on click
    function createWaveEffect(x, y) {
        const wave = document.createElement('div');
        wave.className = 'wave-effect';
        wave.style.left = (x - 150) + 'px';
        wave.style.top = (y - 150) + 'px';
        
        const interactiveBg = document.querySelector('.interactive-bg');
        if (interactiveBg) {
            interactiveBg.appendChild(wave);
            
            setTimeout(() => {
                wave.remove();
            }, 2000);
        }
    }
    
    // Initialize interactive background with delay and retry
    setTimeout(() => {
        createInteractiveBackground();
        console.log('Interactive background initialized');
    }, 500);
    
    // Retry initialization after 2 seconds to ensure DOM is ready
    setTimeout(() => {
        if (!document.querySelector('.interactive-bg')) {
            createInteractiveBackground();
            console.log('Interactive background retry initialized');
        }
    }, 2000);
    </script>
    
    <!-- Animated Particle Background -->
    <div class="particle-container" style="
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        pointer-events: none;
        z-index: 1000;
        overflow: hidden;
        background: rgba(0, 255, 0, 0.1);
    ">
        <div class="floating-orb orb-1"></div>
        <div class="floating-orb orb-2"></div>
        <div class="floating-orb orb-3"></div>
        <div class="floating-orb orb-4"></div>
        <div class="floating-orb orb-5"></div>
    </div>
    
    <!-- Gradient Crawler HTML Elements -->
    <div class="gradient-crawler crawler-1"></div>
    <div class="gradient-crawler crawler-2"></div>
    <div class="gradient-crawler crawler-3"></div>
    <div class="gradient-crawler crawler-4"></div>
    <div class="gradient-crawler crawler-5"></div>
    
    <script>
    // Simple particle animation system
    function animateParticles() {
        const particles = document.querySelectorAll('.floating-orb');
        particles.forEach((particle, index) => {
            const delay = index * 0.5;
            particle.style.animationDelay = delay + 's';
        });
    }
    
    // Initialize particle animations
    setTimeout(animateParticles, 100);
    </script>
    """, unsafe_allow_html=True)
    
    # Apply theme and render switcher
    apply_dynamic_theme(st.session_state.current_theme)
    render_theme_switcher()
    
    # Initialize managers
    db_manager = DatabaseManager()
    auth_manager = AuthManager(db_manager)
    tier_manager = TierListManager(db_manager)
    trading_manager = TradingManager(db_manager)
    achievement_manager = AchievementManager(db_manager)
    admin_manager = AdminManager(db_manager)
    analytics_manager = AdvancedAnalytics(db_manager)
    social_manager = SocialManager(db_manager)
    notification_manager = NotificationManager(db_manager)
    theme_manager = ThemeManager(db_manager)
    guest_trading_manager = GuestTradingManager()

    # Authentication and guest mode check
    if not st.session_state.authenticated and not st.session_state.guest_mode:
        show_auth_page(auth_manager)
    else:
        # Sidebar navigation
        st.sidebar.title("🎮 Navigation")
        
        # Theme selection in sidebar
        with st.sidebar.expander("🎨 Theme Settings"):
            theme_cols = st.columns(2)
            for i, (key, theme) in enumerate(st.session_state.available_themes.items()):
                col = theme_cols[i % 2]
                if col.button(f"{theme['icon']} {theme['name']}", key=f"theme_{key}"):
                    st.session_state.current_theme = key
                    st.rerun()
        
        # Main navigation
        if st.session_state.guest_mode:
            page = st.sidebar.selectbox("Choose Page", [
                "Tier Lists", "Trading Simulator", "Guest Profile"
            ])
        else:
            pages = ["Tier Lists", "Trading Simulator", "Win/Loss Tracking", "Profile", "Settings"]
            if st.session_state.user_role == 'Admin':
                pages.append("Admin Panel")
            page = st.sidebar.selectbox("Choose Page", pages)
        
        # Logout/Exit Guest Mode
        if st.sidebar.button("🚪 " + ("Exit Guest Mode" if st.session_state.guest_mode else "Logout")):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        # Page routing
        if page == "Tier Lists":
            show_tier_lists(tier_manager)
        elif page == "Trading Simulator":
            if st.session_state.guest_mode:
                show_guest_trading(guest_trading_manager, tier_manager)
            else:
                show_trading_simulator(trading_manager, tier_manager, achievement_manager, notification_manager)
        elif page == "Win/Loss Tracking":
            show_wl_tracking(trading_manager)
        elif page == "Profile":
            show_profile(auth_manager, achievement_manager, trading_manager)
        elif page == "Guest Profile":
            show_guest_profile(guest_trading_manager)
        elif page == "Settings":
            show_settings(theme_manager, auth_manager)
        elif page == "Admin Panel":
            show_admin_panel(admin_manager)

def show_auth_page(auth_manager):
    """Display authentication page"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1 style="font-size: 3rem; margin-bottom: 1rem;">🎮 Gaming Tier List Platform</h1>
        <p style="font-size: 1.2rem; margin-bottom: 2rem;">Trade characters, unlock achievements, and dominate the leaderboards</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Start section
    st.markdown("### Quick Start")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎮 CONTINUE AS GUEST", type="primary", use_container_width=True):
            st.session_state.guest_mode = True
            st.session_state.username = "Guest"
            st.rerun()
    
    with col2:
        st.markdown("""
        **Guest Mode Features:**
        ✅ Browse tier lists
        ✅ Trade characters  
        ✅ View statistics
        ⚠️ Progress not saved
        """)
    
    # Authentication tabs
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_submitted = st.form_submit_button("Login", type="primary", use_container_width=True)
            
            if login_submitted:
                result = auth_manager.login(username, password)
                if result:
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    with tab2:
        with st.form("signup_form"):
            new_username = st.text_input("Choose Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Choose Password", type="password")
            signup_submitted = st.form_submit_button("Sign Up", type="primary", use_container_width=True)
            
            if signup_submitted:
                result = auth_manager.register(new_username, new_email, new_password)
                if result:
                    st.success("Account created successfully! Please login.")
                else:
                    st.error("Username or email already exists")

def show_tier_lists(tier_manager):
    """Display tier lists"""
    st.title("🏆 Character Tier Lists")
    
    # Search and filter
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("🔍 Search characters", placeholder="Enter character name...")
    with col2:
        tier_filter = st.selectbox("Filter by tier", ["All", "S", "A", "B", "C", "D"])
    
    # Get tier data
    tier_data = tier_manager.get_tier_data()
    df = pd.DataFrame(tier_data)
    
    if not df.empty:
        # Apply filters
        if search_query:
            df = df[df['name'].str.contains(search_query, case=False, na=False)]
        if tier_filter != "All":
            df = df[df['tier'] == tier_filter]
        
        # Display tier statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Characters", len(df))
        with col2:
            avg_value = df['value'].mean() if not df.empty else 0
            st.metric("Average Value", f"${avg_value:.2f}")
        with col3:
            trending_count = len(df[df['trend'] == 'Rising']) if not df.empty else 0
            st.metric("Trending Up", trending_count)
        with col4:
            high_demand = len(df[df['demand'] == 'High']) if not df.empty else 0
            st.metric("High Demand", high_demand)
        
        # Display characters by tier
        if not df.empty:
            for tier in ['S', 'A', 'B', 'C', 'D']:
                tier_chars = df[df['tier'] == tier]
                if not tier_chars.empty:
                    st.subheader(f"Tier {tier}")
                    
                    cols = st.columns(min(len(tier_chars), 4))
                    for idx, (_, char) in enumerate(tier_chars.iterrows()):
                        col = cols[idx % 4]
                        
                        trend_emoji = "📈" if char['trend'] == 'Rising' else "📉" if char['trend'] == 'Falling' else "➡️"
                        demand_color = "🔴" if char['demand'] == 'High' else "🟡" if char['demand'] == 'Medium' else "🟢"
                        
                        col.markdown(f"""
                        <div style="
                            background: rgba(255, 255, 255, 0.1);
                            border-radius: 15px;
                            padding: 1rem;
                            margin: 0.5rem 0;
                            border: 2px solid rgba(255, 255, 255, 0.2);
                        ">
                            <h4>{char['name']}</h4>
                            <p><strong>${char['value']:.2f}</strong></p>
                            <p>{trend_emoji} {char['trend']}</p>
                            <p>{demand_color} {char['demand']} Demand</p>
                            <p><small>{char['information']}</small></p>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("No characters found matching your search criteria.")
    else:
        st.warning("No tier data available.")

def show_trading_simulator(trading_manager, tier_manager, achievement_manager, notification_manager):
    """Display trading simulator"""
    st.title("💰 Trading Simulator")
    
    # Get user's current currency and portfolio
    portfolio = trading_manager.get_user_portfolio(st.session_state.user_id)
    stats = trading_manager.get_trading_statistics(st.session_state.user_id)
    
    # Display current stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Virtual Currency", f"${stats['virtual_currency']:.2f}")
    with col2:
        st.metric("Portfolio Value", f"${stats['portfolio_value']:.2f}")
    with col3:
        st.metric("Total Profit/Loss", f"${stats['total_profit']:.2f}", 
                 delta=f"{stats['total_profit']:.2f}")
    with col4:
        st.metric("Trade Count", stats['trade_count'])
    
    # Trading interface
    st.subheader("🔄 Trade Characters")
    
    tab1, tab2 = st.tabs(["Buy Characters", "Sell Characters"])
    
    with tab1:
        # Buy interface
        tier_data = tier_manager.get_tier_data()
        if tier_data:
            df = pd.DataFrame(tier_data)
            
            col1, col2 = st.columns([2, 1])
            with col1:
                selected_char = st.selectbox("Select character to buy", df['name'].tolist())
            with col2:
                quantity = st.number_input("Quantity", min_value=1, max_value=100, value=1)
            
            if selected_char:
                char_data = df[df['name'] == selected_char].iloc[0]
                total_cost = char_data['value'] * quantity
                
                st.info(f"Total cost: ${total_cost:.2f}")
                
                if st.button("💳 Buy", type="primary"):
                    result = trading_manager.buy_character(
                        st.session_state.user_id, 
                        selected_char, 
                        quantity, 
                        char_data['value']
                    )
                    
                    if result['success']:
                        st.success(f"Successfully bought {quantity}x {selected_char}!")
                        
                        # Check for achievements
                        new_achievements = achievement_manager.check_and_award_achievements(st.session_state.user_id)
                        for achievement in new_achievements:
                            st.success(f"🏆 Achievement unlocked: {achievement}")
                            notification_manager.create_achievement_notification(
                                st.session_state.user_id, achievement, "New achievement unlocked!"
                            )
                        
                        st.rerun()
                    else:
                        st.error(result['message'])
    
    with tab2:
        # Sell interface
        if portfolio:
            portfolio_df = pd.DataFrame(portfolio)
            
            col1, col2 = st.columns([2, 1])
            with col1:
                owned_chars = portfolio_df['character_name'].tolist()
                selected_sell_char = st.selectbox("Select character to sell", owned_chars)
            with col2:
                if selected_sell_char:
                    max_qty = portfolio_df[portfolio_df['character_name'] == selected_sell_char]['quantity'].iloc[0]
                    sell_quantity = st.number_input("Quantity to sell", min_value=1, max_value=max_qty, value=1)
            
            if selected_sell_char:
                char_data = tier_manager.get_character_data(selected_sell_char)
                if char_data:
                    total_value = char_data['value'] * sell_quantity
                    st.info(f"Total value: ${total_value:.2f}")
                    
                    if st.button("💸 Sell", type="primary"):
                        result = trading_manager.sell_character(
                            st.session_state.user_id, 
                            selected_sell_char, 
                            sell_quantity, 
                            char_data['value']
                        )
                        
                        if result['success']:
                            st.success(f"Successfully sold {sell_quantity}x {selected_sell_char}!")
                            st.rerun()
                        else:
                            st.error(result['message'])
        else:
            st.info("You don't own any characters yet. Buy some characters first!")
    
    # Portfolio display
    if portfolio:
        st.subheader("📊 Your Portfolio")
        portfolio_df = pd.DataFrame(portfolio)
        
        # Calculate current values
        current_values = []
        for _, row in portfolio_df.iterrows():
            char_data = tier_manager.get_character_data(row['character_name'])
            current_value = char_data['value'] if char_data else row['purchase_price']
            current_values.append(current_value)
        
        portfolio_df['current_value'] = current_values
        portfolio_df['total_current_value'] = portfolio_df['current_value'] * portfolio_df['quantity']
        portfolio_df['profit_loss'] = portfolio_df['total_current_value'] - (portfolio_df['purchase_price'] * portfolio_df['quantity'])
        
        st.dataframe(portfolio_df[['character_name', 'quantity', 'purchase_price', 'current_value', 'total_current_value', 'profit_loss']], use_container_width=True)

def show_guest_trading(guest_trading_manager, tier_manager):
    """Display guest trading simulator"""
    st.title("💰 Trading Simulator (Guest Mode)")
    
    # Get guest stats
    stats = guest_trading_manager.get_guest_trading_statistics()
    portfolio = guest_trading_manager.get_guest_portfolio()
    
    # Display current stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Virtual Currency", f"${stats['virtual_currency']:.2f}")
    with col2:
        st.metric("Portfolio Value", f"${stats['portfolio_value']:.2f}")
    with col3:
        st.metric("Total Profit/Loss", f"${stats['total_profit']:.2f}")
    with col4:
        st.metric("Trade Count", stats['trade_count'])
    
    # Trading interface
    st.subheader("🔄 Trade Characters")
    
    tab1, tab2 = st.tabs(["Buy Characters", "Sell Characters"])
    
    with tab1:
        # Buy interface
        tier_data = tier_manager.get_tier_data()
        if tier_data:
            df = pd.DataFrame(tier_data)
            
            col1, col2 = st.columns([2, 1])
            with col1:
                selected_char = st.selectbox("Select character to buy", df['name'].tolist())
            with col2:
                quantity = st.number_input("Quantity", min_value=1, max_value=100, value=1)
            
            if selected_char:
                char_data = df[df['name'] == selected_char].iloc[0]
                total_cost = char_data['value'] * quantity
                
                st.info(f"Total cost: ${total_cost:.2f}")
                
                if st.button("💳 Buy", type="primary"):
                    result = guest_trading_manager.guest_buy_character(
                        selected_char, 
                        quantity, 
                        char_data['value']
                    )
                    
                    if result['success']:
                        st.success(f"Successfully bought {quantity}x {selected_char}!")
                        st.rerun()
                    else:
                        st.error(result['message'])
    
    with tab2:
        # Sell interface for guest
        if portfolio:
            col1, col2 = st.columns([2, 1])
            with col1:
                owned_chars = list(portfolio.keys())
                selected_sell_char = st.selectbox("Select character to sell", owned_chars)
            with col2:
                if selected_sell_char:
                    max_qty = portfolio[selected_sell_char]['quantity']
                    sell_quantity = st.number_input("Quantity to sell", min_value=1, max_value=max_qty, value=1)
            
            if selected_sell_char:
                char_data = tier_manager.get_character_data(selected_sell_char)
                if char_data:
                    total_value = char_data['value'] * sell_quantity
                    st.info(f"Total value: ${total_value:.2f}")
                    
                    if st.button("💸 Sell", type="primary"):
                        result = guest_trading_manager.guest_sell_character(
                            selected_sell_char, 
                            sell_quantity, 
                            char_data['value']
                        )
                        
                        if result['success']:
                            st.success(f"Successfully sold {sell_quantity}x {selected_sell_char}!")
                            st.rerun()
                        else:
                            st.error(result['message'])
        else:
            st.info("You don't own any characters yet. Buy some characters first!")
    
    # Portfolio display for guest
    if portfolio:
        st.subheader("📊 Your Portfolio")
        portfolio_data = []
        
        for char_name, data in portfolio.items():
            char_data = tier_manager.get_character_data(char_name)
            current_value = char_data['value'] if char_data else data['purchase_price']
            
            portfolio_data.append({
                'Character': char_name,
                'Quantity': data['quantity'],
                'Purchase Price': f"${data['purchase_price']:.2f}",
                'Current Value': f"${current_value:.2f}",
                'Total Value': f"${current_value * data['quantity']:.2f}",
                'Profit/Loss': f"${(current_value - data['purchase_price']) * data['quantity']:.2f}"
            })
        
        if portfolio_data:
            st.dataframe(pd.DataFrame(portfolio_data), use_container_width=True)

def show_guest_profile(guest_trading_manager):
    """Display guest profile"""
    st.title("👤 Guest Profile")
    
    stats = guest_trading_manager.get_guest_trading_statistics()
    
    st.info("⚠️ You are in Guest Mode. Your progress will not be saved.")
    
    # Display stats
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Virtual Currency", f"${stats['virtual_currency']:.2f}")
        st.metric("Trade Count", stats['trade_count'])
    
    with col2:
        st.metric("Portfolio Value", f"${stats['portfolio_value']:.2f}")
        st.metric("Total Profit/Loss", f"${stats['total_profit']:.2f}")
    
    # Recent trades
    trades = guest_trading_manager.get_guest_trades(10)
    if trades:
        st.subheader("📈 Recent Trades")
        trades_df = pd.DataFrame(trades)
        st.dataframe(trades_df, use_container_width=True)
    
    # Reset option
    if st.button("🔄 Reset Guest Session", type="secondary"):
        guest_trading_manager.reset_guest_session()
        st.success("Guest session reset!")
        st.rerun()

def show_wl_tracking(trading_manager):
    """Display Win/Loss tracking"""
    st.title("📊 Win/Loss Tracking")
    
    stats = trading_manager.get_trading_statistics(st.session_state.user_id)
    trades = trading_manager.get_user_trades(st.session_state.user_id, 50)
    
    # Overall stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Trades", stats['trade_count'])
    with col2:
        win_rate = (stats['profitable_trades'] / max(stats['trade_count'], 1)) * 100
        st.metric("Win Rate", f"{win_rate:.1f}%")
    with col3:
        st.metric("Profitable Trades", stats['profitable_trades'])
    with col4:
        st.metric("Total Profit", f"${stats['total_profit']:.2f}")
    
    # Recent trades
    if trades:
        st.subheader("📈 Recent Trades")
        trades_df = pd.DataFrame(trades)
        
        # Add profit/loss calculation
        trades_df['profit_loss'] = trades_df.apply(
            lambda row: (row['sell_price'] - row['buy_price']) * row['quantity'] 
            if row['trade_type'] == 'sell' else 0, axis=1
        )
        
        # Color code profitable trades
        def highlight_profit(val):
            if val > 0:
                return 'color: green'
            elif val < 0:
                return 'color: red'
            return ''
        
        styled_df = trades_df.style.applymap(highlight_profit, subset=['profit_loss'])
        st.dataframe(styled_df, use_container_width=True)
        
        # Profit/Loss chart
        if len(trades_df) > 1:
            st.subheader("📊 Profit/Loss Over Time")
            
            # Calculate cumulative profit
            trades_df['cumulative_profit'] = trades_df['profit_loss'].cumsum()
            
            fig = px.line(trades_df, x='timestamp', y='cumulative_profit', 
                         title='Cumulative Profit/Loss Over Time')
            fig.update_traces(line_color='#00ff88')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)

def show_profile(auth_manager, achievement_manager, trading_manager):
    """Display user profile"""
    st.title("👤 User Profile")
    
    # Get user data
    profile = auth_manager.get_user_profile(st.session_state.user_id)
    achievements = achievement_manager.get_user_achievements(st.session_state.user_id)
    stats = trading_manager.get_trading_statistics(st.session_state.user_id)
    
    if profile:
        # Profile info
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Profile Information")
            st.write(f"**Username:** {profile['username']}")
            st.write(f"**Role:** {profile['role']}")
            st.write(f"**Member Since:** {profile['created_at'].strftime('%B %Y')}")
        
        with col2:
            st.subheader("Trading Statistics")
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                st.metric("Virtual Currency", f"${stats['virtual_currency']:.2f}")
                st.metric("Total Trades", stats['trade_count'])
            with col2_2:
                st.metric("Portfolio Value", f"${stats['portfolio_value']:.2f}")
                st.metric("Total Profit", f"${stats['total_profit']:.2f}")
        
        # Achievements
        st.subheader("🏆 Achievements")
        if achievements:
            # Group achievements by status
            unlocked = [a for a in achievements if a['unlocked']]
            locked = [a for a in achievements if not a['unlocked']]
            
            st.write(f"**Unlocked: {len(unlocked)}/{len(achievements)}**")
            
            # Display unlocked achievements
            if unlocked:
                achievement_cols = st.columns(min(len(unlocked), 3))
                for idx, achievement in enumerate(unlocked):
                    col = achievement_cols[idx % 3]
                    col.markdown(f"""
                    <div style="
                        background: linear-gradient(135deg, #ffd700, #ffed4e);
                        color: black;
                        border-radius: 10px;
                        padding: 1rem;
                        margin: 0.5rem 0;
                        text-align: center;
                    ">
                        <h4>🏆 {achievement['name']}</h4>
                        <p><small>{achievement['description']}</small></p>
                        <p><strong>{achievement['progress']}/{achievement['target']}</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Display locked achievements
            if locked:
                with st.expander(f"🔒 Locked Achievements ({len(locked)})"):
                    for achievement in locked:
                        st.markdown(f"""
                        <div style="
                            background: rgba(255, 255, 255, 0.1);
                            border-radius: 10px;
                            padding: 1rem;
                            margin: 0.5rem 0;
                        ">
                            <h4>🔒 {achievement['name']}</h4>
                            <p>{achievement['description']}</p>
                            <p>Progress: {achievement['progress']}/{achievement['target']}</p>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("No achievements available yet. Start trading to unlock achievements!")

def show_settings(theme_manager, auth_manager):
    """Display settings page"""
    st.title("⚙️ Settings")
    
    # Theme settings
    st.subheader("🎨 Theme & Style")
    
    # Theme selection with preview
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.write("**Select Theme:**")
        for key, theme in st.session_state.available_themes.items():
            if st.button(f"{theme['icon']} {theme['name']}", key=f"settings_theme_{key}"):
                st.session_state.current_theme = key
                st.rerun()
    
    with col2:
        current_theme = st.session_state.available_themes[st.session_state.current_theme]
        st.markdown(f"""
        <div style="
            background: {current_theme['background']};
            border-radius: 15px;
            padding: 2rem;
            text-align: center;
            border: 2px solid rgba(255, 255, 255, 0.2);
        ">
            <h3>{current_theme['icon']} {current_theme['name']}</h3>
            <p>Current Theme Preview</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Visual effects toggle
    st.subheader("✨ Visual Effects")
    visual_effects = st.toggle("Enable Visual Effects", value=st.session_state.visual_effects_enabled)
    if visual_effects != st.session_state.visual_effects_enabled:
        st.session_state.visual_effects_enabled = visual_effects
        st.rerun()
    
    # Account settings
    if not st.session_state.guest_mode:
        st.subheader("👤 Account Settings")
        
        with st.form("profile_form"):
            st.write("**Update Profile:**")
            new_display_name = st.text_input("Display Name", value=st.session_state.username)
            new_bio = st.text_area("Bio", placeholder="Tell us about yourself...")
            
            if st.form_submit_button("Update Profile"):
                result = auth_manager.update_profile(st.session_state.user_id, new_display_name, new_bio)
                if result['success']:
                    st.success("Profile updated successfully!")
                else:
                    st.error(result['message'])

def show_admin_panel(admin_manager):
    """Display admin panel"""
    st.title("🛡️ Admin Panel")
    
    # Admin authentication with secret code
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        st.warning("Admin access requires authentication.")
        admin_code = st.text_input("Enter admin secret code:", type="password")
        
        if st.button("Authenticate"):
            if admin_code == "0202024":  # Secret admin code
                st.session_state.admin_authenticated = True
                st.success("Admin authenticated successfully!")
                st.rerun()
            else:
                st.error("Invalid admin code!")
        return
    
    # Admin dashboard
    st.success("Welcome to the Admin Panel!")
    
    # Admin statistics
    user_stats = admin_manager.get_user_statistics()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", user_stats['total_users'])
    with col2:
        st.metric("Active Users", user_stats['active_users'])
    with col3:
        st.metric("Total Trades", user_stats['total_trades'])
    with col4:
        st.metric("Total Currency", f"${user_stats['total_virtual_currency']:.2f}")
    
    # Admin tabs
    tab1, tab2, tab3 = st.tabs(["User Management", "System Stats", "Database"])
    
    with tab1:
        st.subheader("👥 User Management")
        
        # Get all users
        users = admin_manager.get_all_users()
        if users:
            users_df = pd.DataFrame(users)
            st.dataframe(users_df, use_container_width=True)
            
            # User actions
            st.subheader("User Actions")
            col1, col2 = st.columns(2)
            
            with col1:
                selected_user = st.selectbox("Select User", users_df['username'].tolist())
                new_role = st.selectbox("New Role", ["Regular", "Admin", "Banned"])
                
                if st.button("Update Role"):
                    user_id = users_df[users_df['username'] == selected_user]['id'].iloc[0]
                    result = admin_manager.update_user_role(user_id, new_role)
                    if result['success']:
                        st.success(f"Updated {selected_user}'s role to {new_role}")
                        st.rerun()
            
            with col2:
                currency_user = st.selectbox("Select User for Currency Reset", users_df['username'].tolist())
                currency_amount = st.number_input("New Currency Amount", value=10000, min_value=0)
                
                if st.button("Reset Currency"):
                    user_id = users_df[users_df['username'] == currency_user]['id'].iloc[0]
                    admin_manager.reset_user_currency(user_id, currency_amount)
                    st.success(f"Reset {currency_user}'s currency to ${currency_amount}")
    
    with tab2:
        st.subheader("📊 System Statistics")
        
        # Trading activity
        activity = admin_manager.get_trading_activity()
        if activity:
            activity_df = pd.DataFrame(activity)
            
            fig = px.line(activity_df, x='date', y='trade_count', 
                         title='Trading Activity Over Time')
            fig.update_traces(line_color='#00ff88')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Top traders
        top_traders = admin_manager.get_top_traders()
        if top_traders:
            st.subheader("🏆 Top Traders")
            traders_df = pd.DataFrame(top_traders)
            st.dataframe(traders_df, use_container_width=True)
    
    with tab3:
        st.subheader("🗄️ Database Management")
        
        # Database stats
        db_stats = admin_manager.get_database_stats()
        if db_stats:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Tables", db_stats['table_count'])
            with col2:
                st.metric("Database Size", f"{db_stats['database_size_mb']:.2f} MB")
            with col3:
                st.metric("Connection Count", db_stats['connection_count'])
        
        # Dangerous actions
        st.warning("⚠️ Dangerous Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Optimize Database", type="secondary"):
                admin_manager.optimize_database()
                st.success("Database optimized!")
        
        with col2:
            if st.button("📊 Update Market Data", type="secondary"):
                # Simulate market fluctuations
                st.success("Market data updated!")

if __name__ == "__main__":
    main()