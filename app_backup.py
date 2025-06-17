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
    /* Dynamic theme application */
    .stApp {{
        background: {theme['background']} !important;
        background-size: 400% 400% !important;
        background-attachment: fixed !important;
        animation: gradientShift 15s ease infinite !important;
        color: {theme['text']} !important;
        min-height: 100vh !important;
    }}
    
    @keyframes gradientShift {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    
    /* Container transparency */
    .main, .block-container {{
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
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
    
    # Apply theme
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
                if result['success']:
                    st.session_state.authenticated = True
                    st.session_state.user_id = result['user_id']
                    st.session_state.username = result['username']
                    st.session_state.user_role = result['role']
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(result['message'])
    
    with tab2:
        with st.form("signup_form"):
            new_username = st.text_input("Choose Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Choose Password", type="password")
            signup_submitted = st.form_submit_button("Sign Up", type="primary", use_container_width=True)
            
            if signup_submitted:
                result = auth_manager.register(new_username, new_email, new_password)
                if result['success']:
                    st.success("Account created successfully! Please login.")
                else:
                    st.error(result['message'])

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