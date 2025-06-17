import streamlit as st
import json
import pandas as pd
from typing import Dict, List, Any, Optional
from database import DatabaseManager
import logging

class DashboardCustomizationManager:
    """Manage personalized dashboard customization for users"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
        self.init_customization_tables()
        
        # Default dashboard configuration
        self.default_config = {
            "layout": "grid",
            "widgets": {
                "balance": {"enabled": True, "position": 0, "size": "medium"},
                "portfolio_value": {"enabled": True, "position": 1, "size": "medium"},
                "recent_trades": {"enabled": True, "position": 2, "size": "large"},
                "market_trends": {"enabled": True, "position": 3, "size": "large"},
                "achievements": {"enabled": True, "position": 4, "size": "small"},
                "notifications": {"enabled": True, "position": 5, "size": "small"},
                "quick_stats": {"enabled": True, "position": 6, "size": "medium"},
                "top_characters": {"enabled": True, "position": 7, "size": "medium"}
            },
            "theme_preferences": {
                "primary_color": "#667eea",
                "secondary_color": "#764ba2",
                "background_style": "gradient",
                "card_transparency": 0.1,
                "animation_speed": "normal"
            },
            "display_preferences": {
                "show_welcome_message": True,
                "show_tips": True,
                "compact_mode": False,
                "auto_refresh": True,
                "refresh_interval": 30
            }
        }
    
    def init_customization_tables(self):
        """Initialize dashboard customization tables"""
        try:
            # Dashboard configurations table
            create_config_table = """
                CREATE TABLE IF NOT EXISTS dashboard_configs (
                    config_id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                    config_name VARCHAR(100) DEFAULT 'Default',
                    layout_type VARCHAR(20) DEFAULT 'grid',
                    widget_config JSONB DEFAULT '{}',
                    theme_config JSONB DEFAULT '{}',
                    display_config JSONB DEFAULT '{}',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, config_name)
                )
            """
            
            # User widget preferences
            create_widgets_table = """
                CREATE TABLE IF NOT EXISTS user_widgets (
                    widget_id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                    widget_type VARCHAR(50) NOT NULL,
                    widget_config JSONB DEFAULT '{}',
                    position INTEGER DEFAULT 0,
                    size VARCHAR(20) DEFAULT 'medium',
                    enabled BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, widget_type)
                )
            """
            
            # Dashboard templates
            create_templates_table = """
                CREATE TABLE IF NOT EXISTS dashboard_templates (
                    template_id SERIAL PRIMARY KEY,
                    template_name VARCHAR(100) UNIQUE NOT NULL,
                    description TEXT,
                    template_config JSONB NOT NULL,
                    is_public BOOLEAN DEFAULT FALSE,
                    created_by INTEGER REFERENCES users(user_id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    usage_count INTEGER DEFAULT 0
                )
            """
            
            self.db.execute_query(create_config_table, fetch=False)
            self.db.execute_query(create_widgets_table, fetch=False)
            self.db.execute_query(create_templates_table, fetch=False)
            
            # Create indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_dashboard_configs_user_id ON dashboard_configs(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_user_widgets_user_id ON user_widgets(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_dashboard_templates_public ON dashboard_templates(is_public)"
            ]
            
            for index_sql in indexes:
                self.db.execute_query(index_sql, fetch=False)
            
            # Insert default templates
            self._insert_default_templates()
            
            self.logger.info("Dashboard customization tables initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize customization tables: {e}")
    
    def _insert_default_templates(self):
        """Insert default dashboard templates"""
        default_templates = [
            {
                "name": "Trading Focus",
                "description": "Optimized for active traders with market data and trading tools",
                "config": {
                    "layout": "grid",
                    "widgets": {
                        "balance": {"enabled": True, "position": 0, "size": "small"},
                        "portfolio_value": {"enabled": True, "position": 1, "size": "small"},
                        "recent_trades": {"enabled": True, "position": 2, "size": "large"},
                        "market_trends": {"enabled": True, "position": 3, "size": "large"},
                        "top_characters": {"enabled": True, "position": 4, "size": "medium"},
                        "quick_stats": {"enabled": True, "position": 5, "size": "medium"},
                        "achievements": {"enabled": False, "position": 6, "size": "small"},
                        "notifications": {"enabled": True, "position": 7, "size": "small"}
                    }
                }
            },
            {
                "name": "Casual Player",
                "description": "Simple layout for casual gaming and achievement tracking",
                "config": {
                    "layout": "list",
                    "widgets": {
                        "balance": {"enabled": True, "position": 0, "size": "medium"},
                        "achievements": {"enabled": True, "position": 1, "size": "large"},
                        "portfolio_value": {"enabled": True, "position": 2, "size": "medium"},
                        "notifications": {"enabled": True, "position": 3, "size": "medium"},
                        "recent_trades": {"enabled": True, "position": 4, "size": "small"},
                        "market_trends": {"enabled": False, "position": 5, "size": "small"},
                        "top_characters": {"enabled": True, "position": 6, "size": "small"},
                        "quick_stats": {"enabled": False, "position": 7, "size": "small"}
                    }
                }
            },
            {
                "name": "Analytics Pro",
                "description": "Data-heavy layout with comprehensive analytics and charts",
                "config": {
                    "layout": "grid",
                    "widgets": {
                        "market_trends": {"enabled": True, "position": 0, "size": "large"},
                        "quick_stats": {"enabled": True, "position": 1, "size": "large"},
                        "portfolio_value": {"enabled": True, "position": 2, "size": "medium"},
                        "recent_trades": {"enabled": True, "position": 3, "size": "medium"},
                        "top_characters": {"enabled": True, "position": 4, "size": "medium"},
                        "balance": {"enabled": True, "position": 5, "size": "small"},
                        "achievements": {"enabled": True, "position": 6, "size": "small"},
                        "notifications": {"enabled": True, "position": 7, "size": "small"}
                    }
                }
            }
        ]
        
        try:
            check_query = "SELECT COUNT(*) as count FROM dashboard_templates"
            result = self.db.execute_query(check_query)
            
            if not result.empty and result.iloc[0]['count'] == 0:
                for template in default_templates:
                    insert_query = """
                        INSERT INTO dashboard_templates (template_name, description, template_config, is_public)
                        VALUES (%s, %s, %s, %s)
                    """
                    config_json = json.dumps(template["config"])
                    self.db.execute_query(
                        insert_query,
                        (template["name"], template["description"], config_json, True),
                        fetch=False
                    )
                
                self.logger.info("Default templates inserted")
                
        except Exception as e:
            self.logger.error(f"Failed to insert default templates: {e}")
    
    def get_user_dashboard_config(self, user_id: int) -> Dict[str, Any]:
        """Get user's current dashboard configuration"""
        try:
            query = """
                SELECT widget_config, theme_config, display_config, layout_type
                FROM dashboard_configs
                WHERE user_id = %s AND is_active = TRUE
                ORDER BY updated_at DESC
                LIMIT 1
            """
            result = self.db.execute_query(query, (user_id,))
            
            if result.empty:
                # Create default config for new user
                self.save_user_dashboard_config(user_id, self.default_config)
                return self.default_config
            
            config_row = result.iloc[0]
            return {
                "layout": config_row['layout_type'],
                "widgets": json.loads(config_row['widget_config'] or '{}'),
                "theme_preferences": json.loads(config_row['theme_config'] or '{}'),
                "display_preferences": json.loads(config_row['display_config'] or '{}')
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get user dashboard config: {e}")
            return self.default_config
    
    def save_user_dashboard_config(self, user_id: int, config: Dict[str, Any]) -> bool:
        """Save user's dashboard configuration"""
        try:
            # Check if config exists
            check_query = """
                SELECT config_id FROM dashboard_configs
                WHERE user_id = %s AND config_name = 'Default'
            """
            result = self.db.execute_query(check_query, (user_id,))
            
            widget_config = json.dumps(config.get("widgets", {}))
            theme_config = json.dumps(config.get("theme_preferences", {}))
            display_config = json.dumps(config.get("display_preferences", {}))
            layout_type = config.get("layout", "grid")
            
            if result.empty:
                # Insert new config
                insert_query = """
                    INSERT INTO dashboard_configs 
                    (user_id, config_name, layout_type, widget_config, theme_config, display_config)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                self.db.execute_query(
                    insert_query,
                    (user_id, 'Default', layout_type, widget_config, theme_config, display_config),
                    fetch=False
                )
            else:
                # Update existing config
                update_query = """
                    UPDATE dashboard_configs
                    SET layout_type = %s, widget_config = %s, theme_config = %s,
                        display_config = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s AND config_name = 'Default'
                """
                self.db.execute_query(
                    update_query,
                    (layout_type, widget_config, theme_config, display_config, user_id),
                    fetch=False
                )
            
            self.logger.info(f"Dashboard config saved for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save dashboard config: {e}")
            return False
    
    def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get available dashboard templates"""
        try:
            query = """
                SELECT template_id, template_name, description, template_config, usage_count
                FROM dashboard_templates
                WHERE is_public = TRUE
                ORDER BY usage_count DESC, template_name
            """
            result = self.db.execute_query(query)
            
            templates = []
            for _, row in result.iterrows():
                templates.append({
                    "id": row['template_id'],
                    "name": row['template_name'],
                    "description": row['description'],
                    "config": json.loads(row['template_config']),
                    "usage_count": row['usage_count']
                })
            
            return templates
            
        except Exception as e:
            self.logger.error(f"Failed to get templates: {e}")
            return []
    
    def apply_template(self, user_id: int, template_id: int) -> bool:
        """Apply a dashboard template to user's configuration"""
        try:
            # Get template config
            query = """
                SELECT template_config FROM dashboard_templates
                WHERE template_id = %s AND is_public = TRUE
            """
            result = self.db.execute_query(query, (template_id,))
            
            if result.empty:
                return False
            
            template_config = json.loads(result.iloc[0]['template_config'])
            
            # Get user's current config to preserve preferences
            current_config = self.get_user_dashboard_config(user_id)
            
            # Merge template with user preferences
            merged_config = {
                "layout": template_config.get("layout", "grid"),
                "widgets": template_config.get("widgets", {}),
                "theme_preferences": current_config.get("theme_preferences", {}),
                "display_preferences": current_config.get("display_preferences", {})
            }
            
            # Save merged config
            success = self.save_user_dashboard_config(user_id, merged_config)
            
            if success:
                # Increment template usage count
                update_usage = """
                    UPDATE dashboard_templates
                    SET usage_count = usage_count + 1
                    WHERE template_id = %s
                """
                self.db.execute_query(update_usage, (template_id,), fetch=False)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to apply template: {e}")
            return False
    
    def get_widget_data(self, user_id: int, widget_type: str) -> Dict[str, Any]:
        """Get data for a specific widget type"""
        try:
            if widget_type == "balance":
                return self._get_balance_data(user_id)
            elif widget_type == "portfolio_value":
                return self._get_portfolio_value_data(user_id)
            elif widget_type == "recent_trades":
                return self._get_recent_trades_data(user_id)
            elif widget_type == "market_trends":
                return self._get_market_trends_data()
            elif widget_type == "achievements":
                return self._get_achievements_data(user_id)
            elif widget_type == "notifications":
                return self._get_notifications_data(user_id)
            elif widget_type == "quick_stats":
                return self._get_quick_stats_data(user_id)
            elif widget_type == "top_characters":
                return self._get_top_characters_data()
            else:
                return {"error": "Unknown widget type"}
                
        except Exception as e:
            self.logger.error(f"Failed to get widget data for {widget_type}: {e}")
            return {"error": "Failed to load widget data"}
    
    def _get_balance_data(self, user_id: int) -> Dict[str, Any]:
        """Get user balance data"""
        try:
            query = "SELECT virtual_currency FROM users WHERE user_id = %s"
            result = self.db.execute_query(query, (user_id,))
            
            if result.empty:
                return {"balance": 0, "change": 0, "formatted": "$0.00"}
            
            balance = float(result.iloc[0]['virtual_currency'] or 0)
            return {
                "balance": balance,
                "formatted": f"${balance:,.2f}",
                "change": 0  # TODO: Calculate change from previous day
            }
        except Exception as e:
            self.logger.error(f"Failed to get balance data: {e}")
            return {"balance": 0, "change": 0, "formatted": "$0.00"}
    
    def _get_portfolio_value_data(self, user_id: int) -> Dict[str, Any]:
        """Get portfolio value data"""
        try:
            query = """
                SELECT SUM(p.quantity * c.value) as total_value
                FROM portfolios p
                JOIN characters c ON p.character_id = c.character_id
                WHERE p.user_id = %s AND p.quantity > 0
            """
            result = self.db.execute_query(query, (user_id,))
            
            total_value = 0
            if not result.empty and result.iloc[0]['total_value']:
                total_value = float(result.iloc[0]['total_value'])
            
            return {
                "value": total_value,
                "formatted": f"${total_value:,.2f}",
                "change_percent": 0  # TODO: Calculate percentage change
            }
        except Exception as e:
            self.logger.error(f"Failed to get portfolio value data: {e}")
            return {"value": 0, "formatted": "$0.00", "change_percent": 0}
    
    def _get_recent_trades_data(self, user_id: int) -> Dict[str, Any]:
        """Get recent trades data"""
        try:
            query = """
                SELECT t.trade_type, t.quantity, t.price_per_unit, t.timestamp,
                       c.name as character_name, c.tier
                FROM trades t
                JOIN characters c ON t.character_id = c.character_id
                WHERE t.user_id = %s
                ORDER BY t.timestamp DESC
                LIMIT 5
            """
            result = self.db.execute_query(query, (user_id,))
            
            trades = []
            if not result.empty:
                for _, row in result.iterrows():
                    trades.append({
                        "type": row['trade_type'],
                        "character": row['character_name'],
                        "tier": row['tier'],
                        "quantity": row['quantity'],
                        "price": float(row['price_per_unit']),
                        "total": float(row['quantity'] * row['price_per_unit']),
                        "timestamp": row['timestamp']
                    })
            
            return {"trades": trades}
        except Exception as e:
            self.logger.error(f"Failed to get recent trades data: {e}")
            return {"trades": []}
    
    def _get_market_trends_data(self) -> Dict[str, Any]:
        """Get market trends data"""
        try:
            query = """
                SELECT tier, AVG(value) as avg_value, COUNT(*) as count
                FROM characters
                WHERE is_active = TRUE
                GROUP BY tier
                ORDER BY avg_value DESC
            """
            result = self.db.execute_query(query)
            
            trends = []
            if not result.empty:
                for _, row in result.iterrows():
                    trends.append({
                        "tier": row['tier'],
                        "avg_value": float(row['avg_value']),
                        "count": int(row['count'])
                    })
            
            return {"trends": trends}
        except Exception as e:
            self.logger.error(f"Failed to get market trends data: {e}")
            return {"trends": []}
    
    def _get_achievements_data(self, user_id: int) -> Dict[str, Any]:
        """Get user achievements data"""
        try:
            query = """
                SELECT COUNT(*) as total_achievements
                FROM user_achievements
                WHERE user_id = %s
            """
            result = self.db.execute_query(query, (user_id,))
            
            total = 0
            if not result.empty:
                total = int(result.iloc[0]['total_achievements'] or 0)
            
            return {
                "total": total,
                "recent": []  # TODO: Get recent achievements
            }
        except Exception as e:
            self.logger.error(f"Failed to get achievements data: {e}")
            return {"total": 0, "recent": []}
    
    def _get_notifications_data(self, user_id: int) -> Dict[str, Any]:
        """Get user notifications data"""
        try:
            query = """
                SELECT COUNT(*) as unread_count
                FROM notifications
                WHERE user_id = %s AND is_read = FALSE
            """
            result = self.db.execute_query(query, (user_id,))
            
            unread = 0
            if not result.empty:
                unread = int(result.iloc[0]['unread_count'] or 0)
            
            return {"unread_count": unread}
        except Exception as e:
            self.logger.error(f"Failed to get notifications data: {e}")
            return {"unread_count": 0}
    
    def _get_quick_stats_data(self, user_id: int) -> Dict[str, Any]:
        """Get quick statistics data"""
        try:
            queries = {
                "total_trades": "SELECT COUNT(*) as count FROM trades WHERE user_id = %s",
                "characters_owned": "SELECT COUNT(*) as count FROM portfolios WHERE user_id = %s AND quantity > 0",
                "total_profit": "SELECT SUM(CASE WHEN trade_type = 'sell' THEN (price_per_unit * quantity) ELSE -(price_per_unit * quantity) END) as profit FROM trades WHERE user_id = %s"
            }
            
            stats = {}
            for stat_name, query in queries.items():
                try:
                    result = self.db.execute_query(query, (user_id,))
                    if not result.empty:
                        # Use column name instead of position to avoid pandas warning
                        col_name = result.columns[0]
                        value = result.iloc[0][col_name] or 0
                        stats[stat_name] = int(value) if stat_name != "total_profit" else float(value)
                    else:
                        stats[stat_name] = 0
                except Exception:
                    stats[stat_name] = 0
            
            return stats
        except Exception as e:
            self.logger.error(f"Failed to get quick stats data: {e}")
            return {"total_trades": 0, "characters_owned": 0, "total_profit": 0.0}
    
    def _get_top_characters_data(self) -> Dict[str, Any]:
        """Get top characters data"""
        try:
            query = """
                SELECT name, tier, value, trend
                FROM characters
                WHERE is_active = TRUE
                ORDER BY value DESC
                LIMIT 5
            """
            result = self.db.execute_query(query)
            
            characters = []
            if not result.empty:
                for _, row in result.iterrows():
                    characters.append({
                        "name": row['name'],
                        "tier": row['tier'],
                        "value": float(row['value']),
                        "trend": row['trend']
                    })
            
            return {"characters": characters}
        except Exception as e:
            self.logger.error(f"Failed to get top characters data: {e}")
            return {"characters": []}