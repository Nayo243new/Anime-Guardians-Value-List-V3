import streamlit as st
import pandas as pd
from database import DatabaseManager
from auth import AuthManager
from tier_data import TierListManager
from trading import TradingManager
from guest_trading import GuestTradingManager
from achievements import AchievementManager
from notifications_fixed import NotificationManager
from admin import AdminManager
from themes import ThemeManager
from social import SocialManager
from analytics_fixed import AdvancedAnalytics

# Configure page
st.set_page_config(
    page_title="Gaming Tier List Platform",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize session state variables"""
    defaults = {
        'authenticated': False,
        'guest_mode': False,
        'user_id': None,
        'username': None,
        'user_role': 'Regular',
        'virtual_currency': 10000,
        'current_theme': 'cyberpunk',
        'notifications_enabled': True,
        'show_analytics': False,
        'current_page': 'home'
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def load_custom_css():
    """Load enhanced CSS with working animations"""
    st.markdown("""
    <style>
    /* Base Theme */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 25%, #16213e 50%, #533483 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Floating Particles */
    .particle-system {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        pointer-events: none;
        z-index: 1;
        overflow: hidden;
    }
    
    .particle {
        position: absolute;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.8), transparent);
        animation: float 8s infinite ease-in-out;
    }
    
    .particle:nth-child(1) {
        width: 20px; height: 20px;
        top: 20%; left: 10%;
        background: radial-gradient(circle, rgba(255, 100, 100, 0.6), transparent);
        animation-duration: 6s;
        animation-delay: 0s;
    }
    
    .particle:nth-child(2) {
        width: 15px; height: 15px;
        top: 60%; right: 20%;
        background: radial-gradient(circle, rgba(100, 255, 100, 0.6), transparent);
        animation-duration: 8s;
        animation-delay: 2s;
    }
    
    .particle:nth-child(3) {
        width: 25px; height: 25px;
        bottom: 30%; left: 70%;
        background: radial-gradient(circle, rgba(100, 100, 255, 0.6), transparent);
        animation-duration: 10s;
        animation-delay: 4s;
    }
    
    .particle:nth-child(4) {
        width: 18px; height: 18px;
        top: 40%; left: 50%;
        background: radial-gradient(circle, rgba(255, 255, 100, 0.6), transparent);
        animation-duration: 7s;
        animation-delay: 1s;
    }
    
    .particle:nth-child(5) {
        width: 22px; height: 22px;
        bottom: 20%; right: 30%;
        background: radial-gradient(circle, rgba(255, 100, 255, 0.6), transparent);
        animation-duration: 9s;
        animation-delay: 3s;
    }
    
    @keyframes float {
        0%, 100% {
            transform: translateY(0px) translateX(0px);
            opacity: 0.7;
        }
        33% {
            transform: translateY(-30px) translateX(20px);
            opacity: 1;
        }
        66% {
            transform: translateY(-60px) translateX(-20px);
            opacity: 0.8;
        }
    }
    
    /* Modern Card Styling */
    .main-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Button Animations */
    .stButton > button {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 10px;
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        background: linear-gradient(45deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Enhanced Text */
    h1, h2, h3 {
        color: white;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 0.5rem 0;
    }
    </style>
    
    <!-- Particle System -->
    <div class="particle-system">
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
    </div>
    """, unsafe_allow_html=True)

def show_auth_page(auth_manager):
    """Clean authentication page"""
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("# 🎮 Gaming Platform")
        st.markdown("### Trade • Compete • Achieve")
        
        # Guest Mode
        if st.button("🚀 Continue as Guest", type="primary", use_container_width=True):
            st.session_state.guest_mode = True
            st.session_state.username = "Guest"
            st.rerun()
        
        st.markdown("---")
        
        # Authentication tabs
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Login", use_container_width=True):
                    if auth_manager.login(username, password):
                        st.success("Welcome back!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
        
        with tab2:
            with st.form("signup_form"):
                new_username = st.text_input("Choose Username")
                new_email = st.text_input("Email")
                new_password = st.text_input("Choose Password", type="password")
                if st.form_submit_button("Create Account", use_container_width=True):
                    if auth_manager.register(new_username, new_email, new_password):
                        st.success("Account created! Please login.")
                    else:
                        st.error("Username or email already exists")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_dashboard():
    """Main dashboard with clean layout"""
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    # Header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"# Welcome, {st.session_state.username}!")
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Balance", f"${st.session_state.virtual_currency:,}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        if st.button("Logout", type="secondary"):
            for key in ['authenticated', 'guest_mode', 'user_id', 'username']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    st.markdown("---")
    
    # Navigation
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
    
    with nav_col1:
        if st.button("🏆 Tier Lists", use_container_width=True):
            st.session_state.current_page = 'tiers'
            st.rerun()
    
    with nav_col2:
        if st.button("💰 Trading", use_container_width=True):
            st.session_state.current_page = 'trading'
            st.rerun()
    
    with nav_col3:
        if st.button("👤 Profile", use_container_width=True):
            st.session_state.current_page = 'profile'
            st.rerun()
    
    with nav_col4:
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.current_page = 'settings'
            st.rerun()
    
    # Quick Stats
    st.markdown("### 📊 Quick Stats")
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Characters Owned", "0", "0")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with stat_col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Trades", "0", "0")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with stat_col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Win Rate", "0%", "0%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with stat_col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Profit/Loss", "$0", "$0")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_tier_lists(tier_manager):
    """Display tier lists"""
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown("# 🏆 Character Tier Lists")
    
    if st.button("← Back to Dashboard"):
        st.session_state.current_page = 'home'
        st.rerun()
    
    # Get tier data
    tiers = tier_manager.get_tier_data()
    
    if not tiers.empty:
        # Tier tabs
        tier_tabs = st.tabs(["S Tier", "A Tier", "B Tier", "C Tier", "D Tier"])
        
        tier_levels = ['S', 'A', 'B', 'C', 'D']
        for i, tab in enumerate(tier_tabs):
            with tab:
                tier_chars = tiers[tiers['tier'] == tier_levels[i]]
                
                if not tier_chars.empty:
                    for _, char in tier_chars.iterrows():
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        
                        with col1:
                            st.markdown(f"**{char['name']}**")
                            st.caption(char['information'])
                        
                        with col2:
                            st.metric("Value", f"${char['value']:,.0f}")
                        
                        with col3:
                            st.metric("Demand", char['demand'])
                        
                        with col4:
                            trend_emoji = "📈" if char['trend'] == "Rising" else "📉" if char['trend'] == "Falling" else "➡️"
                            st.metric("Trend", f"{trend_emoji} {char['trend']}")
                        
                        st.markdown("---")
                else:
                    st.info(f"No characters in {tier_levels[i]} tier yet.")
    else:
        st.warning("No tier data available.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_trading(trading_manager, tier_manager):
    """Trading interface"""
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown("# 💰 Character Trading")
    
    if st.button("← Back to Dashboard"):
        st.session_state.current_page = 'home'
        st.rerun()
    
    # Trading interface
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Buy Characters")
        tiers = tier_manager.get_tier_data()
        
        if not tiers.empty:
            selected_char = st.selectbox("Select Character", tiers['name'].tolist())
            char_data = tiers[tiers['name'] == selected_char].iloc[0]
            
            st.metric("Current Price", f"${char_data['value']:,.0f}")
            st.metric("Demand Level", char_data['demand'])
            
            quantity = st.number_input("Quantity", min_value=1, value=1)
            total_cost = char_data['value'] * quantity
            
            st.metric("Total Cost", f"${total_cost:,.0f}")
            
            if st.button("Buy Character", type="primary", use_container_width=True):
                if st.session_state.virtual_currency >= total_cost:
                    # Process purchase
                    st.success(f"Purchased {quantity}x {selected_char} for ${total_cost:,.0f}!")
                    st.session_state.virtual_currency -= total_cost
                else:
                    st.error("Insufficient funds!")
    
    with col2:
        st.markdown("### Sell Characters")
        st.info("Your owned characters will appear here after purchasing.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_profile():
    """User profile page"""
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown("# 👤 Profile")
    
    if st.button("← Back to Dashboard"):
        st.session_state.current_page = 'home'
        st.rerun()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Account Info")
        st.info(f"**Username:** {st.session_state.username}")
        st.info(f"**Role:** {st.session_state.user_role}")
        st.info(f"**Balance:** ${st.session_state.virtual_currency:,}")
    
    with col2:
        st.markdown("### Statistics")
        st.metric("Total Trades", 0)
        st.metric("Characters Owned", 0)
        st.metric("Total Profit", "$0")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_settings():
    """Settings page"""
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown("# ⚙️ Settings")
    
    if st.button("← Back to Dashboard"):
        st.session_state.current_page = 'home'
        st.rerun()
    
    # Theme selection
    st.markdown("### 🎨 Theme")
    theme_options = ['cyberpunk', 'neon', 'galaxy', 'forest', 'ocean', 'sunset']
    selected_theme = st.selectbox("Choose Theme", theme_options, 
                                 index=theme_options.index(st.session_state.current_theme))
    
    if selected_theme != st.session_state.current_theme:
        st.session_state.current_theme = selected_theme
        st.success("Theme updated!")
        st.rerun()
    
    # Other settings
    st.markdown("### 🔔 Notifications")
    st.session_state.notifications_enabled = st.checkbox("Enable Notifications", 
                                                        value=st.session_state.notifications_enabled)
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application"""
    initialize_session_state()
    load_custom_css()
    
    # Initialize managers
    db_manager = DatabaseManager()
    auth_manager = AuthManager(db_manager)
    tier_manager = TierListManager(db_manager)
    trading_manager = TradingManager(db_manager)
    
    # Check authentication
    if not st.session_state.authenticated and not st.session_state.guest_mode:
        show_auth_page(auth_manager)
        return
    
    # Main navigation
    if st.session_state.current_page == 'home':
        show_dashboard()
    elif st.session_state.current_page == 'tiers':
        show_tier_lists(tier_manager)
    elif st.session_state.current_page == 'trading':
        show_trading(trading_manager, tier_manager)
    elif st.session_state.current_page == 'profile':
        show_profile()
    elif st.session_state.current_page == 'settings':
        show_settings()

if __name__ == "__main__":
    main()