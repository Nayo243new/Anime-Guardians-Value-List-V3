import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64
import io

class Utils:
    @staticmethod
    def format_currency(amount):
        """Format currency with proper commas and dollar sign"""
        return f"${amount:,.2f}"
    
    @staticmethod
    def format_number(number):
        """Format number with commas"""
        return f"{number:,}"
    
    @staticmethod
    def get_tier_color(tier):
        """Get color for tier"""
        colors = {
            "S+": "#FF6B6B",  # Red
            "S": "#FF8E53",   # Orange  
            "A+": "#FFD93D",  # Yellow
            "A": "#6BCF7F",   # Green
            "A-": "#4ECDC4"   # Teal
        }
        return colors.get(tier, "#CCCCCC")
    
    @staticmethod
    def get_trend_emoji(trend):
        """Get emoji for trend"""
        emojis = {
            "Overpriced": "🔺",
            "Stable": "⚖️",
            "Underpriced": "🔻"
        }
        return emojis.get(trend, "📊")
    
    @staticmethod
    def get_demand_emoji(demand):
        """Get emoji for demand level"""
        if demand >= 8:
            return "🔥"
        elif demand >= 5:
            return "📈"
        else:
            return "📊"
    
    @staticmethod
    def create_profit_loss_chart(trades_data):
        """Create profit/loss chart"""
        if trades_data.empty:
            return None
        
        # Calculate cumulative P&L
        trades_sorted = trades_data.sort_values('trade_date')
        trades_sorted['cumulative_pl'] = trades_sorted['profit_loss'].cumsum()
        
        fig = px.line(
            trades_sorted,
            x='trade_date',
            y='cumulative_pl',
            title='Cumulative Profit/Loss Over Time',
            labels={
                'cumulative_pl': 'Cumulative P&L ($)',
                'trade_date': 'Date'
            }
        )
        
        # Add zero line
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        # Color the line based on profit/loss
        fig.update_traces(
            line_color='green' if trades_sorted['cumulative_pl'].iloc[-1] > 0 else 'red'
        )
        
        return fig
    
    @staticmethod
    def create_portfolio_pie_chart(portfolio_data, tier_data):
        """Create portfolio distribution pie chart"""
        if portfolio_data.empty:
            return None
        
        # Merge with tier data to get tiers
        portfolio_with_tiers = portfolio_data.merge(
            tier_data[['name', 'tier', 'value']], 
            left_on='character_name', 
            right_on='name',
            how='left'
        )
        
        # Calculate values
        portfolio_with_tiers['total_value'] = portfolio_with_tiers['quantity'] * portfolio_with_tiers['value']
        
        # Group by tier
        tier_values = portfolio_with_tiers.groupby('tier')['total_value'].sum().reset_index()
        
        # Create pie chart
        fig = px.pie(
            tier_values,
            values='total_value',
            names='tier',
            title='Portfolio Distribution by Tier',
            color='tier',
            color_discrete_map={
                'S+': '#FF6B6B',
                'S': '#FF8E53',
                'A+': '#FFD93D',
                'A': '#6BCF7F',
                'A-': '#4ECDC4'
            }
        )
        
        return fig
    
    @staticmethod
    def create_trading_volume_chart(trading_data):
        """Create trading volume chart"""
        if trading_data.empty:
            return None
        
        # Group by date
        daily_volume = trading_data.groupby(trading_data['trade_date'].dt.date).agg({
            'total_value': 'sum',
            'trade_id': 'count'
        }).reset_index()
        
        daily_volume.columns = ['date', 'volume', 'trade_count']
        
        # Create dual-axis chart
        fig = go.Figure()
        
        # Add volume bars
        fig.add_trace(go.Bar(
            x=daily_volume['date'],
            y=daily_volume['volume'],
            name='Trading Volume ($)',
            yaxis='y',
            opacity=0.7
        ))
        
        # Add trade count line
        fig.add_trace(go.Scatter(
            x=daily_volume['date'],
            y=daily_volume['trade_count'],
            mode='lines+markers',
            name='Number of Trades',
            yaxis='y2',
            line=dict(color='red')
        ))
        
        # Update layout for dual axis
        fig.update_layout(
            title='Daily Trading Activity',
            xaxis_title='Date',
            yaxis=dict(
                title='Trading Volume ($)',
                side='left'
            ),
            yaxis2=dict(
                title='Number of Trades',
                side='right',
                overlaying='y'
            ),
            hovermode='x unified'
        )
        
        return fig
    
    @staticmethod
    def create_tier_distribution_chart(tier_data):
        """Create tier distribution chart"""
        if tier_data.empty:
            return None
        
        tier_counts = tier_data.groupby('tier').size().reset_index(name='count')
        
        fig = px.bar(
            tier_counts,
            x='tier',
            y='count',
            title='Character Distribution by Tier',
            color='tier',
            color_discrete_map={
                'S+': '#FF6B6B',
                'S': '#FF8E53',
                'A+': '#FFD93D',
                'A': '#6BCF7F',
                'A-': '#4ECDC4'
            }
        )
        
        fig.update_layout(
            xaxis_title='Tier',
            yaxis_title='Number of Characters'
        )
        
        return fig
    
    @staticmethod
    def create_demand_vs_value_scatter(tier_data):
        """Create demand vs value scatter plot"""
        if tier_data.empty:
            return None
        
        fig = px.scatter(
            tier_data,
            x='demand',
            y='value',
            color='tier',
            size='value',
            hover_data=['name'],
            title='Character Demand vs Value',
            color_discrete_map={
                'S+': '#FF6B6B',
                'S': '#FF8E53',
                'A+': '#FFD93D',
                'A': '#6BCF7F',
                'A-': '#4ECDC4'
            }
        )
        
        fig.update_layout(
            xaxis_title='Demand Level',
            yaxis_title='Value ($)'
        )
        
        return fig
    
    @staticmethod
    def validate_image(uploaded_file):
        """Validate uploaded image file"""
        if uploaded_file is None:
            return False, "No file uploaded"
        
        # Check file size (max 5MB)
        if uploaded_file.size > 5 * 1024 * 1024:
            return False, "File size too large (max 5MB)"
        
        # Check file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
        if uploaded_file.type not in allowed_types:
            return False, "Invalid file type (only JPG, JPEG, PNG allowed)"
        
        return True, "Valid file"
    
    @staticmethod
    def resize_image(image, max_size=(300, 300)):
        """Resize image while maintaining aspect ratio"""
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        return image
    
    @staticmethod
    def image_to_base64(image):
        """Convert PIL image to base64 string"""
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()
    
    @staticmethod
    def base64_to_image(base64_string):
        """Convert base64 string to PIL image"""
        try:
            image_data = base64.b64decode(base64_string)
            return Image.open(io.BytesIO(image_data))
        except:
            return None
    
    @staticmethod
    def calculate_win_rate(trades_data):
        """Calculate win rate from trades"""
        if trades_data.empty:
            return 0
        
        sell_trades = trades_data[trades_data['action'] == 'SELL']
        if sell_trades.empty:
            return 0
        
        profitable_trades = len(sell_trades[sell_trades['profit_loss'] > 0])
        total_sell_trades = len(sell_trades)
        
        return (profitable_trades / total_sell_trades) * 100 if total_sell_trades > 0 else 0
    
    @staticmethod
    def get_user_rank(user_stats, all_users_stats):
        """Calculate user rank based on profit"""
        if not all_users_stats or 'total_profit_loss' not in user_stats:
            return "Unranked"
        
        user_profit = user_stats.get('total_profit_loss', 0)
        better_users = sum(1 for stats in all_users_stats if stats.get('total_profit_loss', 0) > user_profit)
        
        total_users = len(all_users_stats)
        rank = better_users + 1
        
        # Convert to percentile
        percentile = (total_users - rank + 1) / total_users * 100
        
        if percentile >= 90:
            return "Diamond 💎"
        elif percentile >= 75:
            return "Platinum 🏆"
        elif percentile >= 50:
            return "Gold 🥇"
        elif percentile >= 25:
            return "Silver 🥈"
        else:
            return "Bronze 🥉"
    
    @staticmethod
    def format_time_ago(timestamp):
        """Format timestamp to 'time ago' format"""
        if pd.isna(timestamp):
            return "Never"
        
        now = datetime.now()
        if hasattr(timestamp, 'to_pydatetime'):
            timestamp = timestamp.to_pydatetime()
        
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"
    
    @staticmethod
    def create_leaderboard_table(users_data, current_user_id=None):
        """Create formatted leaderboard table"""
        if users_data.empty:
            return pd.DataFrame()
        
        # Sort by total profit/loss
        leaderboard = users_data.sort_values('total_profit_loss', ascending=False).reset_index(drop=True)
        
        # Add rank
        leaderboard['rank'] = range(1, len(leaderboard) + 1)
        
        # Format columns
        leaderboard['total_profit_loss'] = leaderboard['total_profit_loss'].apply(Utils.format_currency)
        leaderboard['total_trades'] = leaderboard['total_trades'].apply(Utils.format_number)
        
        # Highlight current user
        if current_user_id:
            leaderboard['highlight'] = leaderboard['user_id'] == current_user_id
        
        return leaderboard[['rank', 'username', 'total_profit_loss', 'total_trades']]
