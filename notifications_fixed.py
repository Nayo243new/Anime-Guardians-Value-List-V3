import pandas as pd
from datetime import datetime, timedelta
import logging
import json

class NotificationManager:
    """Advanced notification and alert system"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.init_notification_tables()
    
    def init_notification_tables(self):
        """Initialize notification system tables"""
        query = """
        CREATE TABLE IF NOT EXISTS notifications (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            notification_type VARCHAR(50) NOT NULL,
            title VARCHAR(255) NOT NULL,
            message TEXT NOT NULL,
            action_url TEXT,
            action_text VARCHAR(100),
            priority VARCHAR(20) DEFAULT 'medium',
            metadata JSONB,
            is_read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            read_at TIMESTAMP WITH TIME ZONE
        );
        
        CREATE TABLE IF NOT EXISTS price_alerts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            character_name VARCHAR(255) NOT NULL,
            alert_type VARCHAR(20) NOT NULL CHECK (alert_type IN ('price_above', 'price_below', 'percentage_change')),
            target_price DECIMAL(15,2),
            percentage_change DECIMAL(5,2),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            triggered_at TIMESTAMP WITH TIME ZONE
        );
        
        CREATE TABLE IF NOT EXISTS notification_preferences (
            user_id INTEGER PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
            email_notifications BOOLEAN DEFAULT TRUE,
            push_notifications BOOLEAN DEFAULT TRUE,
            achievement_alerts BOOLEAN DEFAULT TRUE,
            trading_alerts BOOLEAN DEFAULT TRUE,
            price_alerts BOOLEAN DEFAULT TRUE,
            social_alerts BOOLEAN DEFAULT TRUE,
            system_announcements BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS system_announcements (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            announcement_type VARCHAR(50) DEFAULT 'general',
            priority VARCHAR(20) DEFAULT 'medium',
            target_roles TEXT[] DEFAULT ARRAY['Regular'],
            is_active BOOLEAN DEFAULT TRUE,
            created_by INTEGER REFERENCES users(user_id),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            end_date TIMESTAMP WITH TIME ZONE
        );
        """
        
        try:
            return self.db_manager.execute_query(query, fetch=False)
        except Exception as e:
            self.logger.error(f"Notification table initialization error: {e}")
            return False
    
    def create_notification(self, user_id, notification_type, title, message, 
                          action_url=None, action_text=None, priority='medium', metadata=None):
        """Create a new notification"""
        query = """
        INSERT INTO notifications (user_id, notification_type, title, message, 
                                 action_url, action_text, priority, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        try:
            metadata_json = json.dumps(metadata) if metadata else None
            result = self.db_manager.execute_query(
                query, 
                (user_id, notification_type, title, message, action_url, action_text, priority, metadata_json)
            )
            return result.iloc[0]['id'] if not result.empty else None
        except Exception as e:
            self.logger.error(f"Error creating notification: {e}")
            return None
    
    def get_user_notifications(self, user_id, limit=50, unread_only=False):
        """Get user notifications"""
        query = """
        SELECT * FROM notifications 
        WHERE user_id = %s
        """
        
        if unread_only:
            query += " AND is_read = FALSE"
        
        query += " ORDER BY created_at DESC LIMIT %s"
        
        try:
            return self.db_manager.execute_query(query, (user_id, limit))
        except Exception as e:
            self.logger.error(f"Error getting notifications: {e}")
            return pd.DataFrame()
    
    def mark_notification_read(self, notification_id, user_id):
        """Mark notification as read"""
        query = """
        UPDATE notifications 
        SET is_read = TRUE, read_at = CURRENT_TIMESTAMP 
        WHERE id = %s AND user_id = %s
        """
        
        try:
            return self.db_manager.execute_query(query, (notification_id, user_id), fetch=False)
        except Exception as e:
            self.logger.error(f"Error marking notification as read: {e}")
            return False
    
    def mark_all_read(self, user_id):
        """Mark all notifications as read for user"""
        query = """
        UPDATE notifications 
        SET is_read = TRUE, read_at = CURRENT_TIMESTAMP 
        WHERE user_id = %s AND is_read = FALSE
        """
        
        try:
            return self.db_manager.execute_query(query, (user_id,), fetch=False)
        except Exception as e:
            self.logger.error(f"Error marking all notifications as read: {e}")
            return False
    
    def create_price_alert(self, user_id, character_name, alert_type, target_price=None, percentage_change=None):
        """Create price alert for character"""
        return True  # Simplified for now
    
    def check_price_alerts(self, character_name, current_price, previous_price=None):
        """Check and trigger price alerts"""
        return []  # Simplified for now
    
    def create_achievement_notification(self, user_id, achievement_name, achievement_description):
        """Create achievement unlock notification"""
        return self.create_notification(
            user_id=user_id,
            notification_type='achievement',
            title='🏆 Achievement Unlocked!',
            message=f'You earned the "{achievement_name}" achievement! {achievement_description}',
            priority='high'
        )
    
    def create_trading_notification(self, user_id, trade_type, character_name, profit_loss):
        """Create trading result notification"""
        icon = "📈" if profit_loss >= 0 else "📉"
        profit_text = f"${profit_loss:,.2f}" if profit_loss >= 0 else f"-${abs(profit_loss):,.2f}"
        
        return self.create_notification(
            user_id=user_id,
            notification_type='trading',
            title=f'{icon} Trade Completed',
            message=f'Your {trade_type} of "{character_name}" resulted in {profit_text}',
            priority='medium'
        )
    
    def get_notification_summary(self, user_id):
        """Get notification summary for user"""
        query = """
        SELECT 
            COUNT(*) as total_notifications,
            COUNT(CASE WHEN is_read = FALSE THEN 1 END) as unread_count,
            COUNT(CASE WHEN notification_type = 'achievement' AND is_read = FALSE THEN 1 END) as unread_achievements,
            COUNT(CASE WHEN notification_type = 'trading' AND is_read = FALSE THEN 1 END) as unread_trading
        FROM notifications 
        WHERE user_id = %s
        """
        
        try:
            result = self.db_manager.execute_query(query, (user_id,))
            return result.iloc[0].to_dict() if not result.empty else {}
        except Exception as e:
            self.logger.error(f"Error getting notification summary: {e}")
            return {}