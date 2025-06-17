import json
from datetime import datetime
from typing import Dict, List, Tuple

class AchievementManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.achievements_config = {
            # Trading Achievements
            "first_trade": {
                "name": "First Steps",
                "description": "Complete your first trade",
                "icon": "🏆",
                "rarity": "Common",
                "points": 100
            },
            "profitable_trader": {
                "name": "Profitable Trader",
                "description": "Make a profit of $1,000",
                "icon": "💰",
                "rarity": "Common",
                "points": 250
            },
            "big_trader": {
                "name": "Big Trader",
                "description": "Make a profit of $10,000",
                "icon": "💎",
                "rarity": "Rare",
                "points": 500
            },
            "whale_trader": {
                "name": "Whale Trader",
                "description": "Make a profit of $100,000",
                "icon": "🐋",
                "rarity": "Epic",
                "points": 1000
            },
            "trading_master": {
                "name": "Trading Master",
                "description": "Make a profit of $500,000",
                "icon": "👑",
                "rarity": "Legendary",
                "points": 2500
            },
            
            # Volume Achievements
            "active_trader": {
                "name": "Active Trader",
                "description": "Complete 10 trades",
                "icon": "📈",
                "rarity": "Common",
                "points": 200
            },
            "veteran_trader": {
                "name": "Veteran Trader",
                "description": "Complete 100 trades",
                "icon": "🎖️",
                "rarity": "Rare",
                "points": 750
            },
            "trading_legend": {
                "name": "Trading Legend",
                "description": "Complete 1,000 trades",
                "icon": "⭐",
                "rarity": "Epic",
                "points": 2000
            },
            
            # Win Rate Achievements
            "lucky_streak": {
                "name": "Lucky Streak",
                "description": "Achieve 70% win rate with 20+ trades",
                "icon": "🍀",
                "rarity": "Rare",
                "points": 600
            },
            "master_strategist": {
                "name": "Master Strategist",
                "description": "Achieve 80% win rate with 50+ trades",
                "icon": "🧠",
                "rarity": "Epic",
                "points": 1500
            },
            
            # Collection Achievements
            "collector": {
                "name": "Collector",
                "description": "Own 10 different characters",
                "icon": "📚",
                "rarity": "Common",
                "points": 300
            },
            "hoarder": {
                "name": "Hoarder",
                "description": "Own 50 different characters",
                "icon": "🏛️",
                "rarity": "Rare",
                "points": 800
            },
            "completionist": {
                "name": "Completionist",
                "description": "Own characters from all tiers",
                "icon": "🎯",
                "rarity": "Epic",
                "points": 1200
            },
            
            # Special Achievements
            "high_roller": {
                "name": "High Roller",
                "description": "Make a single trade worth $50,000+",
                "icon": "🎰",
                "rarity": "Epic",
                "points": 1000
            },
            "diversified": {
                "name": "Diversified Portfolio",
                "description": "Own SP, S, A, B, and C tier characters simultaneously",
                "icon": "🌟",
                "rarity": "Rare",
                "points": 700
            },
            "early_adopter": {
                "name": "Early Adopter",
                "description": "Join the platform (automatically earned)",
                "icon": "🎊",
                "rarity": "Common",
                "points": 50
            },
            "theme_explorer": {
                "name": "Theme Explorer",
                "description": "Try all three visual themes",
                "icon": "🎨",
                "rarity": "Common",
                "points": 150
            },
            
