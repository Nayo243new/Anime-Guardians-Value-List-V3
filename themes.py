import streamlit as st
from datetime import datetime
import base64
import io
from PIL import Image
import json

class ThemeManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.themes = {
            'futuristic': {
                'name': 'Futuristic Cyber',
                'primary_color': '#00f5ff',
                'secondary_color': '#ff00ff',
                'background_color': '#0a0a0a',
                'text_color': '#ffffff',
                'accent_color': '#39ff14',
                'gradient': 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%)',
                'border_style': '2px solid #00f5ff',
                'shadow': '0 0 20px rgba(0, 245, 255, 0.3)',
                'animation': 'glow 2s ease-in-out infinite alternate',
                'description': 'Cyberpunk-inspired neon aesthetics'
            },
            'aquatic': {
                'name': 'Ocean Depths',
                'primary_color': '#00bfff',
                'secondary_color': '#20b2aa',
                'background_color': '#001a33',
                'text_color': '#e6f3ff',
                'accent_color': '#7fffd4',
                'gradient': 'linear-gradient(135deg, #001a33 0%, #003366 50%, #004080 100%)',
                'border_style': '2px solid #00bfff',
                'shadow': '0 0 15px rgba(0, 191, 255, 0.4)',
                'animation': 'wave 3s ease-in-out infinite',
                'description': 'Deep ocean tranquility with flowing water effects'
            },
            'heavenly': {
                'name': 'Celestial Light',
                'primary_color': '#ffd700',
                'secondary_color': '#fff8dc',
                'background_color': '#f0f8ff',
                'text_color': '#4a4a4a',
                'accent_color': '#87ceeb',
                'gradient': 'linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 50%, #ddeeff 100%)',
                'border_style': '2px solid #ffd700',
                'shadow': '0 0 25px rgba(255, 215, 0, 0.2)',
                'animation': 'shimmer 4s ease-in-out infinite',
                'description': 'Ethereal golden light with heavenly ambiance'
            },
            'dark_mode': {
                'name': 'Midnight Elite',
                'primary_color': '#bb86fc',
                'secondary_color': '#03dac6',
                'background_color': '#121212',
                'text_color': '#ffffff',
                'accent_color': '#cf6679',
                'gradient': 'linear-gradient(135deg, #121212 0%, #1e1e1e 50%, #2a2a2a 100%)',
                'border_style': '2px solid #bb86fc',
                'shadow': '0 0 10px rgba(187, 134, 252, 0.3)',
                'animation': 'pulse 2s ease-in-out infinite',
                'description': 'Professional dark theme with purple accents'
            },
            'nature': {
                'name': 'Forest Harmony',
                'primary_color': '#228b22',
                'secondary_color': '#32cd32',
                'background_color': '#f0fff0',
                'text_color': '#2d4a2d',
                'accent_color': '#90ee90',
                'gradient': 'linear-gradient(135deg, #f0fff0 0%, #e8f5e8 50%, #d0e8d0 100%)',
                'border_style': '2px solid #228b22',
                'shadow': '0 0 15px rgba(34, 139, 34, 0.2)',
                'animation': 'sway 3s ease-in-out infinite',
                'description': 'Peaceful nature-inspired green theme'
            },
            'sunset': {
                'name': 'Sunset Blaze',
                'primary_color': '#ff6b35',
                'secondary_color': '#f7931e',
                'background_color': '#1a1a1a',
                'text_color': '#fff5e6',
                'accent_color': '#ffcc70',
                'gradient': 'linear-gradient(135deg, #1a1a1a 0%, #2d1b1b 50%, #4d2a1a 100%)',
                'border_style': '2px solid #ff6b35',
                'shadow': '0 0 20px rgba(255, 107, 53, 0.3)',
                'animation': 'flicker 2.5s ease-in-out infinite',
                'description': 'Warm sunset colors with fiery accents'
            }
        }
        
        self.background_patterns = {
            'none': 'No Pattern',
            'dots': 'Dot Matrix',
            'lines': 'Circuit Lines',
            'hexagon': 'Hexagonal Grid',
            'waves': 'Flowing Waves',
            'stars': 'Starfield',
            'particles': 'Floating Particles'
        }
        
        self.init_theme_tables()
    
    def init_theme_tables(self):
        """Initialize theme-related database tables"""
        conn = self.db_manager.get_direct_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # User theme preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_theme_preferences (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    theme_name VARCHAR(50) NOT NULL DEFAULT 'futuristic',
                    background_pattern VARCHAR(50) DEFAULT 'none',
                    custom_background_url TEXT,
                    custom_avatar BYTEA,
                    profile_border_style VARCHAR(100),
                    animation_enabled BOOLEAN DEFAULT TRUE,
                    custom_css TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id)
                )
            """)
            
            # Theme showcase gallery
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS theme_showcase (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                    theme_name VARCHAR(50) NOT NULL,
                    showcase_image BYTEA,
                    description TEXT,
                    likes_count INTEGER DEFAULT 0,
                    is_featured BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User profile customizations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profile_customizations (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    banner_image BYTEA,
                    status_message VARCHAR(200),
                    favorite_characters JSONB DEFAULT '[]',
                    profile_visibility VARCHAR(20) DEFAULT 'public' CHECK (profile_visibility IN ('public', 'friends', 'private')),
                    show_achievements BOOLEAN DEFAULT TRUE,
                    show_trading_stats BOOLEAN DEFAULT TRUE,
                    show_portfolio BOOLEAN DEFAULT TRUE,
                    custom_title VARCHAR(50),
                    title_color VARCHAR(7) DEFAULT '#ffffff',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id)
                )
            """)
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Theme table initialization error: {e}")
            conn.rollback()
            return False
        finally:
            self.db_manager.return_connection(conn)
    
    def get_user_theme(self, user_id):
        """Get user's current theme preferences"""
        query = """
        SELECT theme_name, background_pattern, custom_background_url, 
               custom_avatar, profile_border_style, animation_enabled, custom_css
        FROM user_theme_preferences 
        WHERE user_id = %s
        """
        result = self.db_manager.execute_query(query, (user_id,))
        
        if not result.empty:
            return result.iloc[0].to_dict()
        else:
            # Return default theme
            return {
                'theme_name': 'futuristic',
                'background_pattern': 'none',
                'custom_background_url': None,
                'custom_avatar': None,
                'profile_border_style': None,
                'animation_enabled': True,
                'custom_css': None
            }
    
    def save_user_theme(self, user_id, theme_name, background_pattern='none', 
                       custom_background_url=None, custom_avatar=None,
                       profile_border_style=None, animation_enabled=True, custom_css=None):
        """Save user theme preferences"""
        query = """
        INSERT INTO user_theme_preferences 
        (user_id, theme_name, background_pattern, custom_background_url, 
         custom_avatar, profile_border_style, animation_enabled, custom_css, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        ON CONFLICT (user_id) 
        DO UPDATE SET 
            theme_name = EXCLUDED.theme_name,
            background_pattern = EXCLUDED.background_pattern,
            custom_background_url = EXCLUDED.custom_background_url,
            custom_avatar = EXCLUDED.custom_avatar,
            profile_border_style = EXCLUDED.profile_border_style,
            animation_enabled = EXCLUDED.animation_enabled,
            custom_css = EXCLUDED.custom_css,
            updated_at = NOW()
        """
        
        return self.db_manager.execute_query(query, (
            user_id, theme_name, background_pattern, custom_background_url,
            custom_avatar, profile_border_style, animation_enabled, custom_css
        ), fetch=False)
    
    def get_profile_customization(self, user_id):
        """Get user's profile customization settings"""
        query = """
        SELECT banner_image, status_message, favorite_characters, profile_visibility,
               show_achievements, show_trading_stats, show_portfolio, custom_title, title_color
        FROM profile_customizations 
        WHERE user_id = %s
        """
        result = self.db_manager.execute_query(query, (user_id,))
        
        if not result.empty:
            return result.iloc[0].to_dict()
        else:
            return {
                'banner_image': None,
                'status_message': '',
                'favorite_characters': [],
                'profile_visibility': 'public',
                'show_achievements': True,
                'show_trading_stats': True,
                'show_portfolio': True,
                'custom_title': '',
                'title_color': '#ffffff'
            }
    
    def save_profile_customization(self, user_id, **kwargs):
        """Save user profile customization settings"""
        query = """
        INSERT INTO profile_customizations 
        (user_id, banner_image, status_message, favorite_characters, profile_visibility,
         show_achievements, show_trading_stats, show_portfolio, custom_title, title_color, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        ON CONFLICT (user_id) 
        DO UPDATE SET 
            banner_image = EXCLUDED.banner_image,
            status_message = EXCLUDED.status_message,
            favorite_characters = EXCLUDED.favorite_characters,
            profile_visibility = EXCLUDED.profile_visibility,
            show_achievements = EXCLUDED.show_achievements,
            show_trading_stats = EXCLUDED.show_trading_stats,
            show_portfolio = EXCLUDED.show_portfolio,
            custom_title = EXCLUDED.custom_title,
            title_color = EXCLUDED.title_color,
            updated_at = NOW()
        """
        
        return self.db_manager.execute_query(query, (
            user_id,
            kwargs.get('banner_image'),
            kwargs.get('status_message', ''),
            json.dumps(kwargs.get('favorite_characters', [])),
            kwargs.get('profile_visibility', 'public'),
            kwargs.get('show_achievements', True),
            kwargs.get('show_trading_stats', True),
            kwargs.get('show_portfolio', True),
            kwargs.get('custom_title', ''),
            kwargs.get('title_color', '#ffffff')
        ), fetch=False)
    
    def apply_theme_css(self, theme_name, background_pattern='none', custom_css=None):
        """Generate and apply enhanced theme CSS with modern design"""
        if theme_name not in self.themes:
            theme_name = 'futuristic'
        
        theme = self.themes[theme_name]
        
        # Enhanced theme CSS with modern design patterns
        css = f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500;600&display=swap');
        
        /* Theme: {theme['name']} - Enhanced Design System */
        :root {{
            --primary-color: {theme['primary_color']};
            --secondary-color: {theme['secondary_color']};
            --background-color: {theme['background_color']};
            --text-color: {theme['text_color']};
            --accent-color: {theme['accent_color']};
            --glass-bg: rgba(255, 255, 255, 0.08);
            --glass-border: rgba(255, 255, 255, 0.12);
            --shadow-light: 0 4px 16px rgba(0, 0, 0, 0.1);
            --shadow-medium: 0 8px 32px rgba(0, 0, 0, 0.15);
            --shadow-heavy: 0 16px 64px rgba(0, 0, 0, 0.2);
        }}
        
        /* Global App Styling */
        .stApp {{
            background: {theme['gradient']};
            background-attachment: fixed;
            color: {theme['text_color']};
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            min-height: 100vh;
        }}
        
        /* Enhanced Background with Floating Elements */
        .stApp::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                radial-gradient(circle at 20% 80%, {theme['primary_color']}22 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, {theme['secondary_color']}15 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, {theme['accent_color']}10 0%, transparent 50%);
            background-size: 100% 100%;
            pointer-events: none;
            z-index: -1;
            animation: floating-orbs 20s ease-in-out infinite;
        }}
        
        @keyframes floating-orbs {{
            0%, 100% {{ transform: translate(0, 0) scale(1); }}
            25% {{ transform: translate(10px, -10px) scale(1.1); }}
            50% {{ transform: translate(-5px, 5px) scale(0.9); }}
            75% {{ transform: translate(-10px, -5px) scale(1.05); }}
        }}
        
        /* Typography Enhancements */
        h1, h2, h3, h4, h5, h6 {{
            font-weight: 700;
            letter-spacing: -0.025em;
            line-height: 1.2;
        }}
        
        .main-header {{
            text-align: center;
            background: linear-gradient(135deg, {theme['primary_color']}, {theme['secondary_color']}, {theme['accent_color']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: clamp(2rem, 5vw, 4rem);
            font-weight: 800;
            margin-bottom: 3rem;
            position: relative;
            animation: glow-pulse 3s ease-in-out infinite;
        }}
        
        .main-header::after {{
            content: '';
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 4px;
            background: linear-gradient(90deg, transparent, {theme['primary_color']}, transparent);
            margin-top: 1rem;
            border-radius: 2px;
        }}
        
        @keyframes glow-pulse {{
            0%, 100% {{ 
                filter: brightness(1) drop-shadow(0 0 20px {theme['primary_color']}66); 
                transform: scale(1);
            }}
            50% {{ 
                filter: brightness(1.2) drop-shadow(0 0 30px {theme['primary_color']}99); 
                transform: scale(1.02);
            }}
        }}
        
        /* Advanced Glass Morphism Cards */
        .glass-card, .profile-card, .tier-card {{
            background: linear-gradient(135deg, var(--glass-bg), rgba(255, 255, 255, 0.04));
            backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            border-radius: 24px;
            padding: 2rem;
            box-shadow: 
                var(--shadow-medium),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}
        
        .glass-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
            transition: left 0.7s ease;
        }}
        
        .glass-card:hover {{
            transform: translateY(-6px) scale(1.02);
            box-shadow: 
                var(--shadow-heavy),
                inset 0 1px 0 rgba(255, 255, 255, 0.15);
            border-color: {theme['primary_color']}66;
        }}
        
        .glass-card:hover::before {{
            left: 100%;
        }}
        
        /* Enhanced Button System */
        .stButton > button {{
            background: linear-gradient(135deg, {theme['primary_color']}, {theme['secondary_color']});
            color: white;
            border: none;
            border-radius: 16px;
            padding: 1rem 2rem;
            font-weight: 600;
            font-size: 0.95rem;
            font-family: 'Inter', sans-serif;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 
                0 4px 16px {theme['primary_color']}44,
                0 2px 8px rgba(0, 0, 0, 0.1);
            position: relative;
            overflow: hidden;
            text-transform: none;
            letter-spacing: 0.025em;
        }}
        
        .stButton > button::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.25), transparent);
            transition: left 0.5s ease;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-3px);
            box-shadow: 
                0 8px 24px {theme['primary_color']}66,
                0 4px 16px rgba(0, 0, 0, 0.15);
            filter: brightness(1.1);
        }}
        
        .stButton > button:hover::before {{
            left: 100%;
        }}
        
        .stButton > button:active {{
            transform: translateY(-1px);
            transition: transform 0.1s ease;
        }}
        
        /* Enhanced Form Elements */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div,
        .stNumberInput > div > div > input {{
            background: rgba(255, 255, 255, 0.08) !important;
            border: 2px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 12px !important;
            color: {theme['text_color']} !important;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.95rem !important;
        }}
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus,
        .stSelectbox > div > div:focus,
        .stNumberInput > div > div > input:focus {{
            border-color: {theme['primary_color']} !important;
            box-shadow: 0 0 0 3px {theme['primary_color']}33 !important;
            background: rgba(255, 255, 255, 0.12) !important;
            outline: none !important;
        }}
        
        /* Enhanced Metrics */
        [data-testid="metric-container"] {{
            background: linear-gradient(135deg, var(--glass-bg), rgba(255, 255, 255, 0.04));
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 1.5rem;
            backdrop-filter: blur(15px);
            transition: all 0.3s ease;
            box-shadow: var(--shadow-light);
            position: relative;
            overflow: hidden;
        }}
        
        [data-testid="metric-container"]::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, {theme['primary_color']}, {theme['secondary_color']});
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        
        [data-testid="metric-container"]:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-medium);
            border-color: {theme['primary_color']}44;
        }}
        
        [data-testid="metric-container"]:hover::before {{
            opacity: 1;
        }}
        
        /* Enhanced Sidebar */
        .css-1d391kg {{
            background: linear-gradient(180deg, 
                rgba(0, 0, 0, 0.85) 0%, 
                rgba(0, 0, 0, 0.75) 100%) !important;
            backdrop-filter: blur(20px) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
        }}
        
        /* Enhanced Tables */
        .stDataFrame {{
            border-radius: 16px;
            overflow: hidden;
            box-shadow: var(--shadow-medium);
            border: 1px solid var(--glass-border);
        }}
        
        .stDataFrame table {{
            background: var(--glass-bg);
            backdrop-filter: blur(10px);
        }}
        
        /* Enhanced Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background: rgba(255, 255, 255, 0.06);
            border-radius: 16px;
            padding: 6px;
            backdrop-filter: blur(10px);
            border: 1px solid var(--glass-border);
        }}
        
        .stTabs [data-baseweb="tab"] {{
            border-radius: 12px;
            padding: 12px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
            border: none;
            font-family: 'Inter', sans-serif;
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            background: rgba(255, 255, 255, 0.1);
            transform: translateY(-1px);
        }}
        
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            background: linear-gradient(135deg, {theme['primary_color']}, {theme['secondary_color']});
            color: white;
            box-shadow: 0 4px 12px {theme['primary_color']}44;
        }}
        
        /* Profile Enhancements */
        .profile-avatar {{
            width: 120px;
            height: 120px;
            border-radius: 50%;
            border: 4px solid {theme['primary_color']};
            object-fit: cover;
            margin-top: -60px;
            margin-left: 20px;
            background: var(--glass-bg);
            box-shadow: var(--shadow-medium);
            transition: all 0.3s ease;
            position: relative;
        }}
        
        .profile-avatar::after {{
            content: '';
            position: absolute;
            inset: -4px;
            border-radius: 50%;
            background: linear-gradient(135deg, {theme['primary_color']}, {theme['secondary_color']});
            z-index: -1;
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        
        .profile-avatar:hover {{
            transform: scale(1.05);
            box-shadow: var(--shadow-heavy);
        }}
        
        .profile-avatar:hover::after {{
            opacity: 0.8;
        }}
        
        .profile-banner {{
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 24px 24px 0 0;
        }}
        
        .custom-title {{
            font-weight: 600;
            font-size: 1.1em;
            margin: 10px 0;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            background: linear-gradient(135deg, {theme['primary_color']}, {theme['secondary_color']});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .status-message {{
            font-style: italic;
            opacity: 0.8;
            margin-bottom: 15px;
            font-size: 0.9em;
            font-weight: 300;
        }}
        
        .favorite-character {{
            display: inline-block;
            background: var(--glass-bg);
            border-radius: 20px;
            padding: 8px 16px;
            margin: 4px;
            border: 1px solid {theme['primary_color']}44;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            font-weight: 500;
            font-size: 0.9em;
        }}
        
        .favorite-character:hover {{
            transform: translateY(-2px);
            background: {theme['primary_color']}22;
            border-color: {theme['primary_color']};
            box-shadow: 0 4px 12px {theme['primary_color']}33;
        }}
        
        /* Achievement System */
        .achievement-badge {{
            background: linear-gradient(135deg, {theme['primary_color']}, {theme['secondary_color']});
            border-radius: 24px;
            padding: 8px 20px;
            margin: 6px;
            display: inline-block;
            color: white;
            font-weight: 600;
            box-shadow: 0 4px 16px {theme['primary_color']}44;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            font-size: 0.9em;
        }}
        
        .achievement-badge::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
            transition: left 0.6s ease;
        }}
        
        .achievement-badge:hover {{
            transform: translateY(-2px) scale(1.05);
            box-shadow: 0 8px 24px {theme['primary_color']}66;
        }}
        
        .achievement-badge:hover::before {{
            left: 100%;
        }}
        """
        
        # Add enhanced background patterns
        if background_pattern == 'dots':
            css += f"""
            .stApp::after {{
                content: '';
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-image: radial-gradient({theme['primary_color']}88 1px, transparent 1px);
                background-size: 30px 30px;
                opacity: 0.3;
                z-index: -1;
                animation: dots-float 10s linear infinite;
            }}
            
            @keyframes dots-float {{
                0% {{ transform: translateY(0px); }}
                100% {{ transform: translateY(-30px); }}
            }}
            """
        elif background_pattern == 'lines':
            css += f"""
            .stApp::after {{
                content: '';
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-image: 
                    linear-gradient(90deg, {theme['primary_color']}22 1px, transparent 1px),
                    linear-gradient(0deg, {theme['primary_color']}22 1px, transparent 1px);
                background-size: 40px 40px;
                opacity: 0.4;
                z-index: -1;
                animation: grid-shift 15s linear infinite;
            }}
            
            @keyframes grid-shift {{
                0% {{ transform: translate(0, 0); }}
                100% {{ transform: translate(40px, 40px); }}
            }}
            """
        elif background_pattern == 'hexagon':
            css += f"""
            .stApp::after {{
                content: '';
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='{theme['primary_color'].replace('#', '%23')}' fill-opacity='0.2'%3E%3Cpath d='m36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
                z-index: -1;
                opacity: 0.6;
                animation: hexagon-pulse 8s ease-in-out infinite;
            }}
            
            @keyframes hexagon-pulse {{
                0%, 100% {{ opacity: 0.3; }}
                50% {{ opacity: 0.6; }}
            }}
            """
        
        # Add responsive design improvements
        css += f"""
        
        /* Enhanced Responsive Design */
        @media (max-width: 768px) {{
            .main-header {{
                font-size: 2.5rem;
                margin-bottom: 2rem;
            }}
            
            .glass-card, .profile-card, .tier-card {{
                padding: 1.5rem;
                margin: 1rem 0;
                border-radius: 20px;
            }}
            
            .stButton > button {{
                width: 100%;
                margin-bottom: 0.75rem;
                padding: 1rem 1.5rem;
                font-size: 1rem;
            }}
            
            .profile-avatar {{
                width: 80px;
                height: 80px;
                margin-top: -40px;
            }}
            
            [data-testid="metric-container"] {{
                padding: 1rem;
                margin: 0.5rem 0;
            }}
        }}
        
        @media (max-width: 480px) {{
            .main-header {{
                font-size: 2rem;
            }}
            
            .glass-card, .profile-card, .tier-card {{
                padding: 1rem;
                margin: 0.75rem 0;
            }}
        }}
        
        /* Loading States */
        @keyframes shimmer {{
            0% {{ transform: translateX(-100%); }}
            100% {{ transform: translateX(100%); }}
        }}
        
        .loading-shimmer {{
            position: relative;
            overflow: hidden;
        }}
        
        .loading-shimmer::after {{
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            bottom: 0;
            left: 0;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
            animation: shimmer 2s infinite;
        }}
        
        /* Scrollbar Styling */
        ::-webkit-scrollbar {{
            width: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {theme['primary_color']}88;
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {theme['primary_color']};
        }}
        """
        
        # Add custom CSS if provided
        if custom_css:
            css += f"\n/* Custom User CSS */\n{custom_css}\n"
        
        css += "</style>"
        
        return css
    
    def get_theme_preview(self, theme_name):
        """Generate theme preview"""
        if theme_name not in self.themes:
            return None
        
        theme = self.themes[theme_name]
        
        preview_html = f"""
        <div style="
            background: {theme['gradient']};
            color: {theme['text_color']};
            padding: 20px;
            border-radius: 15px;
            border: {theme['border_style']};
            box-shadow: {theme['shadow']};
            text-align: center;
            margin: 10px 0;
        ">
            <h3 style="margin: 0; color: {theme['primary_color']};">{theme['name']}</h3>
            <p style="margin: 10px 0; font-size: 14px; opacity: 0.8;">{theme['description']}</p>
            <div style="
                background: linear-gradient(45deg, {theme['primary_color']}, {theme['secondary_color']});
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                display: inline-block;
                margin: 5px;
                font-size: 12px;
            ">Sample Badge</div>
        </div>
        """
        
        return preview_html
    
    def process_uploaded_image(self, uploaded_file, max_size=(800, 600)):
        """Process uploaded image for profile customization"""
        if uploaded_file is not None:
            try:
                image = Image.open(uploaded_file)
                
                # Resize if necessary
                if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                    image.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Convert to RGB if necessary
                if image.mode in ('RGBA', 'P'):
                    image = image.convert('RGB')
                
                # Convert to bytes
                img_buffer = io.BytesIO()
                image.save(img_buffer, format='JPEG', quality=85)
                img_bytes = img_buffer.getvalue()
                
                return img_bytes
            except Exception as e:
                st.error(f"Error processing image: {e}")
                return None
        return None
    
    def image_to_base64(self, img_bytes):
        """Convert image bytes to base64 string"""
        if img_bytes:
            return base64.b64encode(img_bytes).decode()
        return None
    
    def get_featured_themes(self):
        """Get featured theme showcases"""
        query = """
        SELECT ts.*, u.username, u.display_name 
        FROM theme_showcase ts
        JOIN users u ON ts.user_id = u.user_id
        WHERE ts.is_featured = TRUE
        ORDER BY ts.likes_count DESC, ts.created_at DESC
        LIMIT 10
        """
        return self.db_manager.execute_query(query)