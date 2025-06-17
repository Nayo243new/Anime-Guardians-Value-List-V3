import streamlit as st
import re
import logging
from typing import Optional, Dict, Any
from database import DatabaseManager, DatabaseSecurityError

class SecureAuthManager:
    """Secure authentication manager with protection against common vulnerabilities"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
        
        # Security configuration
        self.max_login_attempts = 5
        self.lockout_duration = 300  # 5 minutes in seconds
        self.min_password_length = 8
        self.session_timeout = 3600  # 1 hour
        
    def _validate_username(self, username: str) -> bool:
        """Validate username format and security"""
        if not username or not isinstance(username, str):
            return False
        
        # Length check
        if len(username) < 3 or len(username) > 50:
            return False
        
        # Character validation (alphanumeric + underscore)
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False
        
        # Prevent reserved usernames
        reserved_names = ['admin', 'root', 'system', 'test', 'guest', 'null', 'undefined']
        if username.lower() in reserved_names:
            return False
        
        return True
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        if not email or not isinstance(email, str):
            return False
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email)) and len(email) <= 100
    
    def _validate_password(self, password: str) -> tuple[bool, str]:
        """Validate password strength"""
        if not password or not isinstance(password, str):
            return False, "Password is required"
        
        if len(password) < self.min_password_length:
            return False, f"Password must be at least {self.min_password_length} characters"
        
        if len(password) > 128:
            return False, "Password too long"
        
        # Check for at least one uppercase, lowercase, and number
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        # Check for common weak passwords
        weak_passwords = ['password', '12345678', 'qwerty123', 'admin123']
        if password.lower() in weak_passwords:
            return False, "Password is too common"
        
        return True, ""
    
    def _check_rate_limiting(self, username: str) -> bool:
        """Check if user is rate limited due to failed attempts"""
        try:
            query = """
                SELECT login_attempts, last_failed_login 
                FROM users 
                WHERE username = %s
            """
            result = self.db.execute_query(query, (username,))
            
            if result.empty:
                return True  # User doesn't exist, allow attempt
            
            attempts = result.iloc[0]['login_attempts'] or 0
            last_failed = result.iloc[0]['last_failed_login']
            
            if attempts >= self.max_login_attempts and last_failed:
                # Check if lockout period has expired
                import datetime
                now = datetime.datetime.now()
                time_diff = (now - last_failed).total_seconds()
                
                if time_diff < self.lockout_duration:
                    return False  # Still locked out
                else:
                    # Reset attempts after lockout period
                    self._reset_login_attempts(username)
            
            return True
            
        except Exception:
            self.logger.error("Rate limiting check failed")
            return False
    
    def _increment_failed_attempts(self, username: str):
        """Increment failed login attempts"""
        try:
            query = """
                UPDATE users 
                SET login_attempts = COALESCE(login_attempts, 0) + 1,
                    last_failed_login = CURRENT_TIMESTAMP
                WHERE username = %s
            """
            self.db.execute_query(query, (username,), fetch=False)
        except Exception:
            self.logger.error("Failed to increment login attempts")
    
    def _reset_login_attempts(self, username: str):
        """Reset failed login attempts"""
        try:
            query = """
                UPDATE users 
                SET login_attempts = 0, 
                    last_failed_login = NULL 
                WHERE username = %s
            """
            self.db.execute_query(query, (username,), fetch=False)
        except Exception:
            self.logger.error("Failed to reset login attempts")
    
    def register(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """Secure user registration with comprehensive validation"""
        
        # Input validation
        if not self._validate_username(username):
            return {"success": False, "message": "Invalid username format"}
        
        if not self._validate_email(email):
            return {"success": False, "message": "Invalid email format"}
        
        password_valid, password_message = self._validate_password(password)
        if not password_valid:
            return {"success": False, "message": password_message}
        
        try:
            # Check if username or email already exists
            check_query = """
                SELECT username, email 
                FROM users 
                WHERE username = %s OR email = %s
            """
            existing = self.db.execute_query(check_query, (username, email))
            
            if not existing.empty:
                if existing.iloc[0]['username'] == username:
                    return {"success": False, "message": "Username already exists"}
                else:
                    return {"success": False, "message": "Email already registered"}
            
            # Hash password securely
            password_hash, salt = self.db.hash_password(password)
            
            # Create user account
            insert_query = """
                INSERT INTO users (username, email, password_hash, salt, created_at)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                RETURNING user_id
            """
            
            result = self.db.execute_query(
                insert_query, 
                (username, email, password_hash, salt),
                fetch=True
            )
            
            if not result.empty:
                self.logger.info(f"New user registered: {username}")
                return {
                    "success": True, 
                    "message": "Account created successfully",
                    "user_id": result.iloc[0]['user_id']
                }
            else:
                return {"success": False, "message": "Failed to create account"}
                
        except DatabaseSecurityError:
            return {"success": False, "message": "Security validation failed"}
        except Exception:
            self.logger.error("Registration failed")
            return {"success": False, "message": "Registration failed"}
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Secure user login with rate limiting and session management"""
        
        # Input validation
        if not username or not password:
            return {"success": False, "message": "Username and password required"}
        
        # Check rate limiting
        if not self._check_rate_limiting(username):
            return {
                "success": False, 
                "message": f"Account locked. Try again in {self.lockout_duration // 60} minutes"
            }
        
        try:
            # Get user data
            query = """
                SELECT user_id, username, password_hash, salt, role, 
                       virtual_currency, display_name, is_active
                FROM users 
                WHERE username = %s AND is_active = TRUE
            """
            user_data = self.db.execute_query(query, (username,))
            
            if user_data.empty:
                self._increment_failed_attempts(username)
                return {"success": False, "message": "Invalid credentials"}
            
            user = user_data.iloc[0]
            
            # Verify password
            if self.db.verify_password(password, user['password_hash'], user['salt']):
                # Reset failed attempts on successful login
                self._reset_login_attempts(username)
                
                # Update last login
                update_query = """
                    UPDATE users 
                    SET last_login = CURRENT_TIMESTAMP 
                    WHERE user_id = %s
                """
                self.db.execute_query(update_query, (user['user_id'],), fetch=False)
                
                # Set secure session state
                self._set_session_state(user)
                
                self.logger.info(f"User logged in: {username}")
                
                return {
                    "success": True,
                    "message": "Login successful",
                    "user_data": {
                        "user_id": user['user_id'],
                        "username": user['username'],
                        "role": user['role'],
                        "virtual_currency": user['virtual_currency'],
                        "display_name": user['display_name']
                    }
                }
            else:
                self._increment_failed_attempts(username)
                return {"success": False, "message": "Invalid credentials"}
                
        except DatabaseSecurityError:
            return {"success": False, "message": "Security validation failed"}
        except Exception:
            self.logger.error("Login failed")
            return {"success": False, "message": "Login failed"}
    
    def _set_session_state(self, user_data):
        """Set secure session state"""
        st.session_state.authenticated = True
        st.session_state.user_id = user_data['user_id']
        st.session_state.username = user_data['username']
        st.session_state.user_role = user_data['role']
        st.session_state.virtual_currency = float(user_data['virtual_currency'] or 0)
        st.session_state.display_name = user_data['display_name'] or user_data['username']
        
        # Set session timeout
        import time
        st.session_state.session_start = time.time()
    
    def logout(self):
        """Secure logout with session cleanup"""
        try:
            # Clear all session data
            session_keys = [
                'authenticated', 'user_id', 'username', 'user_role',
                'virtual_currency', 'display_name', 'session_start'
            ]
            
            for key in session_keys:
                if key in st.session_state:
                    del st.session_state[key]
            
            self.logger.info("User logged out")
            
        except Exception:
            self.logger.error("Logout failed")
    
    def is_session_valid(self) -> bool:
        """Check if current session is valid and not expired"""
        if not st.session_state.get('authenticated', False):
            return False
        
        # Check session timeout
        session_start = st.session_state.get('session_start', 0)
        import time
        
        if time.time() - session_start > self.session_timeout:
            self.logout()
            return False
        
        return True
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user data"""
        if not self.is_session_valid():
            return None
        
        return {
            "user_id": st.session_state.get('user_id'),
            "username": st.session_state.get('username'),
            "role": st.session_state.get('user_role'),
            "virtual_currency": st.session_state.get('virtual_currency'),
            "display_name": st.session_state.get('display_name')
        }
    
    def is_admin(self) -> bool:
        """Check if current user has admin privileges"""
        user = self.get_current_user()
        return user and user.get('role') == 'Admin'
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> Dict[str, Any]:
        """Secure password change with validation"""
        
        # Validate new password
        password_valid, password_message = self._validate_password(new_password)
        if not password_valid:
            return {"success": False, "message": password_message}
        
        try:
            # Verify current password
            query = """
                SELECT password_hash, salt 
                FROM users 
                WHERE user_id = %s AND is_active = TRUE
            """
            user_data = self.db.execute_query(query, (user_id,))
            
            if user_data.empty:
                return {"success": False, "message": "User not found"}
            
            user = user_data.iloc[0]
            
            if not self.db.verify_password(current_password, user['password_hash'], user['salt']):
                return {"success": False, "message": "Current password is incorrect"}
            
            # Hash new password
            new_password_hash, new_salt = self.db.hash_password(new_password)
            
            # Update password
            update_query = """
                UPDATE users 
                SET password_hash = %s, salt = %s, 
                    login_attempts = 0, last_failed_login = NULL
                WHERE user_id = %s
            """
            
            success = self.db.execute_query(
                update_query, 
                (new_password_hash, new_salt, user_id),
                fetch=False
            )
            
            if success:
                self.logger.info(f"Password changed for user {user_id}")
                return {"success": True, "message": "Password changed successfully"}
            else:
                return {"success": False, "message": "Failed to update password"}
                
        except Exception:
            self.logger.error("Password change failed")
            return {"success": False, "message": "Password change failed"}