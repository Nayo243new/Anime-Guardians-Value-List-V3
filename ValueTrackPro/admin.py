import pandas as pd
from datetime import datetime, timedelta

class AdminManager:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def get_all_users(self):
        """Get all users (Admin only)"""
        return self.db.execute_query("""
            SELECT user_id, username, email, role, virtual_currency, created_at, last_login
            FROM users
            ORDER BY created_at DESC
        """)
    
    def update_user_role(self, user_id, new_role):
        """Update user role (Admin only)"""
        return self.db.execute_query("""
            UPDATE users SET role = %s WHERE user_id = %s
        """, (new_role, user_id), fetch=False)
    
    def get_user_statistics(self):
        """Get user statistics for admin dashboard"""
        stats = {}
        
        # Total users
        total_users = self.db.execute_query("SELECT COUNT(*) as count FROM users")
        if not total_users.empty:
            stats['total_users'] = total_users.iloc[0]['count']
        
        # Active users today
        active_today = self.db.execute_query("""
            SELECT COUNT(*) as count FROM users 
            WHERE last_login >= CURRENT_DATE
        """)
        if not active_today.empty:
            stats['active_today'] = active_today.iloc[0]['count']
        
        # Total trades
        total_trades = self.db.execute_query("SELECT COUNT(*) as count FROM trades")
        if not total_trades.empty:
            stats['total_trades'] = total_trades.iloc[0]['count']
        
        # Total trading volume
        total_volume = self.db.execute_query("SELECT SUM(total_value) as volume FROM trades")
        if not total_volume.empty and total_volume.iloc[0]['volume'] is not None:
            stats['total_volume'] = total_volume.iloc[0]['volume']
        else:
            stats['total_volume'] = 0
        
        return stats
    
    def get_trading_activity(self, days=30):
        """Get trading activity over time"""
        return self.db.execute_query("""
            SELECT 
                DATE(trade_date) as date,
                COUNT(*) as trade_count,
                SUM(total_value) as total_volume
            FROM trades
            WHERE trade_date >= CURRENT_DATE - INTERVAL '%s days'
            GROUP BY DATE(trade_date)
            ORDER BY date
        """ % days)
    
    def get_recent_trades(self, limit=50):
        """Get recent trades across all users"""
        return self.db.execute_query("""
            SELECT 
                t.trade_date,
                u.username,
                t.character_name,
                t.action,
                t.quantity,
                t.price,
                t.total_value,
                t.profit_loss
            FROM trades t
            JOIN users u ON t.user_id = u.user_id
            ORDER BY t.trade_date DESC
            LIMIT %s
        """, (limit,))
    
    def get_top_traders(self, limit=10):
        """Get top traders by profit"""
        return self.db.execute_query("""
            SELECT 
                u.username,
                SUM(t.profit_loss) as total_profit,
                COUNT(t.trade_id) as total_trades,
                AVG(t.profit_loss) as avg_profit_per_trade
            FROM users u
            JOIN trades t ON u.user_id = t.user_id
            WHERE t.action = 'SELL'
            GROUP BY u.user_id, u.username
            ORDER BY total_profit DESC
            LIMIT %s
        """, (limit,))
    
    def get_character_popularity(self):
        """Get character trading popularity"""
        return self.db.execute_query("""
            SELECT 
                c.name,
                c.tier,
                c.value,
                COUNT(t.trade_id) as trade_count,
                SUM(CASE WHEN t.action = 'BUY' THEN t.quantity ELSE 0 END) as total_bought,
                SUM(CASE WHEN t.action = 'SELL' THEN t.quantity ELSE 0 END) as total_sold
            FROM characters c
            LEFT JOIN trades t ON c.name = t.character_name
            GROUP BY c.name, c.tier, c.value
            ORDER BY trade_count DESC
        """)
    
    def get_database_stats(self):
        """Get database statistics"""
        stats = {}
        
        # Total characters
        char_count = self.db.execute_query("SELECT COUNT(*) as count FROM characters")
        if not char_count.empty:
            stats['total_characters'] = char_count.iloc[0]['count']
        
        # Database size (approximate)
        stats['db_size_mb'] = 5.2  # Placeholder - would need specific database queries
        
        return stats
    
    def ban_user(self, user_id):
        """Ban user (set role to 'Banned')"""
        return self.db.execute_query("""
            UPDATE users SET role = 'Banned' WHERE user_id = %s
        """, (user_id,), fetch=False)
    
    def unban_user(self, user_id):
        """Unban user (set role to 'Regular')"""
        return self.db.execute_query("""
            UPDATE users SET role = 'Regular' WHERE user_id = %s
        """, (user_id,), fetch=False)
    
    def reset_user_currency(self, user_id, amount=10000):
        """Reset user's virtual currency"""
        return self.db.execute_query("""
            UPDATE users SET virtual_currency = %s WHERE user_id = %s
        """, (amount, user_id), fetch=False)
    
    def get_user_activity_log(self, user_id, days=30):
        """Get user activity log"""
        return self.db.execute_query("""
            SELECT 
                trade_date as activity_date,
                'TRADE' as activity_type,
                CONCAT(action, ' ', quantity, 'x ', character_name) as activity_description
            FROM trades
            WHERE user_id = %s AND trade_date >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY trade_date DESC
        """ % ('%s', days), (user_id,))
    
    def bulk_update_character_values(self, multiplier=1.0):
        """Bulk update all character values by a multiplier"""
        return self.db.execute_query("""
            UPDATE characters 
            SET value = CAST(value * %s AS INTEGER),
                updated_at = CURRENT_TIMESTAMP
        """, (multiplier,), fetch=False)
    
    def export_user_data(self, user_id):
        """Export all user data for GDPR compliance"""
        user_data = {}
        
        # User profile
        profile = self.db.execute_query("""
            SELECT * FROM users WHERE user_id = %s
        """, (user_id,))
        if not profile.empty:
            user_data['profile'] = profile.iloc[0].to_dict()
        
        # Portfolio
        portfolio = self.db.execute_query("""
            SELECT * FROM portfolios WHERE user_id = %s
        """, (user_id,))
        if not portfolio.empty:
            user_data['portfolio'] = portfolio.to_dict('records')
        
        # Trades
        trades = self.db.execute_query("""
            SELECT * FROM trades WHERE user_id = %s
        """, (user_id,))
        if not trades.empty:
            user_data['trades'] = trades.to_dict('records')
        
        return user_data
    
    def delete_user_data(self, user_id):
        """Delete all user data (GDPR compliance)"""
        try:
            # Delete trades
            self.db.execute_query("DELETE FROM trades WHERE user_id = %s", (user_id,), fetch=False)
            
            # Delete portfolio
            self.db.execute_query("DELETE FROM portfolios WHERE user_id = %s", (user_id,), fetch=False)
            
            # Delete user
            self.db.execute_query("DELETE FROM users WHERE user_id = %s", (user_id,), fetch=False)
            
            return True
        except:
            return False
