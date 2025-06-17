import streamlit as st
from datetime import datetime
import pandas as pd

class GuestTradingManager:
    """Handle trading operations for guest users using session storage"""
    
    def __init__(self):
        pass
    
    def get_guest_portfolio(self):
        """Get guest's current portfolio from session"""
        portfolio_data = []
        for character_name, data in st.session_state.guest_portfolio.items():
            if data['quantity'] > 0:
                portfolio_data.append({
                    'character_name': character_name,
                    'quantity': data['quantity'],
                    'average_price': data['average_price'],
                    'current_price': data.get('current_price', data['average_price'])
                })
        return pd.DataFrame(portfolio_data)
    
    def get_guest_owned_quantity(self, character_name):
        """Get quantity of character owned by guest"""
        if character_name in st.session_state.guest_portfolio:
            return st.session_state.guest_portfolio[character_name]['quantity']
        return 0
    
    def guest_buy_character(self, character_name, quantity, price):
        """Buy character for guest user"""
        total_cost = price * quantity
        
        # Check if guest has enough currency
        if st.session_state.guest_virtual_currency < total_cost:
            return False
        
        # Update guest currency
        st.session_state.guest_virtual_currency -= total_cost
        
        # Update portfolio
        if character_name in st.session_state.guest_portfolio:
            # Update existing entry
            current_qty = st.session_state.guest_portfolio[character_name]['quantity']
            current_avg = st.session_state.guest_portfolio[character_name]['average_price']
            
            new_qty = current_qty + quantity
            new_avg = ((current_avg * current_qty) + (price * quantity)) / new_qty
            
            st.session_state.guest_portfolio[character_name] = {
                'quantity': new_qty,
                'average_price': new_avg,
                'current_price': price
            }
        else:
            # Create new entry
            st.session_state.guest_portfolio[character_name] = {
                'quantity': quantity,
                'average_price': price,
                'current_price': price
            }
        
        # Record trade
        trade_record = {
            'character_name': character_name,
            'trade_type': 'buy',
            'quantity': quantity,
            'price': price,
            'total_amount': total_cost,
            'trade_date': datetime.now(),
            'profit_loss': 0
        }
        st.session_state.guest_trades.append(trade_record)
        
        return True
    
    def guest_sell_character(self, character_name, quantity, price):
        """Sell character for guest user"""
        # Check if guest owns enough
        owned_qty = self.get_guest_owned_quantity(character_name)
        if owned_qty < quantity:
            return False
        
        total_value = price * quantity
        
        # Calculate profit/loss
        avg_price = st.session_state.guest_portfolio[character_name]['average_price']
        profit_loss = (price - avg_price) * quantity
        
        # Update guest currency
        st.session_state.guest_virtual_currency += total_value
        
        # Update portfolio
        new_qty = owned_qty - quantity
        if new_qty == 0:
            # Remove from portfolio
            st.session_state.guest_portfolio[character_name]['quantity'] = 0
        else:
            # Update quantity
            st.session_state.guest_portfolio[character_name]['quantity'] = new_qty
            st.session_state.guest_portfolio[character_name]['current_price'] = price
        
        # Record trade
        trade_record = {
            'character_name': character_name,
            'trade_type': 'sell',
            'quantity': quantity,
            'price': price,
            'total_amount': total_value,
            'trade_date': datetime.now(),
            'profit_loss': profit_loss
        }
        st.session_state.guest_trades.append(trade_record)
        
        return True
    
    def get_guest_trades(self, limit=100):
        """Get guest's trading history"""
        trades = st.session_state.guest_trades[-limit:] if st.session_state.guest_trades else []
        trades.reverse()  # Most recent first
        return pd.DataFrame(trades)
    
    def get_guest_trading_statistics(self):
        """Get guest's trading statistics"""
        trades_df = pd.DataFrame(st.session_state.guest_trades)
        
        if trades_df.empty:
            return {
                'total_trades': 0,
                'total_profit_loss': 0,
                'win_rate': 0,
                'profitable_trades': 0,
                'losing_trades': 0
            }
        
        # Calculate statistics
        total_trades = len(trades_df)
        sell_trades = trades_df[trades_df['trade_type'] == 'sell']
        
        if not sell_trades.empty:
            total_profit_loss = sell_trades['profit_loss'].sum()
            profitable_trades = len(sell_trades[sell_trades['profit_loss'] > 0])
            losing_trades = len(sell_trades[sell_trades['profit_loss'] < 0])
            win_rate = (profitable_trades / len(sell_trades)) * 100 if len(sell_trades) > 0 else 0
        else:
            total_profit_loss = 0
            profitable_trades = 0
            losing_trades = 0
            win_rate = 0
        
        return {
            'total_trades': total_trades,
            'total_profit_loss': total_profit_loss,
            'win_rate': win_rate,
            'profitable_trades': profitable_trades,
            'losing_trades': losing_trades
        }
    
    def get_guest_portfolio_value(self):
        """Calculate total guest portfolio value"""
        total_value = 0
        for character_name, data in st.session_state.guest_portfolio.items():
            if data['quantity'] > 0:
                total_value += data['quantity'] * data['current_price']
        return total_value
    
    def reset_guest_session(self):
        """Reset guest session data"""
        st.session_state.guest_virtual_currency = 10000
        st.session_state.guest_portfolio = {}
        st.session_state.guest_trades = []