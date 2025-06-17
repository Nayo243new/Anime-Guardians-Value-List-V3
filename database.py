import os
import psycopg2
from psycopg2 import pool
import pandas as pd
import bcrypt
import secrets
import time
import re
import logging
import json
from typing import Optional, Dict, Any, List, Tuple

class DatabaseSecurityError(Exception):
    """Custom exception for database security violations"""
    pass

class DatabaseManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.connection_params = {
            'host': os.getenv('PGHOST'),
            'port': os.getenv('PGPORT'),
            'database': os.getenv('PGDATABASE'),
            'user': os.getenv('PGUSER'),
            'password': os.getenv('PGPASSWORD'),
            'sslmode': 'prefer'
        }
        
        # Security settings
        self.max_query_time = 30  # seconds
        self.max_result_rows = 10000
        
        self.connection_pool = None
        self._init_connection_pool()
        self.init_database()

    def _init_connection_pool(self):
        """Initialize connection pool for better performance"""
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 20, **self.connection_params
            )
            self.logger.info("Database connection pool initialized")
        except Exception as e:
            self.logger.error(f"Failed to create connection pool: {e}")

    def get_connection(self):
        """Get database connection from pool with context manager"""
        if self.connection_pool:
            return self.connection_pool.getconn()
        return None

    def get_direct_connection(self):
        """Get direct database connection (legacy method)"""
        try:
            if self.connection_pool:
                return self.connection_pool.getconn()
            else:
                return psycopg2.connect(**self.connection_params)
        except Exception as e:
            self.logger.error(f"Database connection error: {e}")
            return None

    def return_connection(self, conn):
        """Return connection to pool"""
        if self.connection_pool and conn:
            self.connection_pool.putconn(conn)

    def init_database(self):
        """Initialize database tables with robust error handling"""
        max_retries = 3
        
        for attempt in range(max_retries):
            conn = None
            try:
                conn = self.get_direct_connection()
                if not conn:
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    return False
                
                cursor = conn.cursor()
                
                # Create all tables
                self._create_users_table(cursor)
                self._create_characters_table(cursor)
                self._create_portfolios_table(cursor)
                self._create_trades_table(cursor)
                self._create_achievements_table(cursor)
                self._create_analytics_tables(cursor)
                self._create_sessions_table(cursor)
                self._create_notifications_table(cursor)
                
                conn.commit()
                
                # Insert initial data if needed
                cursor.execute("SELECT COUNT(*) FROM characters")
                if cursor.fetchone()[0] == 0:
                    self.insert_initial_characters(cursor)
                    conn.commit()
                
                return True
                
            except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
                self.logger.error(f"Database connection error (attempt {attempt + 1}): {str(e)}")
                if conn:
                    try:
                        conn.close()
                    except:
                        pass
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                else:
                    self.logger.error("Failed to initialize database after all retries")
                    return False
                    
            except Exception as e:
                self.logger.error(f"Database initialization error: {e}")
                if conn:
                    try:
                        conn.rollback()
                        conn.close()
                    except:
                        pass
                return False
            finally:
                if conn:
                    try:
                        self.return_connection(conn)
                    except:
                        pass
        
        return False

    def _create_users_table(self, cursor):
        """Create users table and indexes"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL CHECK (LENGTH(username) >= 3),
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                salt VARCHAR(255) NOT NULL,
                role VARCHAR(20) DEFAULT 'Regular',
                virtual_currency BIGINT DEFAULT 10000,
                display_name VARCHAR(100),
                bio TEXT,
                profile_photo TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP WITH TIME ZONE,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                login_attempts INTEGER DEFAULT 0,
                last_failed_login TIMESTAMP WITH TIME ZONE,
                account_locked_until TIMESTAMP WITH TIME ZONE
            )
        """)
        
        # Create indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)"
        ]
        for index in indexes:
            cursor.execute(index)

    def _create_characters_table(self, cursor):
        """Create characters table and indexes"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS characters (
                character_id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                tier VARCHAR(5) NOT NULL,
                value BIGINT NOT NULL DEFAULT 0,
                demand INTEGER NOT NULL DEFAULT 5,
                trend VARCHAR(20) NOT NULL DEFAULT 'Stable',
                information TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                price_history JSONB DEFAULT '[]',
                last_traded TIMESTAMP WITH TIME ZONE,
                trade_volume_24h INTEGER DEFAULT 0
            )
        """)
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_characters_name ON characters(name)",
            "CREATE INDEX IF NOT EXISTS idx_characters_tier ON characters(tier)",
            "CREATE INDEX IF NOT EXISTS idx_characters_value ON characters(value)"
        ]
        for index in indexes:
            cursor.execute(index)

    def _create_portfolios_table(self, cursor):
        """Create portfolios table"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolios (
                portfolio_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                character_id INTEGER NOT NULL REFERENCES characters(character_id) ON DELETE CASCADE,
                quantity INTEGER NOT NULL DEFAULT 0,
                total_invested DECIMAL(15,2) DEFAULT 0,
                market_conditions JSONB DEFAULT '{}',
                UNIQUE(user_id, character_id)
            )
        """)

    def _create_trades_table(self, cursor):
        """Create trades table"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                trade_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                character_id INTEGER NOT NULL REFERENCES characters(character_id),
                trade_type VARCHAR(10) NOT NULL,
                quantity INTEGER NOT NULL,
                price_per_unit DECIMAL(15,2) NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                trade_session_id UUID DEFAULT gen_random_uuid()
            )
        """)

    def _create_achievements_table(self, cursor):
        """Create achievements table"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_achievements (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                achievement_id VARCHAR(50) NOT NULL,
                earned_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                progress JSONB DEFAULT '{}',
                rarity VARCHAR(20) DEFAULT 'Common',
                points INTEGER DEFAULT 0,
                UNIQUE(user_id, achievement_id)
            )
        """)

    def _create_analytics_tables(self, cursor):
        """Create analytics and market tables"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_analytics (
                id SERIAL PRIMARY KEY,
                character_id INTEGER REFERENCES characters(character_id),
                price DECIMAL(15,2) NOT NULL,
                volume INTEGER DEFAULT 0,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def _create_sessions_table(self, cursor):
        """Create user sessions table"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                ip_address INET,
                user_agent TEXT,
                login_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                logout_time TIMESTAMP WITH TIME ZONE,
                is_active BOOLEAN DEFAULT TRUE,
                session_data JSONB DEFAULT '{}'
            )
        """)

    def _create_notifications_table(self, cursor):
        """Create notifications table"""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                notification_type VARCHAR(50) DEFAULT 'SYSTEM',
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def _validate_query(self, query: str) -> bool:
        """Validate query for security threats"""
        if not query or not isinstance(query, str):
            return False
        
        query_lower = query.lower().strip()
        
        # Allow legitimate database operations
        allowed_operations = [
            'create table', 'create index', 'insert into', 'select',
            'update', 'set statement_timeout', 'alter table add column',
            'comment on'
        ]
        
        for operation in allowed_operations:
            if query_lower.startswith(operation):
                return True
        
        # Block dangerous operations
        dangerous_keywords = [
            'drop table', 'drop database', 'truncate', 'grant all', 
            'revoke all', 'exec', 'execute', 'shutdown'
        ]
        
        for keyword in dangerous_keywords:
            if keyword in query_lower:
                self.logger.warning(f"Blocked dangerous operation: {keyword}")
                return False
        
        return True

    def _sanitize_params(self, params):
        """Sanitize query parameters while preserving JSON"""
        if not params:
            return params
            
        sanitized = []
        for param in params:
            if isinstance(param, str):
                # Don't sanitize JSON strings
                if (param.startswith('{') and param.endswith('}')) or \
                   (param.startswith('[') and param.endswith(']')):
                    sanitized.append(param)
                else:
                    # Regular string sanitization
                    param = re.sub(r'[^\w\s@.-]', '', param)
                    param = param[:255]
                    sanitized.append(param)
            else:
                sanitized.append(param)
        return tuple(sanitized) if isinstance(params, tuple) else sanitized

    def execute_query(self, query, params=None, fetch=True):
        """Execute database query with security validation"""
        if not self._validate_query(query):
            self.logger.error("Query blocked by security validation")
            return pd.DataFrame() if fetch else False
        
        if params:
            params = self._sanitize_params(params)
        
        conn = self.get_direct_connection()
        if not conn:
            return pd.DataFrame() if fetch else False
        
        try:
            cursor = conn.cursor()
            cursor.execute("SET statement_timeout = %s", (self.max_query_time * 1000,))
            cursor.execute(query, params)
            
            if fetch:
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    result = cursor.fetchmany(self.max_result_rows)
                    
                    if result:
                        df = pd.DataFrame(result, columns=columns)
                        return df
                    else:
                        return pd.DataFrame(columns=columns)
                else:
                    return pd.DataFrame()
            else:
                conn.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Database operation failed: {str(e)}")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return pd.DataFrame() if fetch else False
        finally:
            self.return_connection(conn)

    def insert_initial_characters(self, cursor):
        """Insert initial character data"""
        characters_data = [
            ("Test Character S+", "S+", 50000, 3, "Overpriced", "Test character for S+ tier"),
            ("Test Character S", "S", 25000, 5, "Stable", "Test character for S tier"),
            ("Test Character A+", "A+", 12000, 7, "Rising", "Test character for A+ tier"),
            ("Test Character A", "A", 8000, 8, "Stable", "Test character for A tier"),
            ("Test Character B+", "B+", 5000, 9, "Falling", "Test character for B+ tier"),
        ]
        
        for char in characters_data:
            cursor.execute("""
                INSERT INTO characters (name, tier, value, demand, trend, information)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (name) DO NOTHING
            """, char)

    def hash_password(self, password):
        """Hash password with salt"""
        salt = secrets.token_hex(32)
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return password_hash, salt

    def verify_password(self, password, password_hash, salt):
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except:
            return False

    def setup_default_admin_user(self):
        """Set up default admin user with proper password"""
        try:
            # Check if admin user exists
            check_query = "SELECT user_id FROM users WHERE username = %s"
            result = self.execute_query(check_query, ('Nayo',))
            
            if not result.empty:
                # Update existing user with proper password hash
                password_hash, salt = self.hash_password('password')
                update_query = """
                    UPDATE users 
                    SET password_hash = %s, salt = %s, role = 'Admin', is_active = TRUE
                    WHERE username = %s
                """
                self.execute_query(update_query, (password_hash, salt, 'Nayo'), fetch=False)
                print("Default admin user 'Nayo' password updated successfully")
            else:
                # Create new admin user
                password_hash, salt = self.hash_password('password')
                insert_query = """
                    INSERT INTO users (username, email, password_hash, salt, role, virtual_currency, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                self.execute_query(insert_query, (
                    'Nayo', 
                    'putraramdoninayotama@gmail.com', 
                    password_hash, 
                    salt, 
                    'Admin', 
                    10000, 
                    True
                ), fetch=False)
                print("Default admin user 'Nayo' created successfully")
                
        except Exception as e:
            print(f"Error setting up admin user: {e}")

    def setup_placeholder_test_user(self):
        """Set up a placeholder test user account"""
        try:
            # Check if test user already exists
            check_query = "SELECT user_id FROM users WHERE username = %s"
            result = self.execute_query(check_query, ('testuser',))
            
            if result is not None and len(result) > 0:
                # Update existing test user
                password_hash, salt = self.hash_password('test123')
                update_query = """
                    UPDATE users 
                    SET password_hash = %s, salt = %s, email = %s, role = 'Tester', 
                        virtual_currency = %s, is_active = TRUE
                    WHERE username = %s
                """
                self.execute_query(update_query, (
                    password_hash, 
                    salt, 
                    'tester@example.com',
                    10000,
                    'testuser'
                ), fetch=False)
                print("Tester user 'testuser' updated successfully")
            else:
                # Create new test user
                password_hash, salt = self.hash_password('test123')
                insert_query = """
                    INSERT INTO users (username, email, password_hash, salt, role, virtual_currency, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                self.execute_query(insert_query, (
                    'testuser', 
                    'tester@example.com', 
                    password_hash, 
                    salt, 
                    'Tester', 
                    10000, 
                    True
                ), fetch=False)
                print("Tester user 'testuser' created successfully")
                
        except Exception as e:
            print(f"Error setting up test user: {e}")

    def migrate_database_schema(self):
        """Handle database schema migrations"""
        migrations = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS login_attempts INTEGER DEFAULT 0",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_failed_login TIMESTAMP WITH TIME ZONE",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS account_locked_until TIMESTAMP WITH TIME ZONE",
            "ALTER TABLE characters ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE",
            "ALTER TABLE characters ADD COLUMN IF NOT EXISTS price_history JSONB DEFAULT '[]'",
            "ALTER TABLE characters ADD COLUMN IF NOT EXISTS last_traded TIMESTAMP WITH TIME ZONE",
            "ALTER TABLE characters ADD COLUMN IF NOT EXISTS trade_volume_24h INTEGER DEFAULT 0",
            "ALTER TABLE portfolios ADD COLUMN IF NOT EXISTS total_invested DECIMAL(15,2) DEFAULT 0",
            "ALTER TABLE portfolios ADD COLUMN IF NOT EXISTS market_conditions JSONB DEFAULT '{}'",
            "ALTER TABLE trades ADD COLUMN IF NOT EXISTS trade_session_id UUID DEFAULT gen_random_uuid()",
            "ALTER TABLE user_achievements ADD COLUMN IF NOT EXISTS rarity VARCHAR(20) DEFAULT 'Common'",
            "ALTER TABLE user_achievements ADD COLUMN IF NOT EXISTS points INTEGER DEFAULT 0",
        ]
        
        for migration in migrations:
            try:
                result = self.execute_query(migration, fetch=False)
                if result:
                    migration_name = migration.split()[-3] if "ADD COLUMN" in migration else "migration"
                    self.logger.info(f"Migration executed: {migration_name}")
            except Exception as e:
                self.logger.error(f"Migration failed: {e}")
        
        # Set up default admin user after migrations
        self.setup_default_admin_user()
        self.setup_placeholder_test_user()