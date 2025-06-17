import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging

class AdvancedAnalytics:
    """Advanced analytics and data visualization for the gaming platform"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.init_analytics_tables()
    
    def init_analytics_tables(self):
        """Initialize analytics tracking tables"""
        query = """
        CREATE TABLE IF NOT EXISTS user_sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
            session_start TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            session_end TIMESTAMP WITH TIME ZONE,
            duration_minutes INTEGER,
            pages_visited INTEGER DEFAULT 0,
            trades_made INTEGER DEFAULT 0,
            ip_address INET,
            user_agent TEXT
        );
        
        CREATE TABLE IF NOT EXISTS portfolio_snapshots (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            total_value DECIMAL(15,2) NOT NULL,
            character_count INTEGER NOT NULL,
            top_character VARCHAR(255),
            risk_score DECIMAL(5,2),
            diversification_score DECIMAL(5,2),
            snapshot_date DATE DEFAULT CURRENT_DATE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, snapshot_date)
        );
        """
        
        return self.db_manager.execute_query(query, fetch=False)
    
    def track_user_action(self, user_id, action_type, character_involved=None, amount_involved=None):
        """Track user behavior for analytics"""
        return True  # Simplified for now
    
    def calculate_risk_score(self, portfolio_data):
        """Calculate portfolio risk score (0-100)"""
        if not portfolio_data:
            return 0
        
        values = [item.get('current_value', 0) for item in portfolio_data]
        if len(values) < 2:
            return 50  # Medium risk for single asset
        
        # Calculate coefficient of variation
        mean_value = np.mean(values)
        std_value = np.std(values)
        cv = (std_value / mean_value) * 100 if mean_value > 0 else 50
        
        # Normalize to 0-100 scale
        return min(100, max(0, int(cv)))
    
    def calculate_diversification_score(self, portfolio_data):
        """Calculate portfolio diversification score (0-100)"""
        if not portfolio_data:
            return 0
        
        if len(portfolio_data) == 1:
            return 0  # No diversification
        
        # Calculate Herfindahl-Hirschman Index
        total_value = sum(item.get('current_value', 0) for item in portfolio_data)
        if total_value == 0:
            return 0
        
        hhi = sum((item.get('current_value', 0) / total_value) ** 2 for item in portfolio_data)
        
        # Convert to diversification score (inverse of concentration)
        diversification = (1 - hhi) * 100
        return min(100, max(0, int(diversification)))
    
    def get_user_performance_metrics(self, user_id, days=30):
        """Get comprehensive user performance metrics"""
        return {
            'portfolio': pd.DataFrame(),
            'trading': pd.DataFrame(),
            'activity': pd.DataFrame()
        }
    
    def create_performance_dashboard(self, user_id):
        """Create comprehensive performance dashboard"""
        return None  # Simplified for now
    
    def create_market_trends_chart(self):
        """Create market trends visualization"""
        return None  # Simplified for now
    
    def generate_insights(self, user_id):
        """Generate AI-powered insights for user"""
        return []  # Simplified for now