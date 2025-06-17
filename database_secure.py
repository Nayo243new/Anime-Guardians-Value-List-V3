import os
import psycopg2
import psycopg2.pool
import pandas as pd
from datetime import datetime, timedelta
import hashlib
import secrets
import time
import logging
from contextlib import contextmanager
import threading
from typing import Optional, Dict, Any, List, Tuple
import re

class SecureDatabaseManager:
    """Secure database manager with protection against data leaks and SQL injection"""
    
    def __init__(self):
        self.connection_params = {
            'host': os.getenv('PGHOST'),
            'database': os.getenv('PGDATABASE'),
            'user': os.getenv('PGUSER'),
            'password': os.getenv('PGPASSWORD'),
            'port': os.getenv('PGPORT', 5432)
        }
        
        # Security configuration
        self.max_query_time = 30  # Maximum query execution time in seconds
        self.max_result_rows = 10000  # Maximum rows to return
        self.allowed_tables = {
            'users', 'characters', 'portfolios', 'trades', 'achievements',
            'user_achievements', 'notifications', 'price_alerts', 'friends',
            'posts', 'likes', 'followers', 'trading_groups', 'group_members',
            'user_themes', 'profile_customizations', 'user_analytics', 'market_data'
        }
        
        # Setup secure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize connection pool
        self.connection_pool = None
        self._pool_lock = threading.Lock()
        self._init_secure_connection_pool()
        
        # Initialize database with error handling
        self._safe_init_database()
    
    def _init_secure_connection_pool(self):
        """Initialize secure connection pool with proper error handling"""
        try:
            with self._pool_lock:
                if self.connection_pool is None:
                    self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
                        minconn=1,
                        maxconn=10,  # Reduced max connections for security
                        **self.connection_params
                    )
                    self.logger.info("Secure database connection pool initialized")
        except Exception as e:
            self.logger.error("Failed to initialize connection pool")
            self.connection_pool = None
    
    @contextmanager
    def get_secure_connection(self):
        """Get secure database connection with proper cleanup"""
        conn = None
        try:
            if self.connection_pool:
                conn = self.connection_pool.getconn()
                conn.autocommit = False  # Ensure transactions
                yield conn
            else:
                conn = psycopg2.connect(**self.connection_params)
                conn.autocommit = False
                yield conn
        except Exception as e:
            self.logger.error("Database connection error occurred")
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise DatabaseSecurityError("Database connection failed")
        finally:
            if conn:
                try:
                    if self.connection_pool:
                        self.connection_pool.putconn(conn)
                    else:
                        conn.close()
                except:
                    pass
    
    def _validate_query(self, query: str) -> bool:
        """Validate query for security threats"""
        if not query or not isinstance(query, str):
            return False
        
        # Convert to lowercase for checking
        query_lower = query.lower().strip()
        
        # Block dangerous SQL operations
        dangerous_keywords = [
            'drop', 'delete', 'truncate', 'alter', 'create', 'grant', 
            'revoke', 'exec', 'execute', 'xp_', 'sp_', 'bulk', 'shutdown',
            'information_schema', 'pg_', 'sys.', 'master.', 'msdb.',
            'union', 'concat', 'char', 'ascii', 'hex'
        ]
        
        for keyword in dangerous_keywords:
            if keyword in query_lower:
                self.logger.warning(f"Blocked dangerous keyword: {keyword}")
                return False
        
        # Check for SQL injection patterns
        injection_patterns = [
            r"['\";].*['\";]",  # Quote injection
            r"--.*",  # Comment injection
            r"/\*.*\*/",  # Block comment injection
            r"\bunion\b.*\bselect\b",  # Union select
            r"\bor\b.*[=<>].*['\"]",  # OR injection
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, query_lower):
                self.logger.warning("Blocked potential SQL injection")
                return False
        
        return True
    
    def _validate_table_access(self, query: str) -> bool:
        """Validate that query only accesses allowed tables"""
        query_lower = query.lower()
        
        # Extract table names from query
        table_patterns = [
            r'\bfrom\s+(\w+)',
            r'\bjoin\s+(\w+)',
            r'\binto\s+(\w+)',
            r'\bupdate\s+(\w+)',
        ]
        
        for pattern in table_patterns:
            matches = re.findall(pattern, query_lower)
            for table in matches:
                if table not in self.allowed_tables:
                    self.logger.warning(f"Blocked access to unauthorized table: {table}")
                    return False
        
        return True
    
    def execute_secure_query(self, query: str, params: Optional[Tuple] = None, 
                           fetch: bool = True, user_id: Optional[int] = None) -> pd.DataFrame:
        """Execute query with comprehensive security checks"""
        
        # Security validations
        if not self._validate_query(query):
            raise DatabaseSecurityError("Query blocked by security validation")
        
        if not self._validate_table_access(query):
            raise DatabaseSecurityError("Unauthorized table access blocked")
        
        # Sanitize parameters
        if params:
            params = self._sanitize_params(params)
        
        try:
            with self.get_secure_connection() as conn:
                cursor = conn.cursor()
                
                # Set query timeout
                cursor.execute("SET statement_timeout = %s", (self.max_query_time * 1000,))
                
                start_time = time.time()
                cursor.execute(query, params)
                execution_time = time.time() - start_time
                
                # Log query execution (without sensitive data)
                self.logger.info(f"Query executed in {execution_time:.3f}s")
                
                if fetch:
                    # Limit result size
                    results = cursor.fetchmany(self.max_result_rows)
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    
                    if results:
                        df = pd.DataFrame(results, columns=columns)
                        # Filter sensitive columns for non-admin users
                        if user_id and not self._is_admin_user(user_id):
                            df = self._filter_sensitive_columns(df)
                        return df
                    else:
                        return pd.DataFrame()
                else:
                    conn.commit()
                    return pd.DataFrame()
                    
        except psycopg2.Error as e:
            self.logger.error("Database error occurred")
            raise DatabaseSecurityError("Database operation failed")
        except Exception as e:
            self.logger.error("Unexpected error occurred")
            raise DatabaseSecurityError("Operation failed")
    
    def _sanitize_params(self, params: Tuple) -> Tuple:
        """Sanitize query parameters"""
        sanitized = []
        for param in params:
            if isinstance(param, str):
                # Remove potentially dangerous characters
                param = re.sub(r'[^\w\s@.-]', '', param)
                param = param[:255]  # Limit length
            elif isinstance(param, (int, float)):
                # Validate numeric ranges
                if isinstance(param, int) and abs(param) > 2147483647:
                    param = 0
                elif isinstance(param, float) and abs(param) > 1e10:
                    param = 0.0
            sanitized.append(param)
        return tuple(sanitized)
    
    def _is_admin_user(self, user_id: int) -> bool:
        """Check if user has admin privileges"""
        try:
            with self.get_secure_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT role FROM users WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
                return result and result[0] == 'Admin'
        except:
            return False
    
    def _filter_sensitive_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter out sensitive columns for non-admin users"""
        sensitive_columns = [
            'password_hash', 'salt', 'email', 'last_login', 'ip_address',
            'session_token', 'api_key', 'phone_number'
        ]
        
        columns_to_keep = [col for col in df.columns if col not in sensitive_columns]
        return df[columns_to_keep] if columns_to_keep else df
    
    def _safe_init_database(self):
        """Safely initialize database with error handling"""
        try:
            # Only create essential tables with minimal structure
            essential_tables = {
                'users': '''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        salt VARCHAR(255) NOT NULL,
                        role VARCHAR(20) DEFAULT 'Regular',
                        virtual_currency DECIMAL(15,2) DEFAULT 10000.00,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                ''',
                'characters': '''
                    CREATE TABLE IF NOT EXISTS characters (
                        character_id SERIAL PRIMARY KEY,
                        name VARCHAR(100) UNIQUE NOT NULL,
                        tier VARCHAR(1) NOT NULL CHECK (tier IN ('S', 'A', 'B', 'C', 'D')),
                        value DECIMAL(15,2) NOT NULL DEFAULT 0,
                        demand VARCHAR(20) DEFAULT 'Medium',
                        trend VARCHAR(20) DEFAULT 'Stable',
                        information TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE
                    )
                '''
            }
            
            with self.get_secure_connection() as conn:
                cursor = conn.cursor()
                for table_name, table_sql in essential_tables.items():
                    cursor.execute(table_sql)
                conn.commit()
                
            self.logger.info("Database initialized successfully")
            
        except Exception as e:
            self.logger.error("Database initialization failed")
    
    def hash_password_secure(self, password: str) -> Tuple[str, str]:
        """Secure password hashing with salt"""
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return password_hash.hex(), salt
    
    def verify_password_secure(self, password: str, stored_hash: str, salt: str) -> bool:
        """Secure password verification"""
        try:
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return password_hash.hex() == stored_hash
        except:
            return False
    
    def get_user_data_secure(self, user_id: int, requesting_user_id: int) -> Optional[Dict]:
        """Get user data with access control"""
        if user_id != requesting_user_id and not self._is_admin_user(requesting_user_id):
            # Return limited public data only
            query = "SELECT user_id, username, role, created_at FROM users WHERE user_id = %s AND is_active = TRUE"
        else:
            # Return full data for own profile or admin
            query = "SELECT user_id, username, email, role, virtual_currency, created_at, last_login FROM users WHERE user_id = %s AND is_active = TRUE"
        
        df = self.execute_secure_query(query, (user_id,), user_id=requesting_user_id)
        return df.iloc[0].to_dict() if not df.empty else None
    
    def create_user_secure(self, username: str, email: str, password: str) -> bool:
        """Create user with security validations"""
        # Validate input
        if not username or not email or not password:
            return False
        
        if len(username) < 3 or len(username) > 50:
            return False
        
        if len(password) < 8:
            return False
        
        # Check email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False
        
        try:
            password_hash, salt = self.hash_password_secure(password)
            
            query = """
                INSERT INTO users (username, email, password_hash, salt)
                VALUES (%s, %s, %s, %s)
            """
            
            self.execute_secure_query(query, (username, email, password_hash, salt), fetch=False)
            return True
            
        except:
            return False
    
    def close_pool(self):
        """Safely close connection pool"""
        try:
            if self.connection_pool:
                self.connection_pool.closeall()
                self.logger.info("Connection pool closed")
        except:
            pass

class DatabaseSecurityError(Exception):
    """Custom exception for database security violations"""
    pass