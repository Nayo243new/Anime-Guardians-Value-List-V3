import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
import json

class RoleManager:
    """Advanced role and permission management system"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.logger = logging.getLogger(__name__)
        
        # Define all available permissions first
        self.ALL_PERMISSIONS = {
            # User Management
            'users.view': 'View user profiles and information',
            'users.edit': 'Edit user profiles and settings',
            'users.delete': 'Delete user accounts',
            'users.ban': 'Ban/unban users',
            'users.promote': 'Change user roles',
            
            # Trading and Economy
            'trading.basic': 'Basic trading functionality',
            'trading.advanced': 'Advanced trading features',
            'trading.admin': 'Administrative trading controls',
            'currency.grant': 'Grant virtual currency to users',
            'currency.adjust': 'Adjust user currency balances',
            
            # Characters and Tier Lists
            'characters.view': 'View character tier lists',
            'characters.edit': 'Edit character information',
            'characters.create': 'Create new characters',
            'characters.delete': 'Delete characters',
            'characters.values': 'Modify character values and tiers',
            
            # Content Moderation
            'content.moderate': 'Moderate user-generated content',
            'content.delete': 'Delete inappropriate content',
            'reports.handle': 'Handle user reports',
            'chat.moderate': 'Moderate chat and communications',
            
            # Analytics and Data
            'analytics.view': 'View analytics and statistics',
            'analytics.export': 'Export data and reports',
            'logs.view': 'View system logs',
            'logs.admin': 'Access administrative logs',
            
            # System Administration
            'system.settings': 'Modify system settings',
            'system.maintenance': 'Perform system maintenance',
            'system.backup': 'Create and manage backups',
            'database.access': 'Direct database access',
            
            # Role Management
            'roles.view': 'View roles and permissions',
            'roles.edit': 'Edit roles and permissions',
            'roles.create': 'Create new custom roles',
            'roles.delete': 'Delete custom roles',
            'roles.assign': 'Assign roles to users',
            
            # Achievements and Events
            'achievements.manage': 'Manage achievements and rewards',
            'events.create': 'Create special events',
            'events.manage': 'Manage ongoing events',
            
            # Security
            'security.audit': 'View security audit logs',
            'security.manage': 'Manage security settings',
            'ip.ban': 'Ban IP addresses',
            
            # Communication
            'notifications.send': 'Send notifications to users',
            'announcements.create': 'Create system announcements',
            'messages.admin': 'Administrative messaging'
        }
        
        # Initialize tables only - skip automatic role setup to prevent conflicts
        self.init_role_tables()

    def init_role_tables(self):
        """Initialize role management tables"""
        try:
            # Skip initialization if already done to prevent conflicts
            return
            
            # Permissions table
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS permissions (
                    permission_id SERIAL PRIMARY KEY,
                    permission_name VARCHAR(100) UNIQUE NOT NULL,
                    description TEXT,
                    category VARCHAR(50),
                    is_system BOOLEAN DEFAULT TRUE
                )
            """, fetch=False)
            
            # Role permissions mapping
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS role_permissions (
                    id SERIAL PRIMARY KEY,
                    role_id INTEGER REFERENCES roles(role_id) ON DELETE CASCADE,
                    permission_id INTEGER REFERENCES permissions(permission_id) ON DELETE CASCADE,
                    granted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    granted_by INTEGER REFERENCES users(user_id),
                    UNIQUE(role_id, permission_id)
                )
            """, fetch=False)
            
            # User roles mapping (users can have multiple roles)
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS user_roles (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                    role_id INTEGER REFERENCES roles(role_id) ON DELETE CASCADE,
                    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    assigned_by INTEGER REFERENCES users(user_id),
                    expires_at TIMESTAMP WITH TIME ZONE,
                    is_active BOOLEAN DEFAULT TRUE,
                    UNIQUE(user_id, role_id)
                )
            """, fetch=False)
            
            # Role hierarchy for inheritance
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS role_hierarchy (
                    id SERIAL PRIMARY KEY,
                    parent_role_id INTEGER REFERENCES roles(role_id) ON DELETE CASCADE,
                    child_role_id INTEGER REFERENCES roles(role_id) ON DELETE CASCADE,
                    inheritance_type VARCHAR(20) DEFAULT 'full',
                    UNIQUE(parent_role_id, child_role_id)
                )
            """, fetch=False)
            
            # Permission audit log
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS permission_audit (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id),
                    action VARCHAR(50) NOT NULL,
                    target_type VARCHAR(50),
                    target_id INTEGER,
                    permission_used VARCHAR(100),
                    success BOOLEAN,
                    ip_address INET,
                    user_agent TEXT,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    details JSONB DEFAULT '{}'
                )
            """, fetch=False)
            
            # Create indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_user_roles_role_id ON user_roles(role_id)",
                "CREATE INDEX IF NOT EXISTS idx_role_permissions_role_id ON role_permissions(role_id)",
                "CREATE INDEX IF NOT EXISTS idx_permission_audit_user_id ON permission_audit(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_permission_audit_timestamp ON permission_audit(timestamp)"
            ]
            
            for index in indexes:
                self.db.execute_query(index, fetch=False)
                
            self.logger.info("Role management tables initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize role tables: {e}")

    def _setup_default_roles(self):
        """Setup default system roles and permissions"""
        try:
            # Insert all permissions
            self._insert_permissions()
            
            # Define default roles
            default_roles = [
                {
                    'name': 'guest',
                    'display': 'Guest',
                    'description': 'Limited access for unregistered users',
                    'color': '#9E9E9E',
                    'priority': 0,
                    'permissions': ['characters.view']
                },
                {
                    'name': 'user',
                    'display': 'Regular User',
                    'description': 'Standard user with basic permissions',
                    'color': '#4CAF50',
                    'priority': 10,
                    'permissions': [
                        'characters.view', 'trading.basic', 'analytics.view'
                    ]
                },
                {
                    'name': 'premium',
                    'display': 'Premium User',
                    'description': 'Premium user with enhanced features',
                    'color': '#FF9800',
                    'priority': 20,
                    'permissions': [
                        'characters.view', 'trading.basic', 'trading.advanced',
                        'analytics.view', 'analytics.export'
                    ]
                },
                {
                    'name': 'moderator',
                    'display': 'Moderator',
                    'description': 'Content moderation and basic administrative duties',
                    'color': '#2196F3',
                    'priority': 50,
                    'permissions': [
                        'characters.view', 'characters.edit', 'trading.basic', 'trading.advanced',
                        'content.moderate', 'content.delete', 'reports.handle', 'chat.moderate',
                        'users.view', 'users.ban', 'analytics.view', 'logs.view'
                    ]
                },
                {
                    'name': 'admin',
                    'display': 'Administrator',
                    'description': 'Full administrative access',
                    'color': '#F44336',
                    'priority': 90,
                    'permissions': 'all'
                },
                {
                    'name': 'owner',
                    'display': 'Owner',
                    'description': 'System owner with ultimate authority',
                    'color': '#9C27B0',
                    'priority': 100,
                    'permissions': 'all'
                }
            ]
            
            for role_data in default_roles:
                self._create_default_role(role_data)
                
            self.logger.info("Default roles and permissions setup completed")
            
        except Exception as e:
            self.logger.error(f"Failed to setup default roles: {e}")

    def _insert_permissions(self):
        """Insert all permissions into the database"""
        try:
            # Check if permissions already exist
            result = self.db.execute_query("SELECT COUNT(*) as count FROM permissions")
            if not result.empty and result.iloc[0]['count'] > 0:
                return
            
            # Group permissions by category
            categories = {}
            for perm, desc in self.ALL_PERMISSIONS.items():
                category = perm.split('.')[0]
                if category not in categories:
                    categories[category] = []
                categories[category].append((perm, desc))
            
            # Insert permissions
            for category, perms in categories.items():
                for perm_name, description in perms:
                    self.db.execute_query("""
                        INSERT INTO permissions (permission_name, description, category)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (permission_name) DO NOTHING
                    """, (perm_name, description, category), fetch=False)
                    
        except Exception as e:
            self.logger.error(f"Failed to insert permissions: {e}")

    def _create_default_role(self, role_data):
        """Create a default role with its permissions"""
        try:
            # Insert role
            result = self.db.execute_query("""
                INSERT INTO roles (role_name, display_name, description, color, priority, is_system, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (role_name) DO NOTHING
                RETURNING role_id
            """, (
                role_data['name'],
                role_data['display'],
                role_data['description'],
                role_data['color'],
                role_data['priority'],
                True,
                1  # created_by system user
            ))
            
            if result.empty:
                # Role already exists, get its ID
                result = self.db.execute_query(
                    "SELECT role_id FROM roles WHERE role_name = %s",
                    (role_data['name'],)
                )
            
            if not result.empty:
                role_id = int(result.iloc[0]['role_id'])  # Convert numpy.int64 to Python int
                
                # Assign permissions to role
                permissions_to_assign = role_data['permissions']
                if permissions_to_assign == 'all':
                    permissions_to_assign = list(self.ALL_PERMISSIONS.keys())
                
                for perm_name in permissions_to_assign:
                    perm_result = self.db.execute_query(
                        "SELECT permission_id FROM permissions WHERE permission_name = %s",
                        (perm_name,)
                    )
                    
                    if not perm_result.empty:
                        perm_id = int(perm_result.iloc[0]['permission_id'])  # Convert numpy.int64 to Python int
                        # Check if permission assignment already exists to avoid foreign key errors
                        existing_assignment = self.db.execute_query("""
                            SELECT id FROM role_permissions 
                            WHERE role_id = %s AND permission_id = %s
                        """, (role_id, perm_id))
                        
                        if existing_assignment.empty:
                            self.db.execute_query("""
                                INSERT INTO role_permissions (role_id, permission_id, granted_by)
                                VALUES (%s, %s, %s)
                            """, (role_id, perm_id, 1), fetch=False)
                        
        except Exception as e:
            self.logger.error(f"Failed to create default role {role_data['name']}: {e}")

    def create_custom_role(self, creator_id: int, role_name: str, display_name: str, 
                          description: str, permissions: List[str], color: str = '#808080',
                          priority: int = 30) -> Dict[str, Any]:
        """Create a new custom role"""
        try:
            # Validate creator permissions
            if not self.has_permission(creator_id, 'roles.create'):
                return {'success': False, 'error': 'Insufficient permissions to create roles'}
            
            # Validate role name
            if not role_name or len(role_name) < 2:
                return {'success': False, 'error': 'Role name must be at least 2 characters'}
            
            # Check if role already exists
            existing = self.db.execute_query(
                "SELECT role_id FROM roles WHERE role_name = %s",
                (role_name,)
            )
            if not existing.empty:
                return {'success': False, 'error': 'Role name already exists'}
            
            # Validate permissions
            valid_perms = []
            for perm in permissions:
                if perm in self.ALL_PERMISSIONS:
                    valid_perms.append(perm)
            
            # Create role
            result = self.db.execute_query("""
                INSERT INTO roles (role_name, display_name, description, color, priority, is_system, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING role_id
            """, (role_name, display_name, description, color, priority, False, creator_id))
            
            if result.empty:
                return {'success': False, 'error': 'Failed to create role'}
            
            role_id = int(result.iloc[0]['role_id'])  # Convert numpy.int64 to Python int
            
            # Assign permissions
            for perm_name in valid_perms:
                perm_result = self.db.execute_query(
                    "SELECT permission_id FROM permissions WHERE permission_name = %s",
                    (perm_name,)
                )
                
                if not perm_result.empty:
                    perm_id = int(perm_result.iloc[0]['permission_id'])  # Convert numpy.int64 to Python int
                    self.db.execute_query("""
                        INSERT INTO role_permissions (role_id, permission_id, granted_by)
                        VALUES (%s, %s, %s)
                    """, (role_id, perm_id, creator_id), fetch=False)
            
            self._log_permission_action(creator_id, 'role_created', 'role', role_id, 'roles.create')
            
            return {
                'success': True,
                'role_id': role_id,
                'message': f'Custom role "{display_name}" created successfully'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create custom role: {e}")
            return {'success': False, 'error': 'Internal error creating role'}

    def assign_role_to_user(self, assigner_id: int, user_id: int, role_name: str,
                           expires_at: Optional[datetime] = None) -> Dict[str, Any]:
        """Assign a role to a user"""
        try:
            # Check permissions
            if not self.has_permission(assigner_id, 'roles.assign'):
                return {'success': False, 'error': 'Insufficient permissions to assign roles'}
            
            # Get role ID
            role_result = self.db.execute_query(
                "SELECT role_id, priority FROM roles WHERE role_name = %s AND is_active = TRUE",
                (role_name,)
            )
            
            if role_result.empty:
                return {'success': False, 'error': 'Role not found'}
            
            role_id = int(role_result.iloc[0]['role_id'])  # Convert numpy.int64 to Python int
            role_priority = int(role_result.iloc[0]['priority'])  # Convert numpy.int64 to Python int
            
            # Check if assigner can assign this role (can't assign roles higher than their own)
            assigner_max_priority = self.get_user_max_priority(assigner_id)
            if role_priority >= assigner_max_priority:
                return {'success': False, 'error': 'Cannot assign role with equal or higher priority'}
            
            # Check if user already has this role
            existing = self.db.execute_query("""
                SELECT id FROM user_roles 
                WHERE user_id = %s AND role_id = %s AND is_active = TRUE
            """, (user_id, role_id))
            
            if not existing.empty:
                return {'success': False, 'error': 'User already has this role'}
            
            # Assign role
            self.db.execute_query("""
                INSERT INTO user_roles (user_id, role_id, assigned_by, expires_at)
                VALUES (%s, %s, %s, %s)
            """, (user_id, role_id, assigner_id, expires_at), fetch=False)
            
            self._log_permission_action(assigner_id, 'role_assigned', 'user', user_id, 'roles.assign')
            
            return {'success': True, 'message': f'Role assigned successfully'}
            
        except Exception as e:
            self.logger.error(f"Failed to assign role: {e}")
            return {'success': False, 'error': 'Internal error assigning role'}

    def remove_role_from_user(self, remover_id: int, user_id: int, role_name: str) -> Dict[str, Any]:
        """Remove a role from a user"""
        try:
            # Check permissions
            if not self.has_permission(remover_id, 'roles.assign'):
                return {'success': False, 'error': 'Insufficient permissions to remove roles'}
            
            # Get role info
            role_result = self.db.execute_query("""
                SELECT r.role_id, r.priority, r.is_system
                FROM roles r
                WHERE r.role_name = %s
            """, (role_name,))
            
            if role_result.empty:
                return {'success': False, 'error': 'Role not found'}
            
            role_id = int(role_result.iloc[0]['role_id'])  # Convert numpy.int64 to Python int
            role_priority = int(role_result.iloc[0]['priority'])  # Convert numpy.int64 to Python int
            is_system = bool(role_result.iloc[0]['is_system'])  # Convert to Python bool
            
            # Prevent removal of system roles from owners
            if is_system and role_name in ['owner', 'admin']:
                remover_max_priority = self.get_user_max_priority(remover_id)
                if role_priority >= remover_max_priority:
                    return {'success': False, 'error': 'Cannot remove system role with equal or higher priority'}
            
            # Remove role
            result = self.db.execute_query("""
                UPDATE user_roles 
                SET is_active = FALSE
                WHERE user_id = %s AND role_id = %s AND is_active = TRUE
            """, (user_id, role_id), fetch=False)
            
            self._log_permission_action(remover_id, 'role_removed', 'user', user_id, 'roles.assign')
            
            return {'success': True, 'message': 'Role removed successfully'}
            
        except Exception as e:
            self.logger.error(f"Failed to remove role: {e}")
            return {'success': False, 'error': 'Internal error removing role'}

    def has_permission(self, user_id: int, permission: str) -> bool:
        """Check if user has a specific permission"""
        try:
            # Get user's active roles and their permissions
            result = self.db.execute_query("""
                SELECT DISTINCT p.permission_name
                FROM user_roles ur
                JOIN roles r ON ur.role_id = r.role_id
                JOIN role_permissions rp ON r.role_id = rp.role_id
                JOIN permissions p ON rp.permission_id = p.permission_id
                WHERE ur.user_id = %s 
                AND ur.is_active = TRUE 
                AND r.is_active = TRUE
                AND (ur.expires_at IS NULL OR ur.expires_at > CURRENT_TIMESTAMP)
            """, (user_id,))
            
            if result.empty:
                return False
            
            user_permissions = set(result['permission_name'].tolist())
            return permission in user_permissions
            
        except Exception as e:
            self.logger.error(f"Failed to check permission: {e}")
            return False

    def get_user_permissions(self, user_id: int) -> Set[str]:
        """Get all permissions for a user"""
        try:
            result = self.db.execute_query("""
                SELECT DISTINCT p.permission_name
                FROM user_roles ur
                JOIN roles r ON ur.role_id = r.role_id
                JOIN role_permissions rp ON r.role_id = rp.role_id
                JOIN permissions p ON rp.permission_id = p.permission_id
                WHERE ur.user_id = %s 
                AND ur.is_active = TRUE 
                AND r.is_active = TRUE
                AND (ur.expires_at IS NULL OR ur.expires_at > CURRENT_TIMESTAMP)
            """, (user_id,))
            
            if result.empty:
                return set()
            
            return set(result['permission_name'].tolist())
            
        except Exception as e:
            self.logger.error(f"Failed to get user permissions: {e}")
            return set()

    def get_user_roles(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all roles for a user"""
        try:
            result = self.db.execute_query("""
                SELECT r.role_name, r.display_name, r.description, r.color, r.priority,
                       ur.assigned_at, ur.expires_at, ur.is_active
                FROM user_roles ur
                JOIN roles r ON ur.role_id = r.role_id
                WHERE ur.user_id = %s
                ORDER BY r.priority DESC
            """, (user_id,))
            
            if result.empty:
                return []
            
            roles = []
            for _, row in result.iterrows():
                roles.append({
                    'name': row['role_name'],
                    'display_name': row['display_name'],
                    'description': row['description'],
                    'color': row['color'],
                    'priority': row['priority'],
                    'assigned_at': row['assigned_at'],
                    'expires_at': row['expires_at'],
                    'is_active': row['is_active']
                })
            
            return roles
            
        except Exception as e:
            self.logger.error(f"Failed to get user roles: {e}")
            return []

    def get_user_max_priority(self, user_id: int) -> int:
        """Get user's highest role priority"""
        try:
            result = self.db.execute_query("""
                SELECT MAX(r.priority) as max_priority
                FROM user_roles ur
                JOIN roles r ON ur.role_id = r.role_id
                WHERE ur.user_id = %s 
                AND ur.is_active = TRUE 
                AND r.is_active = TRUE
                AND (ur.expires_at IS NULL OR ur.expires_at > CURRENT_TIMESTAMP)
            """, (user_id,))
            
            if result.empty or result.iloc[0]['max_priority'] is None:
                return 0
            
            return int(result.iloc[0]['max_priority'])
            
        except Exception as e:
            self.logger.error(f"Failed to get user max priority: {e}")
            return 0

    def get_all_roles(self) -> List[Dict[str, Any]]:
        """Get all available roles"""
        try:
            result = self.db.execute_query("""
                SELECT role_id, role_name, display_name, description, color, priority, 
                       is_system, is_active, created_at
                FROM roles
                WHERE is_active = TRUE
                ORDER BY priority DESC
            """)
            
            if result.empty:
                return []
            
            roles = []
            for _, row in result.iterrows():
                roles.append({
                    'id': row['role_id'],
                    'name': row['role_name'],
                    'display_name': row['display_name'],
                    'description': row['description'],
                    'color': row['color'],
                    'priority': row['priority'],
                    'is_system': row['is_system'],
                    'created_at': row['created_at']
                })
            
            return roles
            
        except Exception as e:
            self.logger.error(f"Failed to get all roles: {e}")
            return []

    def get_role_permissions(self, role_name: str) -> List[str]:
        """Get all permissions for a specific role"""
        try:
            result = self.db.execute_query("""
                SELECT p.permission_name
                FROM roles r
                JOIN role_permissions rp ON r.role_id = rp.role_id
                JOIN permissions p ON rp.permission_id = p.permission_id
                WHERE r.role_name = %s AND r.is_active = TRUE
            """, (role_name,))
            
            if result.empty:
                return []
            
            return result['permission_name'].tolist()
            
        except Exception as e:
            self.logger.error(f"Failed to get role permissions: {e}")
            return []

    def _log_permission_action(self, user_id: int, action: str, target_type: str, 
                              target_id: int, permission_used: str, success: bool = True):
        """Log permission-related actions for audit trail"""
        try:
            self.db.execute_query("""
                INSERT INTO permission_audit 
                (user_id, action, target_type, target_id, permission_used, success)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, action, target_type, target_id, permission_used, success), fetch=False)
            
        except Exception as e:
            self.logger.error(f"Failed to log permission action: {e}")

    def cleanup_expired_roles(self):
        """Remove expired role assignments"""
        try:
            result = self.db.execute_query("""
                UPDATE user_roles 
                SET is_active = FALSE
                WHERE expires_at < CURRENT_TIMESTAMP AND is_active = TRUE
            """, fetch=False)
            
            self.logger.info("Expired role assignments cleaned up")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired roles: {e}")

    def get_permission_categories(self) -> Dict[str, List[Dict[str, str]]]:
        """Get permissions organized by category"""
        categories = {}
        for perm, desc in self.ALL_PERMISSIONS.items():
            category = perm.split('.')[0].title()
            if category not in categories:
                categories[category] = []
            categories[category].append({
                'name': perm,
                'description': desc
            })
        
        return categories