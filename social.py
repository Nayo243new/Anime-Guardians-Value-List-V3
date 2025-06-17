import pandas as pd
from datetime import datetime, timedelta
import logging

class SocialManager:
    """Enhanced social features for the gaming platform"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.init_social_tables()
    
    def init_social_tables(self):
        """Initialize social feature database tables"""
        query = """
        CREATE TABLE IF NOT EXISTS user_friends (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            friend_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            status VARCHAR(20) DEFAULT 'pending',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, friend_id),
            CHECK (user_id != friend_id)
        );
        
        CREATE TABLE IF NOT EXISTS user_posts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            post_type VARCHAR(50) NOT NULL,
            content TEXT NOT NULL,
            media_url TEXT,
            character_mentioned VARCHAR(255),
            trade_id INTEGER,
            likes_count INTEGER DEFAULT 0,
            comments_count INTEGER DEFAULT 0,
            visibility VARCHAR(20) DEFAULT 'public',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS trading_groups (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            description TEXT,
            owner_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            member_count INTEGER DEFAULT 1,
            is_private BOOLEAN DEFAULT FALSE,
            group_type VARCHAR(50) DEFAULT 'casual',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        return self.db_manager.execute_query(query, fetch=False)
    
    def send_friend_request(self, user_id, friend_id):
        """Send friend request"""
        query = """
        INSERT INTO user_friends (user_id, friend_id, status)
        VALUES (%s, %s, 'pending')
        ON CONFLICT (user_id, friend_id) DO NOTHING
        """
        return self.db_manager.execute_query(query, (user_id, friend_id), fetch=False)
    
    def accept_friend_request(self, user_id, friend_id):
        """Accept friend request and create mutual friendship"""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            
            # Update original request
            cursor.execute("""
                UPDATE user_friends 
                SET status = 'accepted', updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s AND friend_id = %s
            """, (friend_id, user_id))
            
            # Create mutual friendship
            cursor.execute("""
                INSERT INTO user_friends (user_id, friend_id, status)
                VALUES (%s, %s, 'accepted')
                ON CONFLICT (user_id, friend_id) 
                DO UPDATE SET status = 'accepted', updated_at = CURRENT_TIMESTAMP
            """, (user_id, friend_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Accept friend request error: {e}")
            conn.rollback()
            return False
        finally:
            self.db_manager.return_connection(conn)
    
    def get_user_friends(self, user_id):
        """Get user's friends list"""
        query = """
        SELECT u.user_id, u.username, u.display_name, uf.status, uf.created_at
        FROM user_friends uf
        JOIN users u ON u.user_id = uf.friend_id
        WHERE uf.user_id = %s AND uf.status = 'accepted'
        ORDER BY uf.created_at DESC
        """
        return self.db_manager.execute_query(query, (user_id,))
    
    def get_pending_friend_requests(self, user_id):
        """Get pending friend requests"""
        query = """
        SELECT u.user_id, u.username, u.display_name, uf.created_at
        FROM user_friends uf
        JOIN users u ON u.user_id = uf.user_id
        WHERE uf.friend_id = %s AND uf.status = 'pending'
        ORDER BY uf.created_at DESC
        """
        return self.db_manager.execute_query(query, (user_id,))
    
    def create_post(self, user_id, post_type, content, character_mentioned=None, trade_id=None):
        """Create a new post"""
        query = """
        INSERT INTO user_posts (user_id, post_type, content, character_mentioned, trade_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """
        result = self.db_manager.execute_query(
            query, (user_id, post_type, content, character_mentioned, trade_id)
        )
        return result.iloc[0]['id'] if not result.empty else None
    
    def get_activity_feed(self, user_id, limit=50):
        """Get activity feed for user"""
        query = """
        SELECT p.id, p.post_type, p.content, p.character_mentioned, p.likes_count,
               p.comments_count, p.created_at, u.username, u.display_name
        FROM user_posts p
        JOIN users u ON u.user_id = p.user_id
        WHERE p.user_id IN (
            SELECT friend_id FROM user_friends WHERE user_id = %s AND status = 'accepted'
            UNION
            SELECT %s
        ) AND p.visibility = 'public'
        ORDER BY p.created_at DESC
        LIMIT %s
        """
        return self.db_manager.execute_query(query, (user_id, user_id, limit))
    
    def like_post(self, post_id, user_id):
        """Like a post"""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            
            # Add like
            cursor.execute("""
                INSERT INTO post_likes (post_id, user_id)
                VALUES (%s, %s)
                ON CONFLICT (post_id, user_id) DO NOTHING
            """, (post_id, user_id))
            
            # Update like count
            cursor.execute("""
                UPDATE user_posts 
                SET likes_count = (SELECT COUNT(*) FROM post_likes WHERE post_id = %s)
                WHERE id = %s
            """, (post_id, post_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Like post error: {e}")
            conn.rollback()
            return False
        finally:
            self.db_manager.return_connection(conn)
    
    def follow_user(self, follower_id, following_id):
        """Follow another user"""
        query = """
        INSERT INTO user_follows (follower_id, following_id)
        VALUES (%s, %s)
        ON CONFLICT (follower_id, following_id) DO NOTHING
        """
        return self.db_manager.execute_query(query, (follower_id, following_id), fetch=False)
    
    def get_leaderboard(self, category='profit', limit=10):
        """Get leaderboard for different categories"""
        if category == 'profit':
            query = """
            SELECT u.user_id, u.username, u.display_name, u.virtual_currency,
                   COALESCE(SUM(t.profit_loss), 0) as total_profit,
                   COUNT(t.trade_id) as trade_count
            FROM users u
            LEFT JOIN trades t ON u.user_id = t.user_id
            WHERE u.role != 'Banned'
            GROUP BY u.user_id, u.username, u.display_name, u.virtual_currency
            ORDER BY total_profit DESC
            LIMIT %s
            """
        elif category == 'achievements':
            query = """
            SELECT u.user_id, u.username, u.display_name,
                   COUNT(ua.achievement_id) as achievement_count
            FROM users u
            LEFT JOIN user_achievements ua ON u.user_id = ua.user_id
            WHERE u.role != 'Banned'
            GROUP BY u.user_id, u.username, u.display_name
            ORDER BY achievement_count DESC
            LIMIT %s
            """
        else:
            query = """
            SELECT u.user_id, u.username, u.display_name, u.virtual_currency
            FROM users u
            WHERE u.role != 'Banned'
            ORDER BY u.virtual_currency DESC
            LIMIT %s
            """
        
        return self.db_manager.execute_query(query, (limit,))
    
    def create_trading_group(self, owner_id, name, description, is_private=False):
        """Create a new trading group"""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            
            # Create group
            cursor.execute("""
                INSERT INTO trading_groups (name, description, owner_id, is_private)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (name, description, owner_id, is_private))
            
            group_id = cursor.fetchone()[0]
            
            # Add owner as member
            cursor.execute("""
                INSERT INTO group_memberships (group_id, user_id, role)
                VALUES (%s, %s, 'owner')
            """, (group_id, owner_id))
            
            conn.commit()
            return group_id
            
        except Exception as e:
            self.logger.error(f"Create trading group error: {e}")
            conn.rollback()
            return None
        finally:
            self.db_manager.return_connection(conn)
    
    def get_user_groups(self, user_id):
        """Get groups user is member of"""
        query = """
        SELECT tg.id, tg.name, tg.description, tg.member_count, gm.role, tg.created_at
        FROM trading_groups tg
        JOIN group_memberships gm ON tg.id = gm.group_id
        WHERE gm.user_id = %s
        ORDER BY tg.created_at DESC
        """
        return self.db_manager.execute_query(query, (user_id,))
    
    def get_trending_discussions(self, limit=10):
        """Get trending character discussions"""
        query = """
        SELECT cd.id, cd.character_name, cd.title, cd.upvotes, cd.downvotes,
               cd.replies_count, cd.created_at, u.username
        FROM character_discussions cd
        JOIN users u ON cd.user_id = u.user_id
        WHERE cd.created_at > CURRENT_TIMESTAMP - INTERVAL '7 days'
        ORDER BY (cd.upvotes - cd.downvotes) DESC, cd.replies_count DESC
        LIMIT %s
        """
        return self.db_manager.execute_query(query, (limit,))