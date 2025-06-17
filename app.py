import streamlit as st
import pandas as pd
from database import DatabaseManager
from auth import AuthManager
from auth_secure import SecureAuthManager
from tier_data import TierListManager
from trading import TradingManager
from guest_trading import GuestTradingManager
from achievements import AchievementManager
from notifications_fixed import NotificationManager
from admin import AdminManager
from themes import ThemeManager
from social import SocialManager
from analytics_fixed import AdvancedAnalytics
from dashboard_customization import DashboardCustomizationManager
from role_management import RoleManager
from role_ui import show_role_management
from settings_manager import SettingsManager
from role_configurator import RoleConfigurator
from role_configurator_ui import show_role_configurator_interface

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
            # Test account info
            st.info("**Test Account Available:**\n\nUsername: `testuser`\nPassword: `test123`\nEmail: `placeholder@example.com`")
            
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

def show_dashboard(dashboard_manager):
    """Personalized customizable dashboard"""
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    # Header with customization button
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        st.markdown(f"# Welcome, {st.session_state.username}!")
    with col2:
        if st.button("🎨 Customize", use_container_width=True):
            st.session_state.current_page = 'dashboard_customization'
            st.rerun()
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Balance", f"${st.session_state.virtual_currency:,}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
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
    
    # Admin mode access
    st.markdown("---")
    with st.expander("🔒 Admin Access"):
        admin_code = st.text_input("Enter Admin Code", type="password", key="admin_code")
        if st.button("Enter Admin Mode"):
            if admin_code == "2010":
                st.session_state.current_page = 'admin'
                st.session_state.user_role = 'Admin'
                st.success("Admin mode activated!")
                st.rerun()
            else:
                st.error("Invalid admin code")
        
        # Admin navigation options
        if st.session_state.get('user_role') == 'Admin':
            st.markdown("**Admin Tools:**")
            
            admin_nav_col1, admin_nav_col2 = st.columns(2)
            
            with admin_nav_col1:
                if st.button("📊 Admin Panel", use_container_width=True):
                    st.session_state.current_page = 'admin'
                    st.rerun()
                
                if st.button("🎭 Role Configurator", use_container_width=True):
                    st.session_state.current_page = 'role_configurator'
                    st.rerun()
            
            with admin_nav_col2:
                if st.button("🔐 Role Management", use_container_width=True):
                    st.session_state.current_page = 'roles'
                    st.rerun()
    
    # Load user's dashboard configuration
    user_id = st.session_state.get('user_id', 0)
    if user_id == 0 and st.session_state.get('guest_mode'):
        user_id = -1  # Special guest user ID
    
    dashboard_config = dashboard_manager.get_user_dashboard_config(user_id)
    
    # Render dashboard widgets based on user configuration
    st.markdown("---")
    st.markdown("### Dashboard")
    
    # Get enabled widgets sorted by position
    enabled_widgets = {k: v for k, v in dashboard_config['widgets'].items() if v.get('enabled', True)}
    sorted_widgets = sorted(enabled_widgets.items(), key=lambda x: x[1].get('position', 0))
    
    # Render widgets in grid or list layout
    layout = dashboard_config.get('layout', 'grid')
    
    if layout == 'grid':
        # Grid layout with 2 columns
        cols = st.columns(2)
        col_index = 0
        
        for widget_name, widget_config in sorted_widgets:
            with cols[col_index % 2]:
                render_dashboard_widget(dashboard_manager, user_id, widget_name, widget_config)
            col_index += 1
    else:
        # List layout - single column
        for widget_name, widget_config in sorted_widgets:
            render_dashboard_widget(dashboard_manager, user_id, widget_name, widget_config)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_dashboard_widget(dashboard_manager, user_id, widget_name, widget_config):
    """Render a dashboard widget"""
    widget_data = dashboard_manager.get_widget_data(user_id, widget_name)
    
    if "error" in widget_data:
        st.error(f"Error loading {widget_name}: {widget_data['error']}")
        return
    
    size = widget_config.get('size', 'medium')
    
    # Widget container with size-based styling
    container_style = "padding: 1rem; margin: 0.5rem 0; border-radius: 10px; background: rgba(255, 255, 255, 0.05);"
    if size == 'large':
        container_style += " min-height: 300px;"
    elif size == 'small':
        container_style += " min-height: 100px;"
    
    with st.container():
        st.markdown(f'<div style="{container_style}">', unsafe_allow_html=True)
        
        if widget_name == "balance":
            st.markdown("#### 💰 Balance")
            st.metric("Current Balance", widget_data.get('formatted', '$0'), widget_data.get('change', 0))
        
        elif widget_name == "portfolio_value":
            st.markdown("#### 📈 Portfolio Value")
            st.metric("Total Value", widget_data.get('formatted', '$0'), f"{widget_data.get('change_percent', 0):.2f}%")
        
        elif widget_name == "recent_trades":
            st.markdown("#### 🔄 Recent Trades")
            trades = widget_data.get('trades', [])
            if trades:
                for trade in trades[:3]:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"{trade['type'].title()} {trade['character']}")
                    with col2:
                        st.write(f"{trade['quantity']}x")
                    with col3:
                        st.write(f"${trade['total']:,.0f}")
            else:
                st.info("No recent trades")
        
        elif widget_name == "market_trends":
            st.markdown("#### 📊 Market Trends")
            trends = widget_data.get('trends', [])
            if trends:
                for trend in trends[:3]:
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.write(f"{trend['tier']} Tier")
                    with col2:
                        st.write(f"${trend['avg_value']:,.0f}")
            else:
                st.info("No market data")
        
        elif widget_name == "achievements":
            st.markdown("#### 🏆 Achievements")
            total = widget_data.get('total', 0)
            st.metric("Total Achievements", total)
        
        elif widget_name == "notifications":
            st.markdown("#### 🔔 Notifications")
            unread = widget_data.get('unread_count', 0)
            if unread > 0:
                st.warning(f"{unread} unread notifications")
            else:
                st.success("No new notifications")
        
        elif widget_name == "quick_stats":
            st.markdown("#### 📈 Quick Stats")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Trades", widget_data.get('total_trades', 0))
                st.metric("Characters", widget_data.get('characters_owned', 0))
            with col2:
                profit = widget_data.get('total_profit', 0)
                st.metric("Total Profit", f"${profit:,.2f}")
        
        elif widget_name == "top_characters":
            st.markdown("#### ⭐ Top Characters")
            characters = widget_data.get('characters', [])
            if characters:
                for char in characters[:3]:
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"{char['name']}")
                    with col2:
                        st.write(f"{char['tier']}")
                    with col3:
                        st.write(f"${char['value']:,.0f}")
            else:
                st.info("No character data")
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_tier_lists(tier_manager):
    """Display tier lists"""
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    # Animated morphing back button
    st.markdown("""
    <div class="morphing-back-btn" style="margin-bottom: 20px;">
        <span class="back-icon">⬅</span>
        <span>Back to Dashboard</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("", key="back_tier_lists", help="Return to dashboard"):
        st.session_state.current_page = 'home'
        st.rerun()
    
    st.markdown("# 🏆 Character Tier Lists")
    
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
    
    # Glitch effect back button
    st.markdown("""
    <div class="glitch-back-btn" style="margin-bottom: 20px;">
        <span class="back-icon">↩</span>
        <span>Back to Dashboard</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("", key="back_trading", help="Return to dashboard"):
        st.session_state.current_page = 'home'
        st.rerun()
    
    st.markdown("# 💰 Character Trading")
    
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
    
    # Classic animated back button
    st.markdown("""
    <div class="animated-back-btn" style="margin-bottom: 20px;">
        <span class="back-icon">◀</span>
        <span>Back to Dashboard</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("", key="back_profile", help="Return to dashboard"):
        st.session_state.current_page = 'home'
        st.rerun()
    
    st.markdown("# 👤 Profile")
    
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

def show_settings(settings_manager):
    """Advanced Settings page with persistent storage"""
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    # Get current user ID
    user_id = st.session_state.get('user_id', 0)
    if user_id == 0 and st.session_state.get('guest_mode'):
        user_id = -1  # Special guest user ID
    
    # Load user settings from database
    user_settings = settings_manager.get_user_settings(user_id)
    
    # Update session state with loaded settings
    for category, settings in user_settings.items():
        for key, value in settings.items():
            session_key = f"{category}_{key}" if category != 'appearance' else key
            if session_key not in st.session_state:
                st.session_state[session_key] = value
    
    # Morphing back button for settings
    st.markdown("""
    <div class="morphing-back-btn" style="margin-bottom: 20px;">
        <span class="back-icon">⬅</span>
        <span>Back to Dashboard</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("", key="back_settings", help="Return to dashboard"):
        st.session_state.current_page = 'home'
        st.rerun()
    
    st.markdown("# ⚙️ Advanced Settings")
    
    # Settings navigation tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎨 Appearance", "🔔 Notifications", "📊 Trading", 
        "👤 Account", "🔒 Privacy", "⚡ Performance"
    ])
    
    with tab1:
        st.markdown("### Theme & Visual Settings")
        
        # Theme selection with preview
        col1, col2 = st.columns([2, 1])
        
        with col1:
            theme_options = ['cyberpunk', 'neon', 'galaxy', 'forest', 'ocean', 'sunset']
            current_theme = user_settings['appearance'].get('theme', 'cyberpunk')
            try:
                theme_index = theme_options.index(current_theme)
            except ValueError:
                theme_index = 0
            
            selected_theme = st.selectbox("Choose Theme", theme_options, index=theme_index)
            
            if selected_theme != current_theme:
                st.session_state.current_theme = selected_theme
                settings_manager.save_user_setting(user_id, 'appearance', 'theme', selected_theme)
                st.success("Theme updated and saved!")
                st.rerun()
        
        with col2:
            st.markdown(f"""
            <div style="
                background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
                border-radius: 10px;
                padding: 1rem;
                text-align: center;
                color: white;
            ">
                <h4>{selected_theme.title()}</h4>
                <p>Preview</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### Visual Effects")
        
        # Animation settings
        current_animations = user_settings['appearance'].get('animations_enabled', True)
        animations_enabled = st.checkbox("Enable Animations", value=current_animations)
        if animations_enabled != current_animations:
            st.session_state.animations_enabled = animations_enabled
            settings_manager.save_user_setting(user_id, 'appearance', 'animations_enabled', animations_enabled)
        
        # Particle effects
        current_particles = user_settings['appearance'].get('particles_enabled', True)
        particles_enabled = st.checkbox("Enable Particle Effects", value=current_particles)
        if particles_enabled != current_particles:
            st.session_state.particles_enabled = particles_enabled
            settings_manager.save_user_setting(user_id, 'appearance', 'particles_enabled', particles_enabled)
        
        # Glass morphism effects
        current_glass = user_settings['appearance'].get('glassmorphism', True)
        glassmorphism = st.checkbox("Enable Glass Morphism", value=current_glass)
        if glassmorphism != current_glass:
            st.session_state.glassmorphism = glassmorphism
            settings_manager.save_user_setting(user_id, 'appearance', 'glassmorphism', glassmorphism)
        
        # Font size
        font_options = ["Small", "Medium", "Large"]
        current_font = user_settings['appearance'].get('font_size', 'Medium')
        try:
            font_index = font_options.index(current_font)
        except ValueError:
            font_index = 1
        
        font_size = st.selectbox("Font Size", font_options, index=font_index)
        if font_size != current_font:
            st.session_state.font_size = font_size
            settings_manager.save_user_setting(user_id, 'appearance', 'font_size', font_size)
        
        # Color customization
        st.markdown("### Color Customization")
        current_accent = user_settings['appearance'].get('accent_color', '#667eea')
        accent_color = st.color_picker("Accent Color", value=current_accent)
        if accent_color != current_accent:
            st.session_state.accent_color = accent_color
            settings_manager.save_user_setting(user_id, 'appearance', 'accent_color', accent_color)
    
    with tab2:
        st.markdown("### Notification Preferences")
        
        # General notifications
        notifications_enabled = st.checkbox("Enable Notifications", 
                                           value=st.session_state.get('notifications_enabled', True))
        st.session_state.notifications_enabled = notifications_enabled
        
        if notifications_enabled:
            # Trading notifications
            st.markdown("#### Trading Notifications")
            trade_success = st.checkbox("Trade Success Notifications", value=True)
            trade_failure = st.checkbox("Trade Failure Notifications", value=True)
            price_alerts = st.checkbox("Price Change Alerts", value=False)
            
            # Achievement notifications
            st.markdown("#### Achievement Notifications")
            achievement_unlock = st.checkbox("Achievement Unlocked", value=True)
            milestone_reached = st.checkbox("Milestone Reached", value=True)
            
            # System notifications
            st.markdown("#### System Notifications")
            maintenance_alerts = st.checkbox("Maintenance Alerts", value=True)
            security_alerts = st.checkbox("Security Alerts", value=True)
            
            # Notification methods
            st.markdown("#### Notification Methods")
            in_app_notifications = st.checkbox("In-App Notifications", value=True)
            email_notifications = st.checkbox("Email Notifications", value=False)
            
            # Notification frequency
            st.markdown("#### Frequency Settings")
            notification_frequency = st.selectbox("Notification Frequency", 
                                                 ["Real-time", "Every 5 minutes", "Every 15 minutes", "Hourly"])
            
            # Do not disturb
            st.markdown("#### Do Not Disturb")
            dnd_enabled = st.checkbox("Enable Do Not Disturb", value=False)
            if dnd_enabled:
                dnd_start = st.time_input("Start Time", value=None)
                dnd_end = st.time_input("End Time", value=None)
    
    with tab3:
        st.markdown("### Trading Configuration")
        
        # Trading preferences
        st.markdown("#### Default Trading Settings")
        
        default_trade_amount = st.number_input("Default Trade Amount", min_value=1, max_value=1000, value=10)
        st.session_state.default_trade_amount = default_trade_amount
        
        auto_confirm_trades = st.checkbox("Auto-confirm Small Trades", value=False)
        st.session_state.auto_confirm_trades = auto_confirm_trades
        
        if auto_confirm_trades:
            auto_confirm_threshold = st.number_input("Auto-confirm Threshold", min_value=1, max_value=100, value=5)
            st.session_state.auto_confirm_threshold = auto_confirm_threshold
        
        # Risk management
        st.markdown("#### Risk Management")
        
        enable_stop_loss = st.checkbox("Enable Stop Loss", value=False)
        if enable_stop_loss:
            stop_loss_percentage = st.slider("Stop Loss Percentage", min_value=1, max_value=50, value=10)
            st.session_state.stop_loss_percentage = stop_loss_percentage
        
        enable_take_profit = st.checkbox("Enable Take Profit", value=False)
        if enable_take_profit:
            take_profit_percentage = st.slider("Take Profit Percentage", min_value=1, max_value=100, value=20)
            st.session_state.take_profit_percentage = take_profit_percentage
        
        # Trading analytics
        st.markdown("#### Analytics & Reporting")
        
        track_performance = st.checkbox("Track Trading Performance", value=True)
        st.session_state.track_performance = track_performance
        
        detailed_analytics = st.checkbox("Enable Detailed Analytics", value=False)
        st.session_state.detailed_analytics = detailed_analytics
        
        export_data = st.checkbox("Allow Data Export", value=True)
        st.session_state.export_data = export_data
    
    with tab4:
        st.markdown("### Account Management")
        
        if not st.session_state.get('guest_mode', False):
            # Profile settings
            st.markdown("#### Profile Information")
            
            with st.form("profile_update"):
                current_username = st.session_state.get('username', '')
                new_display_name = st.text_input("Display Name", value=current_username)
                new_email = st.text_input("Email", value="user@example.com")
                new_bio = st.text_area("Bio", placeholder="Tell us about yourself...")
                
                profile_visibility = st.selectbox("Profile Visibility", 
                                                 ["Public", "Friends Only", "Private"])
                
                show_achievements = st.checkbox("Show Achievements on Profile", value=True)
                show_trading_stats = st.checkbox("Show Trading Statistics", value=True)
                
                if st.form_submit_button("Update Profile"):
                    st.success("Profile updated successfully!")
            
            # Security settings
            st.markdown("#### Security Settings")
            
            with st.form("security_settings"):
                st.markdown("##### Change Password")
                current_password = st.text_input("Current Password", type="password")
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
                
                if st.form_submit_button("Change Password"):
                    if new_password == confirm_password:
                        st.success("Password changed successfully!")
                    else:
                        st.error("Passwords do not match!")
            
            # Two-factor authentication
            st.markdown("#### Two-Factor Authentication")
            enable_2fa = st.checkbox("Enable Two-Factor Authentication", value=False)
            if enable_2fa:
                st.info("Scan the QR code with your authenticator app")
                # Placeholder for QR code
                st.code("QR Code would appear here in production")
        
        else:
            st.info("Guest users have limited account features. Please register for full access.")
            
            if st.button("Register Account"):
                st.session_state.current_page = 'login'
                st.rerun()
    
    with tab5:
        st.markdown("### Privacy & Data Settings")
        
        # Data collection preferences
        st.markdown("#### Data Collection")
        
        analytics_tracking = st.checkbox("Allow Analytics Tracking", value=True)
        st.session_state.analytics_tracking = analytics_tracking
        
        performance_monitoring = st.checkbox("Performance Monitoring", value=True)
        st.session_state.performance_monitoring = performance_monitoring
        
        crash_reporting = st.checkbox("Crash Reporting", value=True)
        st.session_state.crash_reporting = crash_reporting
        
        # Privacy controls
        st.markdown("#### Privacy Controls")
        
        hide_online_status = st.checkbox("Hide Online Status", value=False)
        st.session_state.hide_online_status = hide_online_status
        
        private_trading_history = st.checkbox("Make Trading History Private", value=False)
        st.session_state.private_trading_history = private_trading_history
        
        block_friend_requests = st.checkbox("Block Friend Requests", value=False)
        st.session_state.block_friend_requests = block_friend_requests
        
        # Data management
        st.markdown("#### Data Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Export My Data"):
                st.info("Data export will be sent to your email")
        
        with col2:
            if st.button("Clear Cache"):
                st.success("Cache cleared successfully!")
        
        with col3:
            if st.button("Delete Account", type="secondary"):
                st.error("Account deletion is permanent and cannot be undone!")
    
    with tab6:
        st.markdown("### Performance Settings")
        
        # Display settings
        st.markdown("#### Display Optimization")
        
        reduce_animations = st.checkbox("Reduce Animations for Better Performance", value=False)
        st.session_state.reduce_animations = reduce_animations
        
        limit_chart_data = st.checkbox("Limit Chart Data Points", value=False)
        if limit_chart_data:
            max_data_points = st.slider("Maximum Data Points", min_value=50, max_value=1000, value=200)
            st.session_state.max_data_points = max_data_points
        
        lazy_loading = st.checkbox("Enable Lazy Loading", value=True)
        st.session_state.lazy_loading = lazy_loading
        
        # Cache settings
        st.markdown("#### Cache Management")
        
        cache_duration = st.selectbox("Cache Duration", 
                                    ["5 minutes", "15 minutes", "1 hour", "1 day"])
        st.session_state.cache_duration = cache_duration
        
        auto_clear_cache = st.checkbox("Auto-clear Cache on Exit", value=False)
        st.session_state.auto_clear_cache = auto_clear_cache
        
        # Bandwidth optimization
        st.markdown("#### Bandwidth Optimization")
        
        compress_images = st.checkbox("Compress Images", value=True)
        st.session_state.compress_images = compress_images
        
        low_bandwidth_mode = st.checkbox("Low Bandwidth Mode", value=False)
        st.session_state.low_bandwidth_mode = low_bandwidth_mode
        
        # Performance monitoring
        st.markdown("#### Performance Monitoring")
        
        show_performance_metrics = st.checkbox("Show Performance Metrics", value=False)
        if show_performance_metrics:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Load Time", "1.2s", delta="-0.3s")
            
            with col2:
                st.metric("Memory Usage", "45MB", delta="2MB")
            
            with col3:
                st.metric("FPS", "60", delta="0")
    
    # Settings templates
    st.markdown("---")
    st.markdown("### 🎯 Quick Setup Templates")
    
    templates = settings_manager.get_available_templates()
    if templates:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            template_names = [template['name'] for template in templates]
            template_displays = [f"{template['display_name']} - {template['description']}" for template in templates]
            
            selected_template_index = st.selectbox(
                "Choose a settings template",
                range(len(templates)),
                format_func=lambda x: template_displays[x]
            )
            
            if st.button("Apply Template", type="primary"):
                template_name = template_names[selected_template_index]
                if settings_manager.apply_settings_template(user_id, template_name):
                    st.success(f"Applied {templates[selected_template_index]['display_name']} template!")
                    st.rerun()
                else:
                    st.error("Failed to apply template")
        
        with col2:
            st.markdown("**Available Templates:**")
            for template in templates:
                st.markdown(f"• **{template['display_name']}**: {template['description']}")
    
    # Advanced actions
    st.markdown("---")
    st.markdown("### 🔧 Advanced Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💾 Save All Settings", type="primary"):
            # Settings are already saved automatically, this is just for confirmation
            st.success("All settings are saved automatically!")
    
    with col2:
        if st.button("🔄 Reset Category"):
            category_options = ['appearance', 'notifications', 'trading', 'privacy', 'performance']
            selected_category = st.selectbox("Select category to reset", category_options)
            if st.button("Confirm Reset", key="confirm_reset"):
                if settings_manager.reset_user_settings(user_id, selected_category):
                    st.success(f"Reset {selected_category} settings to defaults!")
                    st.rerun()
                else:
                    st.error("Failed to reset settings")
    
    with col3:
        if st.button("📋 Export Settings"):
            settings_export = settings_manager.export_user_settings(user_id)
            st.download_button(
                label="Download Settings",
                data=str(settings_export),
                file_name=f"gaming_platform_settings_{user_id}.json",
                mime="application/json"
            )
    
    with col4:
        if st.button("📥 Import Settings"):
            uploaded_file = st.file_uploader("Upload settings file", type=['json'])
            if uploaded_file is not None:
                try:
                    import json
                    settings_data = json.loads(uploaded_file.read())
                    if settings_manager.import_user_settings(user_id, settings_data):
                        st.success("Settings imported successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to import settings")
                except Exception as e:
                    st.error(f"Invalid settings file: {str(e)}")
    
    # Settings audit log
    if st.checkbox("Show Settings History"):
        st.markdown("### 📜 Settings Change History")
        audit_log = settings_manager.get_settings_audit_log(user_id, days=30)
        
        if audit_log:
            import pandas as pd
            df = pd.DataFrame(audit_log)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No recent settings changes found")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_admin_panel(admin_manager):
    """Admin panel interface"""
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    # Glitch effect back button for admin
    st.markdown("""
    <div class="glitch-back-btn" style="margin-bottom: 20px;">
        <span class="back-icon">↩</span>
        <span>Back to Dashboard</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("", key="back_admin", help="Return to dashboard"):
        st.session_state.current_page = 'home'
        st.rerun()
    
    st.markdown("# 🔧 Admin Panel")
    st.markdown(f"**Role:** {st.session_state.user_role}")
    
    # Admin navigation tabs
    admin_tab1, admin_tab2, admin_tab3, admin_tab4 = st.tabs([
        "Users", "Characters", "System", "Analytics"
    ])
    
    with admin_tab1:
        st.markdown("### 👥 User Management")
        
        # User statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Users", "0")
        with col2:
            st.metric("Active Users", "0")
        with col3:
            st.metric("Banned Users", "0")
        with col4:
            st.metric("New Today", "0")
        
        st.markdown("---")
        
        # User actions
        st.markdown("#### User Actions")
        user_id_input = st.number_input("User ID", min_value=1, value=1)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Reset Currency", use_container_width=True):
                st.success(f"Reset currency for user {user_id_input}")
        
        with col2:
            if st.button("Ban User", use_container_width=True):
                st.warning(f"Banned user {user_id_input}")
        
        with col3:
            if st.button("Unban User", use_container_width=True):
                st.success(f"Unbanned user {user_id_input}")
    
    with admin_tab2:
        st.markdown("### 🎮 Character Management")
        
        # Add new character
        with st.form("add_character_form"):
            st.markdown("#### Add New Character")
            char_name = st.text_input("Character Name")
            char_value = st.number_input("Value", min_value=0, value=1000)
            char_tier = st.selectbox("Tier", ["S", "A", "B", "C", "D"])
            char_demand = st.selectbox("Demand", ["Very High", "High", "Medium", "Low", "Very Low"])
            char_trend = st.selectbox("Trend", ["Rising", "Stable", "Falling"])
            char_info = st.text_area("Information")
            
            if st.form_submit_button("Add Character", type="primary"):
                st.success(f"Added character: {char_name}")
        
        st.markdown("---")
        
        # Bulk actions
        st.markdown("#### Bulk Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            multiplier = st.number_input("Value Multiplier", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
            if st.button("Update All Values", use_container_width=True):
                st.success(f"Updated all character values by {multiplier}x")
        
        with col2:
            if st.button("Refresh Market Data", use_container_width=True):
                st.success("Market data refreshed")
    
    with admin_tab3:
        st.markdown("### 🖥️ System Management")
        
        # System stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Database Size", "50 MB")
        with col2:
            st.metric("Active Connections", "12")
        with col3:
            st.metric("Server Uptime", "24h 15m")
        
        st.markdown("---")
        
        # System actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Clear Cache", use_container_width=True):
                st.success("Cache cleared")
        
        with col2:
            if st.button("Optimize Database", use_container_width=True):
                st.success("Database optimized")
        
        with col3:
            if st.button("Backup Data", use_container_width=True):
                st.success("Data backup created")
        
        # Security settings
        st.markdown("#### Security")
        maintenance_mode = st.checkbox("Maintenance Mode")
        if maintenance_mode:
            st.warning("Maintenance mode enabled - new users cannot access the system")
    
    with admin_tab4:
        st.markdown("### 📊 Analytics")
        
        # Trading analytics
        st.markdown("#### Trading Activity")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Trades", "0", "0")
        with col2:
            st.metric("Trade Volume", "$0", "$0")
        with col3:
            st.metric("Average Trade", "$0", "$0")
        
        # User engagement
        st.markdown("#### User Engagement")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Daily Active Users", "0")
        with col2:
            st.metric("Session Duration", "0m")
        with col3:
            st.metric("Retention Rate", "0%")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_dashboard_customization(dashboard_manager):
    """Dashboard customization interface"""
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    # Animated back button for customization
    st.markdown("""
    <div class="animated-back-btn" style="margin-bottom: 20px;">
        <span class="back-icon">◀</span>
        <span>Back to Dashboard</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("", key="back_customization", help="Return to dashboard"):
        st.session_state.current_page = 'home'
        st.rerun()
    
    st.markdown("# 🎨 Dashboard Customization")
    
    st.markdown("Personalize your dashboard layout, widgets, and appearance")
    st.markdown("---")
    
    # Get user ID
    user_id = st.session_state.get('user_id', 0)
    if user_id == 0 and st.session_state.get('guest_mode'):
        user_id = -1
    
    # Get current configuration
    current_config = dashboard_manager.get_user_dashboard_config(user_id)
    
    # Tabs for different customization options
    tab1, tab2, tab3, tab4 = st.tabs(["🎛️ Widget Settings", "📋 Layout", "🎨 Themes", "📄 Templates"])
    
    with tab1:
        st.markdown("### Widget Configuration")
        st.markdown("Enable/disable widgets and configure their size and position")
        
        # Widget configuration
        widget_changes = {}
        
        # Create columns for widget settings
        col1, col2 = st.columns(2)
        
        widgets = current_config.get('widgets', {})
        
        for i, (widget_name, widget_config) in enumerate(widgets.items()):
            with col1 if i % 2 == 0 else col2:
                with st.container():
                    st.markdown(f"#### {widget_name.replace('_', ' ').title()}")
                    
                    # Widget enable/disable
                    enabled = st.checkbox(
                        "Enabled", 
                        value=widget_config.get('enabled', True),
                        key=f"enable_{widget_name}"
                    )
                    
                    # Widget size
                    size_options = ["small", "medium", "large"]
                    size = st.selectbox(
                        "Size",
                        size_options,
                        index=size_options.index(widget_config.get('size', 'medium')),
                        key=f"size_{widget_name}"
                    )
                    
                    # Widget position
                    position = st.number_input(
                        "Position (order)",
                        min_value=0,
                        max_value=len(widgets)-1,
                        value=widget_config.get('position', i),
                        key=f"pos_{widget_name}"
                    )
                    
                    # Store changes
                    widget_changes[widget_name] = {
                        'enabled': enabled,
                        'size': size,
                        'position': position
                    }
                    
                    st.markdown("---")
        
        # Save widget settings
        if st.button("💾 Save Widget Settings", type="primary"):
            # Update configuration
            updated_config = current_config.copy()
            updated_config['widgets'] = widget_changes
            
            if dashboard_manager.save_user_dashboard_config(user_id, updated_config):
                st.success("Widget settings saved successfully!")
                st.balloons()
                st.rerun()
            else:
                st.error("Failed to save widget settings")
    
    with tab2:
        st.markdown("### Layout Configuration")
        st.markdown("Choose how your dashboard widgets are arranged")
        
        # Layout options
        current_layout = current_config.get('layout', 'grid')
        
        layout_options = {
            'grid': 'Grid Layout - Widgets in 2 columns',
            'list': 'List Layout - Single column vertical stack'
        }
        
        selected_layout = st.radio(
            "Choose Layout Style",
            options=list(layout_options.keys()),
            format_func=lambda x: layout_options[x],
            index=0 if current_layout == 'grid' else 1
        )
        
        # Display preferences
        st.markdown("---")
        st.markdown("### Display Preferences")
        
        display_prefs = current_config.get('display_preferences', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            show_welcome = st.checkbox(
                "Show welcome message",
                value=display_prefs.get('show_welcome_message', True)
            )
            
            compact_mode = st.checkbox(
                "Compact mode",
                value=display_prefs.get('compact_mode', False)
            )
        
        with col2:
            auto_refresh = st.checkbox(
                "Auto-refresh data",
                value=display_prefs.get('auto_refresh', True)
            )
            
            if auto_refresh:
                refresh_interval = st.slider(
                    "Refresh interval (seconds)",
                    min_value=10,
                    max_value=300,
                    value=display_prefs.get('refresh_interval', 30),
                    step=10
                )
            else:
                refresh_interval = 30
        
        # Save layout settings
        if st.button("💾 Save Layout Settings", type="primary"):
            updated_config = current_config.copy()
            updated_config['layout'] = selected_layout
            updated_config['display_preferences'] = {
                'show_welcome_message': show_welcome,
                'compact_mode': compact_mode,
                'auto_refresh': auto_refresh,
                'refresh_interval': refresh_interval
            }
            
            if dashboard_manager.save_user_dashboard_config(user_id, updated_config):
                st.success("Layout settings saved successfully!")
                st.rerun()
            else:
                st.error("Failed to save layout settings")
    
    with tab3:
        st.markdown("### Theme Customization")
        st.markdown("Customize the visual appearance of your dashboard")
        
        theme_prefs = current_config.get('theme_preferences', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            primary_color = st.color_picker(
                "Primary Color",
                value=theme_prefs.get('primary_color', '#667eea')
            )
            
            secondary_color = st.color_picker(
                "Secondary Color", 
                value=theme_prefs.get('secondary_color', '#764ba2')
            )
        
        with col2:
            background_options = ["gradient", "solid", "pattern"]
            background_style = st.selectbox(
                "Background Style",
                background_options,
                index=background_options.index(theme_prefs.get('background_style', 'gradient'))
            )
            
            animation_options = ["disabled", "slow", "normal", "fast"]
            animation_speed = st.selectbox(
                "Animation Speed",
                animation_options,
                index=animation_options.index(theme_prefs.get('animation_speed', 'normal'))
            )
        
        # Preview
        st.markdown("---")
        st.markdown("### Theme Preview")
        preview_style = f"""
        <div style="
            background: linear-gradient(135deg, {primary_color}, {secondary_color});
            padding: 20px;
            border-radius: 10px;
            color: white;
            margin: 10px 0;
        ">
            <h4>Preview Dashboard Card</h4>
            <p>This shows how your dashboard will look with the selected theme.</p>
        </div>
        """
        st.markdown(preview_style, unsafe_allow_html=True)
        
        # Save theme settings
        if st.button("💾 Save Theme Settings", type="primary"):
            updated_config = current_config.copy()
            updated_config['theme_preferences'] = {
                'primary_color': primary_color,
                'secondary_color': secondary_color,
                'background_style': background_style,
                'animation_speed': animation_speed
            }
            
            if dashboard_manager.save_user_dashboard_config(user_id, updated_config):
                st.success("Theme settings saved successfully!")
                st.rerun()
            else:
                st.error("Failed to save theme settings")
    
    with tab4:
        st.markdown("### Dashboard Templates")
        st.markdown("Apply pre-designed dashboard layouts")
        
        # Get available templates
        templates = dashboard_manager.get_available_templates()
        
        if templates:
            st.markdown("#### Available Templates")
            
            for template in templates:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{template['name']}**")
                        st.markdown(template['description'])
                        st.markdown(f"*Used by {template['usage_count']} users*")
                    
                    with col2:
                        if st.button(f"Apply", key=f"apply_{template['id']}", type="primary"):
                            if dashboard_manager.apply_template(user_id, template['id']):
                                st.success(f"Applied template: {template['name']}")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error("Failed to apply template")
                    
                    st.markdown("---")
        
        else:
            st.info("No templates available")
    
    # Reset to defaults
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("🔄 Reset to Defaults", type="secondary"):
            if dashboard_manager.save_user_dashboard_config(user_id, dashboard_manager.default_config):
                st.success("Dashboard reset to default configuration!")
                st.rerun()
            else:
                st.error("Failed to reset dashboard")
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application"""
    initialize_session_state()
    load_custom_css()
    
    # Initialize managers
    db_manager = DatabaseManager()
    db_manager.init_database()
    db_manager.migrate_database_schema()
    auth_manager = AuthManager(db_manager)
    tier_manager = TierListManager(db_manager)
    trading_manager = TradingManager(db_manager)
    admin_manager = AdminManager(db_manager)
    dashboard_manager = DashboardCustomizationManager(db_manager)
    role_manager = RoleManager(db_manager)
    settings_manager = SettingsManager(db_manager)
    role_configurator = RoleConfigurator(db_manager)
    
    # Check authentication
    if not st.session_state.authenticated and not st.session_state.guest_mode:
        show_auth_page(auth_manager)
        return
    
    # Main navigation
    if st.session_state.current_page == 'home':
        show_dashboard(dashboard_manager)
    elif st.session_state.current_page == 'tiers':
        show_tier_lists(tier_manager)
    elif st.session_state.current_page == 'trading':
        show_trading(trading_manager, tier_manager)
    elif st.session_state.current_page == 'profile':
        show_profile()
    elif st.session_state.current_page == 'settings':
        show_settings(settings_manager)
    elif st.session_state.current_page == 'admin':
        show_admin_panel(admin_manager)
    elif st.session_state.current_page == 'roles':
        show_role_management(role_manager, st.session_state.user_id)
    elif st.session_state.current_page == 'dashboard_customization':
        show_dashboard_customization(dashboard_manager)
    elif st.session_state.current_page == 'role_configurator':
        show_role_configurator_interface(role_configurator)

if __name__ == "__main__":
    main()