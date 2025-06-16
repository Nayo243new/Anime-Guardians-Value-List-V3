import streamlit as st
from datetime import datetime
import base64

class AuthManager:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def register(self, username, email, password):
        """Register new user"""
        # Check if username or email exists
        existing = self.db.execute_query("""
            SELECT username, email FROM users 
            WHERE username = %s OR email = %s
        """, (username, email))
        
        if not existing.empty:
            return False
        
        # Hash password
        password_hash, salt = self.db.hash_password(password)
        
        # Insert user
        success = self.db.execute_query("""
            INSERT INTO users (username, email, password_hash, salt, display_name)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, email, password_hash, salt, username), fetch=False)
        
        return success
    
    def login(self, username, password):
        """Login user"""
        user_data = self.db.execute_query("""
            SELECT user_id, username, password_hash, salt, role, virtual_currency, display_name
            FROM users WHERE username = %s
        """, (username,))
        
        if user_data.empty:
            return False
        
        user = user_data.iloc[0]
        
        # Verify password
        if self.db.verify_password(password, user['password_hash'], user['salt']):
            # Update last login
            self.db.execute_query("""
                UPDATE users SET last_login = CURRENT_TIMESTAMP
                WHERE user_id = %s
            """, (user['user_id'],), fetch=False)
            
            # Set session state
            st.session_state.authenticated = True
            st.session_state.user_id = user['user_id']
            st.session_state.username = user['username']
            st.session_state.user_role = user['role']
            st.session_state.virtual_currency = user['virtual_currency']
            
            return True
        
        return False
    
    def logout(self):
        """Logout user"""
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.user_role = None
        st.session_state.virtual_currency = 0
    
    def get_user_profile(self, user_id):
        """Get user profile data"""
        profile = self.db.execute_query("""
            SELECT username, email, display_name, bio, profile_photo, created_at, role
            FROM users WHERE user_id = %s
        """, (user_id,))
        
        if profile is not None and not profile.empty:
            return profile.iloc[0].to_dict()
        return {}
    
    def update_profile(self, user_id, display_name, bio):
        """Update user profile"""
        return self.db.execute_query("""
            UPDATE users SET display_name = %s, bio = %s
            WHERE user_id = %s
        """, (display_name, bio, user_id), fetch=False)
    
    def update_profile_photo(self, user_id, photo_data):
        """Update user profile photo"""
        return self.db.execute_query("""
            UPDATE users SET profile_photo = %s
            WHERE user_id = %s
        """, (photo_data, user_id), fetch=False)
    
    def change_password(self, user_id, current_password, new_password):
        """Change user password"""
        # Get current password hash
        user_data = self.db.execute_query("""
            SELECT password_hash, salt FROM users WHERE user_id = %s
        """, (user_id,))
        
        if user_data.empty:
            return False
        
        user = user_data.iloc[0]
        
        # Verify current password
        if not self.db.verify_password(current_password, user['password_hash'], user['salt']):
            return False
        
        # Hash new password
        new_password_hash, new_salt = self.db.hash_password(new_password)
        
        # Update password
        return self.db.execute_query("""
            UPDATE users SET password_hash = %s, salt = %s
            WHERE user_id = %s
        """, (new_password_hash, new_salt, user_id), fetch=False)
    
    def update_virtual_currency(self, user_id, amount):
        """Update user virtual currency"""
        success = self.db.execute_query("""
            UPDATE users SET virtual_currency = %s
            WHERE user_id = %s
        """, (amount, user_id), fetch=False)
        
        if success:
            st.session_state.virtual_currency = amount
        
        return success
