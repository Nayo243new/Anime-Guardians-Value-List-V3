import os
import psycopg2
import pandas as pd
from datetime import datetime
import hashlib
import secrets

class DatabaseManager:
    def __init__(self):
        self.connection_params = {
            'host': os.getenv('PGHOST'),
            'database': os.getenv('PGDATABASE'),
            'user': os.getenv('PGUSER'),
            'password': os.getenv('PGPASSWORD'),
            'port': os.getenv('PGPORT', 5432)
        }
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(**self.connection_params)
        except Exception as e:
            print(f"Database connection error: {e}")
            return None
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    salt VARCHAR(255) NOT NULL,
                    role VARCHAR(20) DEFAULT 'Regular',
                    virtual_currency INTEGER DEFAULT 10000,
                    display_name VARCHAR(100),
                    bio TEXT,
                    profile_photo TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """)
            
            # Characters table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS characters (
                    character_id SERIAL PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    tier VARCHAR(5) NOT NULL,
                    value INTEGER NOT NULL,
                    demand INTEGER NOT NULL,
                    trend VARCHAR(20) NOT NULL,
                    information TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User portfolios table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolios (
                    portfolio_id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id),
                    character_name VARCHAR(100) NOT NULL,
                    quantity INTEGER NOT NULL,
                    average_price DECIMAL(10,2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Trading history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    trade_id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id),
                    character_name VARCHAR(100) NOT NULL,
                    action VARCHAR(10) NOT NULL,
                    quantity INTEGER NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
                    total_value DECIMAL(10,2) NOT NULL,
                    profit_loss DECIMAL(10,2) DEFAULT 0,
                    trade_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User achievements table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_achievements (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                    achievement_id VARCHAR(50) NOT NULL,
                    earned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    progress JSONB DEFAULT '{}',
                    UNIQUE(user_id, achievement_id)
                );
            """)
            
            conn.commit()
            
            # Insert initial character data if empty
            cursor.execute("SELECT COUNT(*) FROM characters")
            if cursor.fetchone()[0] == 0:
                self.insert_initial_characters(cursor)
                conn.commit()
            
            return True
            
        except Exception as e:
            print(f"Database initialization error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def insert_initial_characters(self, cursor):
        """Insert initial character data based on the tier list images"""
        characters_data = [
            # S+ Tier
            ("Placeholder (Baaset) / Gohan", "S+", 0, 3, "Overpriced", "Less than 30 in Game. Top 30 Fourth Season Leaderboards"),
            ("Xiro / Kira", "S+", 0, 3, "Overpriced", "Less than 50 in Game. Top 50 First Season Leaderboards"),
            ("Rika (Queen) / Rika", "S+", 0, 3, "Overpriced", "Less than 30 in Game. Top 30 Second Season Leaderboards"),
            ("Yaido / Yasdora", "S+", 0, 3, "Overpriced", "Less than 30 in Game. Top 30 Third Season Leaderboards"),
            
            # S Tier
            ("Matsuri (Love Pillar) / Mitsuri", "S", 12000, 10, "Overpriced", "Update 6.5 Matsuri Valentines Event Evolved Unit"),
            ("Matsuri / Mitsuri", "S", 10000, 10, "Overpriced", "Update 6.5 Matsuri Valentines Event Unit"),
            ("Griffith (Sacrifice) / Griffith", "S", 7000, 10, "Overpriced", "Update 10 Part 2 Craftable Unit"),
            ("Guts (Berserk) / Guts", "S", 5000, 10, "Overpriced", "Update 10 Part 2 Craftable Evolved Unit"),
            ("Tio (Over Heaven) / Dio", "S", 4000, 7, "Overpriced", "Update 6 Banner Secret Unit"),
            
            # A+ Tier
            ("Beerus (Destroyer) / Beerus", "A+", 3500, 7, "Stable", "Update 9.5 Part 1 Craftable Unit"),
            ("Goku (Ultra Instinct) / Goku", "A+", 3000, 7, "Stable", "Update 9.5 Part 2 Craftable Unit"),
            ("Vegeta (Ultra Ego) / Vegeta", "A+", 3000, 7, "Stable", "Update 9.5 Part 2 Craftable Unit"),
            ("Ainz (Overlord) / Ainz Opal Gown", "A+", 2000, 6, "Stable", "Update 8 Secret Banner Unit"),
            ("Lofy (Gear 5) / Luffy Gear 5", "A+", 1500, 6, "Stable", "Update 7.5 Secret Portal Unit"),
            
            # A Tier
            ("Guts / Guts", "A", 1000, 8, "Unstable", "Update 10 Part 2 Craftable Unit"),
            ("Robin (HSR) / Robin", "A", 950, 7, "Stable", "Update 10 Part 1 Event Unit"),
            ("Castorice (HSR) / Castorice", "A", 950, 7, "Stable", "Update 10 Part 1 Event Unit"),
            ("Kafka (Overpower) / Kafka Hibino", "A", 800, 4, "Stable", "Update 2 Christmas Banner Evolved Unit"),
            ("Void (God Hand) / Void", "A", 750, 7, "Stable", "Update 10 Part 2 Crimson Eclipse Raid Secret Unit"),
            ("Yhwach (Almighty) / Yhwach", "A", 700, 5, "Stable", "Update 9 Kingdom of Wardenreich Raid Portal Evolved Unit"),
            ("Alucord (Vampire King) / Alucard", "A", 700, 5, "Stable", "Update 1 Vampire Castle Portal Evolved Unit"),
            ("Gilgamesh (King of the Heroes) / Gilgamesh", "A", 670, 5, "Stable", "Update 5 Temple Raid Portal Secret Evolved Unit"),
            ("Kurume (Time Spirit) / Kurumi", "A", 650, 5, "Stable", "Update 3 Event Banner Unit"),
            ("Homura (Devil) / Homura", "A", 650, 5, "Stable", "Update 3 Event Banner Unit"),
            
            # A- Tier
            ("Enki (God) / Enkidu", "A-", 620, 3, "Stable", "Update 4 Event Unit Banner"),
            ("Kiri (Aura) / Kiritsugi Emiya", "A-", 620, 3, "Stable", "Update 4 Event Unit Banner"),
            ("Zid (Atomic) / Gid Kagenou", "A-", 600, 3, "Stable", "Update 1 Lawless City Portal Secret Evolved Unit"),
            ("Emeya (Archer) / Archer EMIYA", "A-", 560, 3, "Stable", "Update 6 Cog Portal Secret Evolved Unit"),
            ("Milim (Lord) / Milim", "A-", 550, 3, "Stable", "Update 8.5 Secret Honey Rush Evolved Unit"),
            ("Rukia (Bankai) / Rukia", "A-", 500, 5, "Stable", "Update 9 Secret Rukia Banner Evolved Unit"),
            ("Sung (Shadow Monarch) / Sung Jin-woo", "A-", 455, 3, "Stable", "Update 2 Secret Triple Banner Evolved Unit"),
            ("Satella (Witch of Jealousy) / Satella", "A-", 450, 3, "Stable", "Update 3 Secret Triple Banner Evolved Unit"),
            ("Yugi (Duel) / Yugi", "A-", 420, 3, "Stable", "Update 5.5 Battlepass Evolved Unit"),
            ("Goblin Slayer / Goblin Slayer", "A-", 400, 1, "Stable", "Update 7 Battlepass Unit"),
            ("Albedo (Charm) / Albedo", "A-", 350, 3, "Stable", "Update 8 Event Banner Unit"),
            ("Shaltean (Bloodfallen) / Shalltear", "A-", 350, 3, "Stable", "Update 8 Event Banner Unit"),
            ("Demi (Demon) / Demiurge", "A-", 350, 3, "Stable", "Update 8 Event Banner Unit"),
            ("Kafka / Kafka Hibino", "A-", 315, 3, "Stable", "Update 1 Christmas Banner Unit"),
            ("Kurume / Kirumi", "A-", 300, 3, "Stable", "Update 3 Exclusive Banner Unit"),
            ("Homura / Homura", "A-", 300, 3, "Stable", "Update 3 Exclusive Banner Unit"),
            ("Kiri / Kiritsugi Emiya", "A-", 270, 3, "Stable", "Update 4 Event Unit Banner"),
            ("Enki / Enkidu", "A-", 270, 3, "Stable", "Update 4 Event Unit Banner"),
            ("Yugi / Yugi", "A-", 255, 1, "Stable", "Update 5.5 Battlepass Unit"),
            ("Megumin (Explosion) / Megumin", "A-", 255, 3, "Stable", "Update 9.5 Part 3 Event Banner Evolved Unit"),
            ("Igris (Shadow Monarch) / Igris", "A-", 240, 3, "Stable", "Update 7 Craftable Unit"),
            ("Bero (Shadow Monarch) / Bero", "A-", 240, 3, "Stable", "Update 7 Craftable Unit"),
            ("Asha (Reincarnation) / Asha Necron", "A-", 230, 3, "Stable", "Update 9.5 Part 3 Event Banner Evolved Unit"),
            ("Vivian (Banshee) / Vivian", "A-", 230, 3, "Stable", "Update 9.5 Part 3 Event Banner Evolved Unit")
        ]
        
        for char in characters_data:
            cursor.execute("""
                INSERT INTO characters (name, tier, value, demand, trend, information)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, char)
    
    def execute_query(self, query, params=None, fetch=True):
        """Execute database query"""
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if fetch:
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    result = cursor.fetchall()
                    return pd.DataFrame(result, columns=columns)
                else:
                    return pd.DataFrame()
            else:
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Query execution error: {e}")
            conn.rollback()
            return None if fetch else False
        finally:
            conn.close()
    
    def hash_password(self, password):
        """Hash password with salt"""
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return password_hash.hex(), salt
    
    def verify_password(self, password, password_hash, salt):
        """Verify password against hash"""
        test_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return test_hash.hex() == password_hash
