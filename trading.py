import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

class TradingManager:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def get_user_portfolio(self, user_id):
        """Get user's current portfolio"""
        return self.db.execute_query("""
            SELECT character_name, quantity, average_price
            FROM portfolios
            WHERE user_id = %s AND quantity > 0
            ORDER BY character_name
        """, (user_id,))
    
    def get_owned_quantity(self, user_id, character_name):
        """Get quantity of character owned by user"""
        result = self.db.execute_query("""
            SELECT quantity FROM portfolios
            WHERE user_id = %s AND character_name = %s
        """, (user_id, character_name))
        
        if not result.empty:
            return result.iloc[0]['quantity']
        return 0
    
    def buy_character(self, user_id, character_name, quantity, price):
        """Buy character"""
        total_cost = price * quantity
        
        # Check if user has enough currency
        user_data = self.db.execute_query("""
            SELECT virtual_currency FROM users WHERE user_id = %s
        """, (user_id,))
        
        if user_data.empty or user_data.iloc[0]['virtual_currency'] < total_cost:
            return False
        
        # Update user currency
        new_balance = int(user_data.iloc[0]['virtual_currency']) - int(total_cost)
        self.db.execute_query("""
            UPDATE users SET virtual_currency = %s WHERE user_id = %s
        """, (new_balance, user_id), fetch=False)
        
        # Update portfolio
        existing = self.db.execute_query("""
            SELECT quantity, average_price FROM portfolios
            WHERE user_id = %s AND character_name = %s
        """, (user_id, character_name))
        
        if existing.empty:
            # Create new portfolio entry
            self.db.execute_query("""
                INSERT INTO portfolios (user_id, character_name, quantity, average_price)
                VALUES (%s, %s, %s, %s)
            """, (user_id, character_name, quantity, price), fetch=False)
        else:
            # Update existing entry
            current_qty = existing.iloc[0]['quantity']
            current_avg = existing.iloc[0]['average_price']
            
            new_qty = current_qty + quantity
            new_avg = ((current_avg * current_qty) + (price * quantity)) / new_qty
            
            self.db.execute_query("""
                UPDATE portfolios 
                SET quantity = %s, average_price = %s, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s AND character_name = %s
            """, (new_qty, new_avg, user_id, character_name), fetch=False)
        
        # Record trade
        self.db.execute_query("""
            INSERT INTO trades (user_id, character_name, action, quantity, price, total_value)
            VALUES (%s, %s, 'BUY', %s, %s, %s)
        """, (user_id, character_name, quantity, price, total_cost), fetch=False)
        
        # Check for achievements after successful trade
        try:
            from achievements import AchievementManager
            achievement_manager = AchievementManager(self.db)
            achievement_manager.check_and_award_achievements(user_id)
        except:
            pass  # Don't fail trades if achievement system has issues
        
        return True
    
    def sell_character(self, user_id, character_name, quantity, price):
        """Sell character"""
        # Check if user owns enough
        owned_qty = self.get_owned_quantity(user_id, character_name)
        if owned_qty < quantity:
            return False
        
        total_value = price * quantity
        
        # Get average purchase price for profit/loss calculation
        portfolio_data = self.db.execute_query("""
            SELECT average_price FROM portfolios
            WHERE user_id = %s AND character_name = %s
        """, (user_id, character_name))
        
        profit_loss = 0
        if not portfolio_data.empty:
            avg_price = portfolio_data.iloc[0]['average_price']
            profit_loss = (price - avg_price) * quantity
        
        # Update user currency
        user_data = self.db.execute_query("""
            SELECT virtual_currency FROM users WHERE user_id = %s
        """, (user_id,))
        
        if not user_data.empty:
            new_balance = int(user_data.iloc[0]['virtual_currency']) + int(total_value)
            self.db.execute_query("""
                UPDATE users SET virtual_currency = %s WHERE user_id = %s
            """, (new_balance, user_id), fetch=False)
        
        # Update portfolio
        new_qty = owned_qty - quantity
        if new_qty == 0:
            # Remove from portfolio
            self.db.execute_query("""
                UPDATE portfolios SET quantity = 0
                WHERE user_id = %s AND character_name = %s
            """, (user_id, character_name), fetch=False)
        else:
            # Update quantity
            self.db.execute_query("""
                UPDATE portfolios 
                SET quantity = %s, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s AND character_name = %s
            """, (new_qty, user_id, character_name), fetch=False)
        
        # Record trade
        self.db.execute_query("""
            INSERT INTO trades (user_id, character_name, action, quantity, price, total_value, profit_loss)
            VALUES (%s, %s, 'SELL', %s, %s, %s, %s)
        """, (user_id, character_name, quantity, price, total_value, profit_loss), fetch=False)
        
        # Check for achievements after successful trade
        try:
            from achievements import AchievementManager
            achievement_manager = AchievementManager(self.db)
            achievement_manager.check_and_award_achievements(user_id)
        except:
            pass  # Don't fail trades if achievement system has issues
        
        return True
    
    def get_user_trades(self, user_id, limit=100):
        """Get user's trading history"""
        return self.db.execute_query("""
            SELECT trade_id, character_name, action, quantity, price, total_value, profit_loss, trade_date
            FROM trades
            WHERE user_id = %s
            ORDER BY trade_date DESC
            LIMIT %s
        """, (user_id, limit))
    
    def get_trading_statistics(self, user_id):
        """Get user's trading statistics"""
        stats = {}
        
        # Total trades
        trades = self.db.execute_query("""
            SELECT COUNT(*) as total_trades,
                   SUM(CASE WHEN action = 'BUY' THEN total_value ELSE 0 END) as total_bought,
                   SUM(CASE WHEN action = 'SELL' THEN total_value ELSE 0 END) as total_sold,
                   SUM(profit_loss) as total_profit_loss
            FROM trades
            WHERE user_id = %s
        """, (user_id,))
        
        if not trades.empty:
            stats.update(trades.iloc[0].to_dict())
        
        # Win/Loss ratio
        profitable_trades = self.db.execute_query("""
            SELECT COUNT(*) as profitable_trades
            FROM trades
            WHERE user_id = %s AND profit_loss > 0
        """, (user_id,))
        
        if not profitable_trades.empty:
            stats['profitable_trades'] = profitable_trades.iloc[0]['profitable_trades']
        
        return stats
    
    def get_market_trends(self):
        """Get market trends and popular characters"""
        return self.db.execute_query("""
            SELECT c.name, c.tier, c.value, c.demand, c.trend,
                   COUNT(t.trade_id) as trade_count,
                   SUM(CASE WHEN t.action = 'BUY' THEN t.quantity ELSE 0 END) as buy_volume,
                   SUM(CASE WHEN t.action = 'SELL' THEN t.quantity ELSE 0 END) as sell_volume
            FROM characters c
            LEFT JOIN trades t ON c.name = t.character_name
                AND t.trade_date >= NOW() - INTERVAL '7 days'
            GROUP BY c.name, c.tier, c.value, c.demand, c.trend
            ORDER BY trade_count DESC, c.value DESC
            LIMIT 20
        """)
    
    def simulate_market_fluctuation(self):
        """Simulate market price fluctuations (for realism)"""
        # This would be called periodically to update character values
        # based on trading activity and demand
        import random
        
        characters = self.db.execute_query("SELECT name, value, demand FROM characters")
        
        for _, char in characters.iterrows():
            # Small random fluctuation based on demand
            base_change = random.uniform(-0.05, 0.05)  # ±5% base change
            demand_multiplier = char['demand'] / 10  # Higher demand = more volatility
            
            change_factor = 1 + (base_change * demand_multiplier)
            new_value = max(1, int(char['value'] * change_factor))
            
            # Update character value
            self.db.execute_query("""
                UPDATE characters SET value = %s WHERE name = %s
            """, (new_value, char['name']), fetch=False)
    
    def get_portfolio_value(self, user_id):
        """Calculate total portfolio value"""
        portfolio = self.get_user_portfolio(user_id)
        total_value = 0
        
        for _, item in portfolio.iterrows():
            current_price = self.db.execute_query("""
                SELECT value FROM characters WHERE name = %s
            """, (item['character_name'],))
            
            if not current_price.empty:
                total_value += current_price.iloc[0]['value'] * item['quantity']
        
        return total_value