            # Time-based Achievements
            "dedicated_user": {
                "name": "Dedicated User",
                "description": "Use the platform for 7 consecutive days",
                "icon": "📅",
                "rarity": "Rare",
                "points": 500
            },
            "loyal_member": {
                "name": "Loyal Member",
                "description": "Use the platform for 30 days",
                "icon": "💝",
                "rarity": "Epic",
                "points": 1500
            }
        }
    
    def init_achievements_table(self):
        """Initialize achievements table"""
        query = """
        CREATE TABLE IF NOT EXISTS user_achievements (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            achievement_id VARCHAR(50) NOT NULL,
            earned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            progress JSONB DEFAULT '{}',
            UNIQUE(user_id, achievement_id)
        );
        """
        self.db_manager.execute_query(query, fetch=False)
    
    def get_user_achievements(self, user_id: int) -> List[Dict]:
        """Get all achievements for a user"""
        query = """
        SELECT achievement_id, earned_date, progress 
        FROM user_achievements 
        WHERE user_id = %s
        """
        earned_achievements = self.db_manager.execute_query(query, (user_id,))
        
        result = []
        earned_ids = {ach[0] for ach in earned_achievements}
        
        for ach_id, config in self.achievements_config.items():
            achievement = {
                "id": ach_id,
                "name": config["name"],
                "description": config["description"],
                "icon": config["icon"],
                "rarity": config["rarity"],
                "points": config["points"],
                "earned": ach_id in earned_ids,
                "earned_date": None,
                "progress": {}
            }
            
            if ach_id in earned_ids:
                for earned in earned_achievements:
                    if earned[0] == ach_id:
                        achievement["earned_date"] = earned[1]
                        achievement["progress"] = earned[2] if earned[2] else {}
                        break
            else:
                # Calculate progress for unearned achievements
                achievement["progress"] = self._calculate_progress(user_id, ach_id)
            
            result.append(achievement)
        
        return result
    
    def _calculate_progress(self, user_id: int, achievement_id: str) -> Dict:
        """Calculate progress towards an achievement"""
        if achievement_id == "first_trade":
            trades = self._get_trade_count(user_id)
            return {"current": min(trades, 1), "target": 1, "percentage": min(trades * 100, 100)}
        
        elif achievement_id == "profitable_trader":
            profit = self._get_total_profit(user_id)
            return {"current": max(0, profit), "target": 1000, "percentage": min(max(0, profit) / 1000 * 100, 100)}
        
        elif achievement_id == "big_trader":
            profit = self._get_total_profit(user_id)
            return {"current": max(0, profit), "target": 10000, "percentage": min(max(0, profit) / 10000 * 100, 100)}
        
        elif achievement_id == "whale_trader":
            profit = self._get_total_profit(user_id)
            return {"current": max(0, profit), "target": 100000, "percentage": min(max(0, profit) / 100000 * 100, 100)}
        
        elif achievement_id == "trading_master":
            profit = self._get_total_profit(user_id)
            return {"current": max(0, profit), "target": 500000, "percentage": min(max(0, profit) / 500000 * 100, 100)}
        
        elif achievement_id == "active_trader":
            trades = self._get_trade_count(user_id)
            return {"current": trades, "target": 10, "percentage": min(trades / 10 * 100, 100)}
        
        elif achievement_id == "veteran_trader":
            trades = self._get_trade_count(user_id)
            return {"current": trades, "target": 100, "percentage": min(trades / 100 * 100, 100)}
        
        elif achievement_id == "trading_legend":
            trades = self._get_trade_count(user_id)
            return {"current": trades, "target": 1000, "percentage": min(trades / 1000 * 100, 100)}
        
        elif achievement_id == "collector":
            unique_chars = self._get_unique_characters_owned(user_id)
            return {"current": unique_chars, "target": 10, "percentage": min(unique_chars / 10 * 100, 100)}
        
        elif achievement_id == "hoarder":
            unique_chars = self._get_unique_characters_owned(user_id)
            return {"current": unique_chars, "target": 50, "percentage": min(unique_chars / 50 * 100, 100)}
        
        else:
            return {"current": 0, "target": 1, "percentage": 0}
    
    def _get_trade_count(self, user_id: int) -> int:
        """Get total number of trades for user"""
        query = "SELECT COUNT(*) FROM trades WHERE user_id = %s"
        result = self.db_manager.execute_query(query, (user_id,))
        return result[0][0] if result else 0
    
    def _get_total_profit(self, user_id: int) -> float:
        """Get total profit for user"""
        query = """
        SELECT COALESCE(SUM(
            CASE 
                WHEN trade_type = 'sell' THEN total_amount 
                ELSE -total_amount 
            END
        ), 0) as total_profit
        FROM trades WHERE user_id = %s
        """
        result = self.db_manager.execute_query(query, (user_id,))
        return float(result[0][0]) if result and result[0][0] else 0.0
    
    def _get_unique_characters_owned(self, user_id: int) -> int:
        """Get number of unique characters owned"""
        query = """
        SELECT COUNT(DISTINCT character_name) 
        FROM portfolio 
        WHERE user_id = %s AND quantity > 0
        """
        result = self.db_manager.execute_query(query, (user_id,))
        return result[0][0] if result else 0
    
    def check_and_award_achievements(self, user_id: int) -> List[str]:
        """Check and award any newly earned achievements"""
        newly_earned = []
        
        # Check each achievement
        for ach_id in self.achievements_config:
            if not self._has_achievement(user_id, ach_id):
                if self._check_achievement_criteria(user_id, ach_id):
                    self._award_achievement(user_id, ach_id)
                    newly_earned.append(ach_id)
        
        return newly_earned
    
    def _has_achievement(self, user_id: int, achievement_id: str) -> bool:
        """Check if user already has achievement"""
        query = "SELECT 1 FROM user_achievements WHERE user_id = %s AND achievement_id = %s"
        result = self.db_manager.execute_query(query, (user_id, achievement_id))
        return len(result) > 0
    
    def _check_achievement_criteria(self, user_id: int, achievement_id: str) -> bool:
        """Check if user meets criteria for achievement"""
        if achievement_id == "first_trade":
            return self._get_trade_count(user_id) >= 1
        
        elif achievement_id == "profitable_trader":
            return self._get_total_profit(user_id) >= 1000
        
        elif achievement_id == "big_trader":
            return self._get_total_profit(user_id) >= 10000
        
        elif achievement_id == "whale_trader":
            return self._get_total_profit(user_id) >= 100000
        
        elif achievement_id == "trading_master":
            return self._get_total_profit(user_id) >= 500000
        
        elif achievement_id == "active_trader":
            return self._get_trade_count(user_id) >= 10
        
        elif achievement_id == "veteran_trader":
            return self._get_trade_count(user_id) >= 100
        
        elif achievement_id == "trading_legend":
            return self._get_trade_count(user_id) >= 1000
        
        elif achievement_id == "lucky_streak":
            return self._check_win_rate(user_id, 0.70, 20)
        
        elif achievement_id == "master_strategist":
            return self._check_win_rate(user_id, 0.80, 50)
        
        elif achievement_id == "collector":
            return self._get_unique_characters_owned(user_id) >= 10
        
        elif achievement_id == "hoarder":
            return self._get_unique_characters_owned(user_id) >= 50
        
        elif achievement_id == "completionist":
            return self._owns_all_tiers(user_id)
        
        elif achievement_id == "high_roller":
            return self._has_large_single_trade(user_id, 50000)
        
        elif achievement_id == "diversified":
            return self._has_diversified_portfolio(user_id)
        
        elif achievement_id == "early_adopter":
            return True  # Automatically earned
        
        return False
    
    def _check_win_rate(self, user_id: int, target_rate: float, min_trades: int) -> bool:
        """Check if user has required win rate with minimum trades"""
        trade_count = self._get_trade_count(user_id)
        if trade_count < min_trades:
            return False
        
        # Calculate win rate based on profitable trades
        query = """
        SELECT COUNT(*) as profitable_trades
        FROM trades t1
        WHERE t1.user_id = %s 
        AND t1.trade_type = 'sell'
        AND EXISTS (
            SELECT 1 FROM trades t2 
            WHERE t2.user_id = %s 
            AND t2.character_name = t1.character_name 
            AND t2.trade_type = 'buy' 
            AND t2.trade_date < t1.trade_date
            AND t2.price < t1.price
        )
        """
        result = self.db_manager.execute_query(query, (user_id, user_id))
        profitable_trades = result[0][0] if result else 0
        
        win_rate = profitable_trades / trade_count if trade_count > 0 else 0
        return win_rate >= target_rate
    
    def _owns_all_tiers(self, user_id: int) -> bool:
        """Check if user owns characters from all tiers"""
        query = """
        SELECT DISTINCT c.tier
        FROM portfolio p
        JOIN characters c ON p.character_name = c.name
        WHERE p.user_id = %s AND p.quantity > 0
        """
        result = self.db_manager.execute_query(query, (user_id,))
        owned_tiers = {row[0] for row in result}
        required_tiers = {'SP', 'S', 'A', 'B', 'C'}
        return required_tiers.issubset(owned_tiers)
    
    def _has_large_single_trade(self, user_id: int, min_amount: float) -> bool:
        """Check if user has made a single large trade"""
        query = "SELECT MAX(total_amount) FROM trades WHERE user_id = %s"
        result = self.db_manager.execute_query(query, (user_id,))
        max_trade = result[0][0] if result and result[0][0] else 0
        return max_trade >= min_amount
    
    def _has_diversified_portfolio(self, user_id: int) -> bool:
        """Check if user has diversified portfolio with all tiers"""
        return self._owns_all_tiers(user_id)
    
    def _award_achievement(self, user_id: int, achievement_id: str):
        """Award achievement to user"""
        query = """
        INSERT INTO user_achievements (user_id, achievement_id, earned_date)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id, achievement_id) DO NOTHING
        """
        self.db_manager.execute_query(query, (user_id, achievement_id, datetime.now()), fetch=False)
    
    def get_achievement_stats(self, user_id: int) -> Dict:
        """Get achievement statistics for user"""
        achievements = self.get_user_achievements(user_id)
        earned = [a for a in achievements if a["earned"]]
        
        total_points = sum(a["points"] for a in earned)
        total_achievements = len(achievements)
        earned_achievements = len(earned)
        
        # Calculate rarity breakdown
        rarity_counts = {}
        for ach in earned:
            rarity = ach["rarity"]
            rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1
        
        return {
            "total_points": total_points,
            "total_achievements": total_achievements,
            "earned_achievements": earned_achievements,
            "completion_percentage": (earned_achievements / total_achievements * 100) if total_achievements > 0 else 0,
            "rarity_breakdown": rarity_counts,
            "recent_achievements": sorted(earned, key=lambda x: x["earned_date"], reverse=True)[:5]
        }
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get achievement leaderboard"""
        query = """
        SELECT u.username, u.display_name, COUNT(ua.achievement_id) as achievement_count,
               COALESCE(SUM(
                   CASE ua.achievement_id
                       WHEN 'early_adopter' THEN 50
                       WHEN 'theme_explorer' THEN 150
                       WHEN 'first_trade' THEN 100
                       WHEN 'profitable_trader' THEN 250
                       WHEN 'active_trader' THEN 200
                       WHEN 'collector' THEN 300
                       WHEN 'big_trader' THEN 500
                       WHEN 'dedicated_user' THEN 500
                       WHEN 'lucky_streak' THEN 600
                       WHEN 'diversified' THEN 700
                       WHEN 'veteran_trader' THEN 750
                       WHEN 'hoarder' THEN 800
                       WHEN 'whale_trader' THEN 1000
                       WHEN 'high_roller' THEN 1000
                       WHEN 'completionist' THEN 1200
                       WHEN 'loyal_member' THEN 1500
                       WHEN 'master_strategist' THEN 1500
                       WHEN 'trading_legend' THEN 2000
                       WHEN 'trading_master' THEN 2500
                       ELSE 0
                   END
               ), 0) as total_points
        FROM users u
        LEFT JOIN user_achievements ua ON u.id = ua.user_id
        WHERE u.role != 'Banned'
        GROUP BY u.id, u.username, u.display_name
        ORDER BY total_points DESC, achievement_count DESC
        LIMIT %s
        """
        result = self.db_manager.execute_query(query, (limit,))
        
        leaderboard = []
        for i, row in enumerate(result):
            leaderboard.append({
                "rank": i + 1,
                "username": row[0],
                "display_name": row[1] or row[0],
                "achievement_count": row[2],
                "total_points": row[3]
            })
        
        return leaderboard