"""
Advanced Settings Management System
Handles user preferences, configuration persistence, and settings validation
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime


class SettingsManager:
    """Comprehensive settings management with database persistence"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.default_settings = self._get_default_settings()
        self.init_settings_tables()
    
    def init_settings_tables(self):
        """Initialize settings storage tables"""
        try:
            # User settings table
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    setting_id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    category VARCHAR(50) NOT NULL,
                    setting_key VARCHAR(100) NOT NULL,
                    setting_value TEXT NOT NULL,
                    data_type VARCHAR(20) DEFAULT 'string',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, category, setting_key)
                )
            """, fetch=False)
            
            # Settings categories table
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS settings_categories (
                    category_id SERIAL PRIMARY KEY,
                    category_name VARCHAR(50) UNIQUE NOT NULL,
                    display_name VARCHAR(100) NOT NULL,
                    description TEXT,
                    icon VARCHAR(20),
                    sort_order INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """, fetch=False)
            
            # Settings templates for different user types
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS settings_templates (
                    template_id SERIAL PRIMARY KEY,
                    template_name VARCHAR(50) UNIQUE NOT NULL,
                    display_name VARCHAR(100) NOT NULL,
                    description TEXT,
                    user_type VARCHAR(20) DEFAULT 'regular',
                    settings_json TEXT NOT NULL,
                    is_default BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """, fetch=False)
            
            # Settings audit log
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS settings_audit (
                    audit_id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(user_id),
                    category VARCHAR(50) NOT NULL,
                    setting_key VARCHAR(100) NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    change_reason VARCHAR(200),
                    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    ip_address VARCHAR(45)
                )
            """, fetch=False)
            
            self._insert_default_categories()
            self._insert_default_templates()
            
        except Exception as e:
            print(f"Settings table initialization error: {str(e)}")
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Define comprehensive default settings"""
        return {
            'appearance': {
                'theme': 'cyberpunk',
                'font_size': 'Medium',
                'animations_enabled': True,
                'particles_enabled': True,
                'glassmorphism': True,
                'accent_color': '#667eea',
                'sidebar_collapsed': False,
                'compact_mode': False,
                'high_contrast': False,
                'dark_mode': True
            },
            'notifications': {
                'notifications_enabled': True,
                'trade_success': True,
                'trade_failure': True,
                'price_alerts': False,
                'achievement_unlock': True,
                'milestone_reached': True,
                'maintenance_alerts': True,
                'security_alerts': True,
                'in_app_notifications': True,
                'email_notifications': False,
                'notification_frequency': 'Real-time',
                'dnd_enabled': False,
                'dnd_start_time': '22:00',
                'dnd_end_time': '08:00'
            },
            'trading': {
                'default_trade_amount': 10,
                'auto_confirm_trades': False,
                'auto_confirm_threshold': 5,
                'enable_stop_loss': False,
                'stop_loss_percentage': 10,
                'enable_take_profit': False,
                'take_profit_percentage': 20,
                'track_performance': True,
                'detailed_analytics': False,
                'export_data': True,
                'risk_warnings': True,
                'confirmation_dialogs': True
            },
            'privacy': {
                'analytics_tracking': True,
                'performance_monitoring': True,
                'crash_reporting': True,
                'hide_online_status': False,
                'private_trading_history': False,
                'block_friend_requests': False,
                'profile_visibility': 'Public',
                'show_achievements': True,
                'show_trading_stats': True,
                'data_retention_days': 365
            },
            'performance': {
                'reduce_animations': False,
                'limit_chart_data': False,
                'max_data_points': 200,
                'lazy_loading': True,
                'cache_duration': '15 minutes',
                'auto_clear_cache': False,
                'compress_images': True,
                'low_bandwidth_mode': False,
                'show_performance_metrics': False
            },
            'accessibility': {
                'screen_reader_support': False,
                'keyboard_navigation': True,
                'focus_indicators': True,
                'reduced_motion': False,
                'large_text': False,
                'color_blind_mode': 'none',
                'voice_commands': False
            }
        }
    
    def _insert_default_categories(self):
        """Insert default settings categories"""
        categories = [
            ('appearance', 'Appearance', 'Theme and visual customization', '🎨', 1),
            ('notifications', 'Notifications', 'Alert and notification preferences', '🔔', 2),
            ('trading', 'Trading', 'Trading behavior and risk management', '📊', 3),
            ('privacy', 'Privacy', 'Data privacy and security settings', '🔒', 4),
            ('performance', 'Performance', 'Optimization and performance tuning', '⚡', 5),
            ('accessibility', 'Accessibility', 'Accessibility and user assistance', '♿', 6)
        ]
        
        for category, display_name, description, icon, sort_order in categories:
            try:
                self.db.execute_query("""
                    INSERT INTO settings_categories (category_name, display_name, description, icon, sort_order)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (category_name) DO NOTHING
                """, (category, display_name, description, icon, sort_order), fetch=False)
            except Exception:
                pass
    
    def _insert_default_templates(self):
        """Insert default settings templates"""
        templates = [
            ('minimal', 'Minimal Setup', 'Basic settings for new users', 'regular'),
            ('performance', 'Performance Optimized', 'Settings optimized for speed', 'regular'),
            ('accessibility', 'Accessibility Enhanced', 'Enhanced accessibility features', 'regular'),
            ('advanced', 'Advanced User', 'Full feature set enabled', 'premium')
        ]
        
        for template_name, display_name, description, user_type in templates:
            settings_json = json.dumps(self._get_template_settings(template_name))
            try:
                self.db.execute_query("""
                    INSERT INTO settings_templates (template_name, display_name, description, user_type, settings_json)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (template_name) DO NOTHING
                """, (template_name, display_name, description, user_type, settings_json), fetch=False)
            except Exception:
                pass
    
    def _get_template_settings(self, template_name: str) -> Dict[str, Any]:
        """Get settings for specific template"""
        base_settings = self.default_settings.copy()
        
        if template_name == 'minimal':
            base_settings['appearance']['animations_enabled'] = False
            base_settings['appearance']['particles_enabled'] = False
            base_settings['notifications']['email_notifications'] = False
            base_settings['performance']['reduce_animations'] = True
            
        elif template_name == 'performance':
            base_settings['appearance']['animations_enabled'] = False
            base_settings['appearance']['particles_enabled'] = False
            base_settings['performance']['reduce_animations'] = True
            base_settings['performance']['limit_chart_data'] = True
            base_settings['performance']['compress_images'] = True
            
        elif template_name == 'accessibility':
            base_settings['accessibility']['screen_reader_support'] = True
            base_settings['accessibility']['large_text'] = True
            base_settings['accessibility']['reduced_motion'] = True
            base_settings['appearance']['high_contrast'] = True
            
        elif template_name == 'advanced':
            base_settings['trading']['detailed_analytics'] = True
            base_settings['notifications']['email_notifications'] = True
            base_settings['performance']['show_performance_metrics'] = True
        
        return base_settings
    
    def get_user_settings(self, user_id: int) -> Dict[str, Any]:
        """Get complete user settings with defaults for missing values"""
        try:
            result = self.db.execute_query("""
                SELECT category, setting_key, setting_value, data_type
                FROM user_settings
                WHERE user_id = %s
            """, (user_id,))
            
            # Handle DataFrame result properly
            if result is not None and hasattr(result, 'empty'):
                if result.empty:
                    result = None
                else:
                    result = result.values.tolist()
            
            # Start with defaults
            user_settings = self.default_settings.copy()
            
            # Override with user's saved settings
            if result and len(result) > 0:
                for row in result:
                    category = row[0]
                    key = row[1]
                    value = row[2]
                    data_type = row[3]
                    
                    # Convert value based on data type
                    converted_value = self._convert_setting_value(value, data_type)
                    
                    if category in user_settings:
                        user_settings[category][key] = converted_value
            
            return user_settings
            
        except Exception as e:
            print(f"Error getting user settings: {str(e)}")
            return self.default_settings
    
    def save_user_setting(self, user_id: int, category: str, key: str, value: Any, change_reason: str = None) -> bool:
        """Save individual user setting with audit trail"""
        try:
            # Get old value for audit
            old_value = self.get_user_setting(user_id, category, key)
            
            # Determine data type
            data_type = self._get_data_type(value)
            
            # Convert value to string for storage
            str_value = self._convert_to_string(value)
            
            # Save setting
            self.db.execute_query("""
                INSERT INTO user_settings (user_id, category, setting_key, setting_value, data_type, updated_at)
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id, category, setting_key)
                DO UPDATE SET 
                    setting_value = EXCLUDED.setting_value,
                    data_type = EXCLUDED.data_type,
                    updated_at = CURRENT_TIMESTAMP
            """, (user_id, category, key, str_value, data_type), fetch=False)
            
            # Add audit entry
            self._log_setting_change(user_id, category, key, old_value, value, change_reason)
            
            return True
            
        except Exception as e:
            print(f"Error saving user setting: {str(e)}")
            return False
    
    def save_user_settings_bulk(self, user_id: int, settings: Dict[str, Any]) -> bool:
        """Save multiple settings at once"""
        try:
            for category, category_settings in settings.items():
                for key, value in category_settings.items():
                    self.save_user_setting(user_id, category, key, value, "Bulk update")
            return True
        except Exception as e:
            print(f"Error bulk saving settings: {str(e)}")
            return False
    
    def get_user_setting(self, user_id: int, category: str, key: str) -> Any:
        """Get specific user setting with fallback to default"""
        try:
            result = self.db.execute_query("""
                SELECT setting_value, data_type
                FROM user_settings
                WHERE user_id = %s AND category = %s AND setting_key = %s
            """, (user_id, category, key))
            
            if result and len(result) > 0:
                value = result[0][0]
                data_type = result[0][1]
                return self._convert_setting_value(value, data_type)
            
            # Return default if not found
            if category in self.default_settings and key in self.default_settings[category]:
                return self.default_settings[category][key]
            
            return None
            
        except Exception as e:
            print(f"Error getting user setting: {str(e)}")
            return None
    
    def reset_user_settings(self, user_id: int, category: str = None) -> bool:
        """Reset user settings to defaults"""
        try:
            if category:
                # Reset specific category
                self.db.execute_query("""
                    DELETE FROM user_settings
                    WHERE user_id = %s AND category = %s
                """, (user_id, category), fetch=False)
                
                self._log_setting_change(user_id, category, '*', 'custom', 'default', f"Reset {category} category")
            else:
                # Reset all settings
                self.db.execute_query("""
                    DELETE FROM user_settings
                    WHERE user_id = %s
                """, (user_id,), fetch=False)
                
                self._log_setting_change(user_id, '*', '*', 'custom', 'default', "Reset all settings")
            
            return True
            
        except Exception as e:
            print(f"Error resetting user settings: {str(e)}")
            return False
    
    def apply_settings_template(self, user_id: int, template_name: str) -> bool:
        """Apply settings template to user"""
        try:
            result = self.db.execute_query("""
                SELECT settings_json FROM settings_templates
                WHERE template_name = %s
            """, (template_name,))
            
            if result and len(result) > 0:
                template_settings = json.loads(result[0][0])
                success = self.save_user_settings_bulk(user_id, template_settings)
                
                if success:
                    self._log_setting_change(user_id, '*', '*', 'custom', template_name, f"Applied {template_name} template")
                
                return success
            
            return False
            
        except Exception as e:
            print(f"Error applying settings template: {str(e)}")
            return False
    
    def export_user_settings(self, user_id: int) -> Dict[str, Any]:
        """Export user settings as JSON"""
        settings = self.get_user_settings(user_id)
        return {
            'export_timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'settings': settings,
            'version': '1.0'
        }
    
    def import_user_settings(self, user_id: int, settings_data: Dict[str, Any]) -> bool:
        """Import user settings from JSON"""
        try:
            if 'settings' in settings_data:
                return self.save_user_settings_bulk(user_id, settings_data['settings'])
            return False
        except Exception as e:
            print(f"Error importing settings: {str(e)}")
            return False
    
    def get_settings_categories(self) -> List[Dict[str, Any]]:
        """Get available settings categories"""
        try:
            result = self.db.execute_query("""
                SELECT category_name, display_name, description, icon, sort_order
                FROM settings_categories
                WHERE is_active = TRUE
                ORDER BY sort_order
            """)
            
            if result:
                return [
                    {
                        'name': row[0],
                        'display_name': row[1],
                        'description': row[2],
                        'icon': row[3],
                        'sort_order': row[4]
                    }
                    for row in result
                ]
            return []
            
        except Exception as e:
            print(f"Error getting settings categories: {str(e)}")
            return []
    
    def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get available settings templates"""
        try:
            result = self.db.execute_query("""
                SELECT template_name, display_name, description, user_type
                FROM settings_templates
                ORDER BY template_name
            """)
            
            if result:
                return [
                    {
                        'name': row[0],
                        'display_name': row[1],
                        'description': row[2],
                        'user_type': row[3]
                    }
                    for row in result
                ]
            return []
            
        except Exception as e:
            print(f"Error getting templates: {str(e)}")
            return []
    
    def _convert_setting_value(self, value: str, data_type: str) -> Any:
        """Convert string value to appropriate data type"""
        if data_type == 'boolean':
            return value.lower() in ('true', '1', 'yes', 'on')
        elif data_type == 'integer':
            return int(value)
        elif data_type == 'float':
            return float(value)
        elif data_type == 'json':
            return json.loads(value)
        else:
            return value
    
    def _convert_to_string(self, value: Any) -> str:
        """Convert value to string for storage"""
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        elif isinstance(value, bool):
            return str(value).lower()
        else:
            return str(value)
    
    def _get_data_type(self, value: Any) -> str:
        """Determine data type of value"""
        if isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, int):
            return 'integer'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, (dict, list)):
            return 'json'
        else:
            return 'string'
    
    def _log_setting_change(self, user_id: int, category: str, key: str, old_value: Any, new_value: Any, reason: str = None):
        """Log setting change for audit trail"""
        try:
            self.db.execute_query("""
                INSERT INTO settings_audit (user_id, category, setting_key, old_value, new_value, change_reason)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, category, key, str(old_value), str(new_value), reason), fetch=False)
        except Exception:
            pass  # Don't fail if audit logging fails
    
    def get_settings_audit_log(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get settings change audit log"""
        try:
            result = self.db.execute_query("""
                SELECT category, setting_key, old_value, new_value, change_reason, changed_at
                FROM settings_audit
                WHERE user_id = %s AND changed_at >= CURRENT_TIMESTAMP - INTERVAL '%s days'
                ORDER BY changed_at DESC
                LIMIT 100
            """, (user_id, days))
            
            if result:
                return [
                    {
                        'category': row[0],
                        'key': row[1],
                        'old_value': row[2],
                        'new_value': row[3],
                        'reason': row[4],
                        'timestamp': row[5]
                    }
                    for row in result
                ]
            return []
            
        except Exception as e:
            print(f"Error getting audit log: {str(e)}")
            return []