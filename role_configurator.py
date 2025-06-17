"""
Dynamic Role Permission Configurator with Visual Hierarchy
Advanced role management system with drag-and-drop hierarchy and granular permissions
"""

import streamlit as st
import json
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import pandas as pd


class RoleConfigurator:
    """Advanced role configuration system with visual hierarchy"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.permission_categories = self._get_permission_categories()
        self.default_permissions = self._get_default_permissions()
        self.init_role_configurator_tables()
    
    def init_role_configurator_tables(self):
        """Initialize role configurator tables"""
        try:
            # Enhanced roles table with hierarchy support
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS role_hierarchy (
                    role_id SERIAL PRIMARY KEY,
                    role_name VARCHAR(50) UNIQUE NOT NULL,
                    display_name VARCHAR(100) NOT NULL,
                    description TEXT,
                    parent_role_id INTEGER REFERENCES role_hierarchy(role_id),
                    level INTEGER DEFAULT 0,
                    color VARCHAR(7) DEFAULT '#667eea',
                    icon VARCHAR(20) DEFAULT '👤',
                    priority INTEGER DEFAULT 0,
                    is_system BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    max_users INTEGER DEFAULT NULL,
                    auto_assign BOOLEAN DEFAULT FALSE,
                    inherit_permissions BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """, fetch=False)
            
            # Enhanced permissions table with categories
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS permission_registry (
                    permission_id SERIAL PRIMARY KEY,
                    permission_key VARCHAR(100) UNIQUE NOT NULL,
                    permission_name VARCHAR(100) NOT NULL,
                    description TEXT,
                    category VARCHAR(50) NOT NULL,
                    subcategory VARCHAR(50),
                    permission_type VARCHAR(20) DEFAULT 'action',
                    resource_type VARCHAR(50),
                    scope VARCHAR(20) DEFAULT 'global',
                    danger_level INTEGER DEFAULT 1,
                    requires_approval BOOLEAN DEFAULT FALSE,
                    is_system BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """, fetch=False)
            
            # Role permissions mapping with conditions
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS role_permissions_mapping (
                    mapping_id SERIAL PRIMARY KEY,
                    role_id INTEGER NOT NULL REFERENCES role_hierarchy(role_id) ON DELETE CASCADE,
                    permission_id INTEGER NOT NULL REFERENCES permission_registry(permission_id) ON DELETE CASCADE,
                    granted BOOLEAN DEFAULT TRUE,
                    conditions JSONB DEFAULT '{}',
                    granted_by INTEGER,
                    granted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
                    UNIQUE(role_id, permission_id)
                )
            """, fetch=False)
            
            # User role assignments with context
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS user_role_assignments (
                    assignment_id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    role_id INTEGER NOT NULL REFERENCES role_hierarchy(role_id) ON DELETE CASCADE,
                    assigned_by INTEGER,
                    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP WITH TIME ZONE DEFAULT NULL,
                    is_primary BOOLEAN DEFAULT FALSE,
                    context JSONB DEFAULT '{}',
                    UNIQUE(user_id, role_id)
                )
            """, fetch=False)
            
            # Permission templates for quick setup
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS role_templates (
                    template_id SERIAL PRIMARY KEY,
                    template_name VARCHAR(50) UNIQUE NOT NULL,
                    display_name VARCHAR(100) NOT NULL,
                    description TEXT,
                    category VARCHAR(50) DEFAULT 'custom',
                    permissions JSONB NOT NULL,
                    role_config JSONB DEFAULT '{}',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """, fetch=False)
            
            # Audit log for role changes
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS role_audit_log (
                    audit_id SERIAL PRIMARY KEY,
                    action_type VARCHAR(50) NOT NULL,
                    role_id INTEGER,
                    user_id INTEGER,
                    permission_id INTEGER,
                    old_value JSONB,
                    new_value JSONB,
                    changed_by INTEGER,
                    change_reason TEXT,
                    ip_address VARCHAR(45),
                    changed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """, fetch=False)
            
            self._insert_default_permissions()
            self._insert_default_templates()
            
        except Exception as e:
            print(f"Role configurator table initialization error: {str(e)}")
    
    def _get_permission_categories(self) -> Dict[str, Dict[str, Any]]:
        """Define permission categories with metadata"""
        return {
            'user_management': {
                'name': 'User Management',
                'icon': '👥',
                'color': '#4CAF50',
                'description': 'Manage users, profiles, and accounts'
            },
            'content_management': {
                'name': 'Content Management',
                'icon': '📝',
                'color': '#2196F3',
                'description': 'Manage content, posts, and media'
            },
            'trading_operations': {
                'name': 'Trading Operations',
                'icon': '💹',
                'color': '#FF9800',
                'description': 'Trading, transactions, and market operations'
            },
            'system_administration': {
                'name': 'System Administration',
                'icon': '⚙️',
                'color': '#9C27B0',
                'description': 'System settings, maintenance, and configuration'
            },
            'security_compliance': {
                'name': 'Security & Compliance',
                'icon': '🔒',
                'color': '#F44336',
                'description': 'Security settings, audits, and compliance'
            },
            'analytics_reporting': {
                'name': 'Analytics & Reporting',
                'icon': '📊',
                'color': '#607D8B',
                'description': 'Analytics, reports, and data insights'
            },
            'communication': {
                'name': 'Communication',
                'icon': '💬',
                'color': '#795548',
                'description': 'Messaging, notifications, and announcements'
            }
        }
    
    def _get_default_permissions(self) -> List[Dict[str, Any]]:
        """Define comprehensive default permissions"""
        return [
            # User Management
            {'key': 'users.view', 'name': 'View Users', 'category': 'user_management', 'description': 'View user profiles and lists', 'danger_level': 1},
            {'key': 'users.create', 'name': 'Create Users', 'category': 'user_management', 'description': 'Create new user accounts', 'danger_level': 2},
            {'key': 'users.edit', 'name': 'Edit Users', 'category': 'user_management', 'description': 'Modify user profiles and settings', 'danger_level': 3},
            {'key': 'users.delete', 'name': 'Delete Users', 'category': 'user_management', 'description': 'Delete user accounts', 'danger_level': 4, 'requires_approval': True},
            {'key': 'users.ban', 'name': 'Ban Users', 'category': 'user_management', 'description': 'Ban or suspend users', 'danger_level': 4},
            {'key': 'users.impersonate', 'name': 'Impersonate Users', 'category': 'user_management', 'description': 'Login as another user', 'danger_level': 5, 'requires_approval': True},
            
            # Content Management
            {'key': 'content.view', 'name': 'View Content', 'category': 'content_management', 'description': 'View all content and posts', 'danger_level': 1},
            {'key': 'content.create', 'name': 'Create Content', 'category': 'content_management', 'description': 'Create new content', 'danger_level': 2},
            {'key': 'content.edit', 'name': 'Edit Content', 'category': 'content_management', 'description': 'Modify existing content', 'danger_level': 2},
            {'key': 'content.delete', 'name': 'Delete Content', 'category': 'content_management', 'description': 'Delete content permanently', 'danger_level': 3},
            {'key': 'content.moderate', 'name': 'Moderate Content', 'category': 'content_management', 'description': 'Approve, reject, or flag content', 'danger_level': 3},
            {'key': 'content.publish', 'name': 'Publish Content', 'category': 'content_management', 'description': 'Publish content publicly', 'danger_level': 2},
            
            # Trading Operations
            {'key': 'trading.view', 'name': 'View Trades', 'category': 'trading_operations', 'description': 'View trading activity and history', 'danger_level': 1},
            {'key': 'trading.execute', 'name': 'Execute Trades', 'category': 'trading_operations', 'description': 'Execute trading operations', 'danger_level': 2},
            {'key': 'trading.manage_others', 'name': 'Manage Others Trades', 'category': 'trading_operations', 'description': 'Manage other users trades', 'danger_level': 4},
            {'key': 'trading.market_admin', 'name': 'Market Administration', 'category': 'trading_operations', 'description': 'Administer market settings', 'danger_level': 4},
            {'key': 'trading.currency_admin', 'name': 'Currency Administration', 'category': 'trading_operations', 'description': 'Manage virtual currency', 'danger_level': 5},
            
            # System Administration
            {'key': 'system.view', 'name': 'View System Info', 'category': 'system_administration', 'description': 'View system information and status', 'danger_level': 2},
            {'key': 'system.configure', 'name': 'Configure System', 'category': 'system_administration', 'description': 'Modify system configuration', 'danger_level': 4},
            {'key': 'system.maintenance', 'name': 'System Maintenance', 'category': 'system_administration', 'description': 'Perform system maintenance', 'danger_level': 4},
            {'key': 'system.backup', 'name': 'System Backup', 'category': 'system_administration', 'description': 'Create and manage backups', 'danger_level': 3},
            {'key': 'database.access', 'name': 'Database Access', 'category': 'system_administration', 'description': 'Direct database access', 'danger_level': 5, 'requires_approval': True},
            
            # Security & Compliance
            {'key': 'security.audit', 'name': 'Security Audits', 'category': 'security_compliance', 'description': 'View security audit logs', 'danger_level': 3},
            {'key': 'security.manage', 'name': 'Security Management', 'category': 'security_compliance', 'description': 'Manage security settings', 'danger_level': 4},
            {'key': 'roles.view', 'name': 'View Roles', 'category': 'security_compliance', 'description': 'View roles and permissions', 'danger_level': 2},
            {'key': 'roles.edit', 'name': 'Edit Roles', 'category': 'security_compliance', 'description': 'Modify roles and permissions', 'danger_level': 4},
            {'key': 'roles.create', 'name': 'Create Roles', 'category': 'security_compliance', 'description': 'Create new roles', 'danger_level': 4},
            {'key': 'roles.assign', 'name': 'Assign Roles', 'category': 'security_compliance', 'description': 'Assign roles to users', 'danger_level': 3},
            
            # Analytics & Reporting
            {'key': 'analytics.view', 'name': 'View Analytics', 'category': 'analytics_reporting', 'description': 'View analytics and reports', 'danger_level': 2},
            {'key': 'analytics.export', 'name': 'Export Analytics', 'category': 'analytics_reporting', 'description': 'Export analytics data', 'danger_level': 2},
            {'key': 'reports.generate', 'name': 'Generate Reports', 'category': 'analytics_reporting', 'description': 'Generate custom reports', 'danger_level': 2},
            {'key': 'reports.schedule', 'name': 'Schedule Reports', 'category': 'analytics_reporting', 'description': 'Schedule automated reports', 'danger_level': 3},
            
            # Communication
            {'key': 'notifications.send', 'name': 'Send Notifications', 'category': 'communication', 'description': 'Send notifications to users', 'danger_level': 2},
            {'key': 'announcements.create', 'name': 'Create Announcements', 'category': 'communication', 'description': 'Create system announcements', 'danger_level': 3},
            {'key': 'messages.admin', 'name': 'Administrative Messaging', 'category': 'communication', 'description': 'Send administrative messages', 'danger_level': 3},
            {'key': 'communication.moderate', 'name': 'Moderate Communication', 'category': 'communication', 'description': 'Moderate messages and communications', 'danger_level': 3}
        ]
    
    def _insert_default_permissions(self):
        """Insert default permissions into database"""
        for perm in self.default_permissions:
            try:
                self.db.execute_query("""
                    INSERT INTO permission_registry 
                    (permission_key, permission_name, description, category, danger_level, requires_approval)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (permission_key) DO NOTHING
                """, (
                    perm['key'], perm['name'], perm['description'], 
                    perm['category'], perm['danger_level'], 
                    perm.get('requires_approval', False)
                ), fetch=False)
            except Exception:
                pass
    
    def _insert_default_templates(self):
        """Insert default role templates"""
        templates = [
            {
                'name': 'admin_full',
                'display_name': 'Full Administrator',
                'description': 'Complete system access with all permissions',
                'category': 'system',
                'permissions': [p['key'] for p in self.default_permissions],
                'config': {'color': '#F44336', 'icon': '👑', 'level': 0}
            },
            {
                'name': 'moderator',
                'display_name': 'Content Moderator',
                'description': 'Content and user moderation capabilities',
                'category': 'moderation',
                'permissions': [
                    'users.view', 'users.ban', 'content.view', 'content.moderate',
                    'content.delete', 'trading.view', 'analytics.view'
                ],
                'config': {'color': '#FF9800', 'icon': '🛡️', 'level': 2}
            },
            {
                'name': 'trader_advanced',
                'display_name': 'Advanced Trader',
                'description': 'Enhanced trading capabilities and market access',
                'category': 'trading',
                'permissions': [
                    'trading.view', 'trading.execute', 'analytics.view',
                    'content.view', 'content.create'
                ],
                'config': {'color': '#4CAF50', 'icon': '💼', 'level': 3}
            },
            {
                'name': 'support_agent',
                'display_name': 'Support Agent',
                'description': 'Customer support and basic user management',
                'category': 'support',
                'permissions': [
                    'users.view', 'users.edit', 'content.view', 'trading.view',
                    'notifications.send', 'messages.admin'
                ],
                'config': {'color': '#2196F3', 'icon': '🎧', 'level': 4}
            }
        ]
        
        for template in templates:
            try:
                self.db.execute_query("""
                    INSERT INTO role_templates 
                    (template_name, display_name, description, category, permissions, role_config)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (template_name) DO NOTHING
                """, (
                    template['name'], template['display_name'], template['description'],
                    template['category'], json.dumps(template['permissions']),
                    json.dumps(template['config'])
                ), fetch=False)
            except Exception:
                pass
    
    def get_role_hierarchy(self) -> List[Dict[str, Any]]:
        """Get complete role hierarchy with relationships"""
        try:
            result = self.db.execute_query("""
                WITH RECURSIVE role_tree AS (
                    -- Base case: top-level roles
                    SELECT 
                        role_id, role_name, display_name, description,
                        parent_role_id, level, color, icon, priority,
                        is_system, is_active, max_users, auto_assign,
                        inherit_permissions, created_at,
                        ARRAY[role_id] as path,
                        role_name as root_role
                    FROM role_hierarchy 
                    WHERE parent_role_id IS NULL
                    
                    UNION ALL
                    
                    -- Recursive case: child roles
                    SELECT 
                        rh.role_id, rh.role_name, rh.display_name, rh.description,
                        rh.parent_role_id, rh.level, rh.color, rh.icon, rh.priority,
                        rh.is_system, rh.is_active, rh.max_users, rh.auto_assign,
                        rh.inherit_permissions, rh.created_at,
                        rt.path || rh.role_id,
                        rt.root_role
                    FROM role_hierarchy rh
                    JOIN role_tree rt ON rh.parent_role_id = rt.role_id
                )
                SELECT * FROM role_tree
                ORDER BY path
            """)
            
            if result is not None and hasattr(result, 'empty'):
                if not result.empty:
                    return result.to_dict('records')
            elif result:
                return [dict(zip([
                    'role_id', 'role_name', 'display_name', 'description',
                    'parent_role_id', 'level', 'color', 'icon', 'priority',
                    'is_system', 'is_active', 'max_users', 'auto_assign',
                    'inherit_permissions', 'created_at', 'path', 'root_role'
                ], row)) for row in result]
            
            return []
            
        except Exception as e:
            print(f"Error getting role hierarchy: {str(e)}")
            return []
    
    def get_permissions_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all permissions organized by category"""
        try:
            result = self.db.execute_query("""
                SELECT permission_id, permission_key, permission_name, description,
                       category, subcategory, permission_type, resource_type,
                       scope, danger_level, requires_approval, is_system
                FROM permission_registry
                ORDER BY category, danger_level, permission_name
            """)
            
            permissions_by_category = {}
            
            if result is not None:
                if hasattr(result, 'empty') and not result.empty:
                    records = result.to_dict('records')
                elif isinstance(result, list):
                    records = [dict(zip([
                        'permission_id', 'permission_key', 'permission_name', 'description',
                        'category', 'subcategory', 'permission_type', 'resource_type',
                        'scope', 'danger_level', 'requires_approval', 'is_system'
                    ], row)) for row in result]
                else:
                    records = []
                
                for perm in records:
                    category = perm['category']
                    if category not in permissions_by_category:
                        permissions_by_category[category] = []
                    permissions_by_category[category].append(perm)
            
            return permissions_by_category
            
        except Exception as e:
            print(f"Error getting permissions: {str(e)}")
            return {}
    
    def get_role_permissions(self, role_id: int) -> Set[str]:
        """Get all permissions for a role including inherited ones"""
        try:
            result = self.db.execute_query("""
                WITH RECURSIVE role_inheritance AS (
                    -- Base case: the role itself
                    SELECT role_id, parent_role_id, inherit_permissions
                    FROM role_hierarchy 
                    WHERE role_id = %s
                    
                    UNION ALL
                    
                    -- Recursive case: parent roles if inheritance is enabled
                    SELECT rh.role_id, rh.parent_role_id, rh.inherit_permissions
                    FROM role_hierarchy rh
                    JOIN role_inheritance ri ON rh.role_id = ri.parent_role_id
                    WHERE ri.inherit_permissions = TRUE
                )
                SELECT DISTINCT pr.permission_key
                FROM role_inheritance ri
                JOIN role_permissions_mapping rpm ON ri.role_id = rpm.role_id
                JOIN permission_registry pr ON rpm.permission_id = pr.permission_id
                WHERE rpm.granted = TRUE
                AND (rpm.expires_at IS NULL OR rpm.expires_at > CURRENT_TIMESTAMP)
            """, (role_id,))
            
            if result is not None:
                if hasattr(result, 'empty') and not result.empty:
                    return set(result['permission_key'].tolist())
                elif isinstance(result, list):
                    return set(row[0] for row in result)
            
            return set()
            
        except Exception as e:
            print(f"Error getting role permissions: {str(e)}")
            return set()
    
    def create_role(self, role_data: Dict[str, Any]) -> Optional[int]:
        """Create a new role with specified configuration"""
        try:
            result = self.db.execute_query("""
                INSERT INTO role_hierarchy 
                (role_name, display_name, description, parent_role_id, level, 
                 color, icon, priority, max_users, auto_assign, inherit_permissions, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING role_id
            """, (
                role_data['role_name'], role_data['display_name'], role_data.get('description', ''),
                role_data.get('parent_role_id'), role_data.get('level', 0),
                role_data.get('color', '#667eea'), role_data.get('icon', '👤'),
                role_data.get('priority', 0), role_data.get('max_users'),
                role_data.get('auto_assign', False), role_data.get('inherit_permissions', True),
                role_data.get('created_by')
            ))
            
            if result and len(result) > 0:
                role_id = result[0][0] if isinstance(result[0], (list, tuple)) else result[0]['role_id']
                
                # Log the creation
                self._log_role_action('create_role', role_id, role_data.get('created_by'), 
                                    change_reason=f"Created role: {role_data['display_name']}")
                
                return role_id
            
            return None
            
        except Exception as e:
            print(f"Error creating role: {str(e)}")
            return None
    
    def assign_permissions_to_role(self, role_id: int, permission_keys: List[str], 
                                 assigned_by: Optional[int] = None) -> bool:
        """Assign multiple permissions to a role"""
        try:
            # Get permission IDs
            placeholders = ','.join(['%s'] * len(permission_keys))
            result = self.db.execute_query(f"""
                SELECT permission_id, permission_key
                FROM permission_registry
                WHERE permission_key IN ({placeholders})
            """, permission_keys)
            
            if not result:
                return False
            
            permission_mapping = {}
            if hasattr(result, 'empty') and not result.empty:
                for _, row in result.iterrows():
                    permission_mapping[row['permission_key']] = row['permission_id']
            elif isinstance(result, list):
                for row in result:
                    permission_mapping[row[1]] = row[0]
            
            # Assign permissions
            for perm_key in permission_keys:
                if perm_key in permission_mapping:
                    self.db.execute_query("""
                        INSERT INTO role_permissions_mapping 
                        (role_id, permission_id, granted_by)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (role_id, permission_id) 
                        DO UPDATE SET granted = TRUE, granted_by = EXCLUDED.granted_by
                    """, (role_id, permission_mapping[perm_key], assigned_by), fetch=False)
            
            # Log the assignment
            self._log_role_action('assign_permissions', role_id, assigned_by,
                                new_value={'permissions': permission_keys},
                                change_reason=f"Assigned {len(permission_keys)} permissions")
            
            return True
            
        except Exception as e:
            print(f"Error assigning permissions: {str(e)}")
            return False
    
    def get_role_templates(self) -> List[Dict[str, Any]]:
        """Get available role templates"""
        try:
            result = self.db.execute_query("""
                SELECT template_id, template_name, display_name, description, 
                       category, permissions, role_config, created_at
                FROM role_templates
                ORDER BY category, display_name
            """)
            
            if result is not None:
                if hasattr(result, 'empty') and not result.empty:
                    templates = result.to_dict('records')
                elif isinstance(result, list):
                    templates = [dict(zip([
                        'template_id', 'template_name', 'display_name', 'description',
                        'category', 'permissions', 'role_config', 'created_at'
                    ], row)) for row in result]
                else:
                    return []
                
                # Parse JSON fields
                for template in templates:
                    try:
                        template['permissions'] = json.loads(template['permissions']) if isinstance(template['permissions'], str) else template['permissions']
                        template['role_config'] = json.loads(template['role_config']) if isinstance(template['role_config'], str) else template['role_config']
                    except (json.JSONDecodeError, TypeError):
                        template['permissions'] = []
                        template['role_config'] = {}
                
                return templates
            
            return []
            
        except Exception as e:
            print(f"Error getting role templates: {str(e)}")
            return []
    
    def apply_role_template(self, template_name: str, role_name: str, 
                          display_name: str, created_by: Optional[int] = None) -> Optional[int]:
        """Create a role from a template"""
        try:
            # Get template
            result = self.db.execute_query("""
                SELECT permissions, role_config
                FROM role_templates
                WHERE template_name = %s
            """, (template_name,))
            
            if not result:
                return None
            
            template_data = result[0] if isinstance(result, list) else result.iloc[0]
            permissions = json.loads(template_data[0]) if isinstance(template_data[0], str) else template_data[0]
            role_config = json.loads(template_data[1]) if isinstance(template_data[1], str) else template_data[1]
            
            # Create role with template configuration
            role_data = {
                'role_name': role_name,
                'display_name': display_name,
                'created_by': created_by,
                **role_config
            }
            
            role_id = self.create_role(role_data)
            
            if role_id and permissions:
                self.assign_permissions_to_role(role_id, permissions, created_by)
            
            return role_id
            
        except Exception as e:
            print(f"Error applying role template: {str(e)}")
            return None
    
    def update_role_hierarchy(self, role_id: int, new_parent_id: Optional[int], 
                            updated_by: Optional[int] = None) -> bool:
        """Update role hierarchy by changing parent"""
        try:
            # Check for circular dependency
            if new_parent_id and self._would_create_cycle(role_id, new_parent_id):
                return False
            
            # Get old parent for logging
            old_result = self.db.execute_query("""
                SELECT parent_role_id FROM role_hierarchy WHERE role_id = %s
            """, (role_id,))
            
            old_parent = old_result[0][0] if old_result else None
            
            # Update parent
            self.db.execute_query("""
                UPDATE role_hierarchy 
                SET parent_role_id = %s, updated_at = CURRENT_TIMESTAMP
                WHERE role_id = %s
            """, (new_parent_id, role_id), fetch=False)
            
            # Update levels for all affected roles
            self._update_role_levels()
            
            # Log the change
            self._log_role_action('update_hierarchy', role_id, updated_by,
                                old_value={'parent_role_id': old_parent},
                                new_value={'parent_role_id': new_parent_id},
                                change_reason="Updated role hierarchy")
            
            return True
            
        except Exception as e:
            print(f"Error updating role hierarchy: {str(e)}")
            return False
    
    def _would_create_cycle(self, role_id: int, new_parent_id: int) -> bool:
        """Check if setting new parent would create a circular dependency"""
        try:
            result = self.db.execute_query("""
                WITH RECURSIVE parent_chain AS (
                    SELECT role_id, parent_role_id, 1 as depth
                    FROM role_hierarchy 
                    WHERE role_id = %s
                    
                    UNION ALL
                    
                    SELECT rh.role_id, rh.parent_role_id, pc.depth + 1
                    FROM role_hierarchy rh
                    JOIN parent_chain pc ON rh.role_id = pc.parent_role_id
                    WHERE pc.depth < 10  -- Prevent infinite recursion
                )
                SELECT role_id FROM parent_chain WHERE role_id = %s
            """, (new_parent_id, role_id))
            
            return result is not None and len(result) > 0
            
        except Exception:
            return True  # Assume cycle to be safe
    
    def _update_role_levels(self):
        """Update level field for all roles based on hierarchy depth"""
        try:
            self.db.execute_query("""
                WITH RECURSIVE role_levels AS (
                    -- Top level roles
                    SELECT role_id, 0 as new_level
                    FROM role_hierarchy 
                    WHERE parent_role_id IS NULL
                    
                    UNION ALL
                    
                    -- Child roles
                    SELECT rh.role_id, rl.new_level + 1
                    FROM role_hierarchy rh
                    JOIN role_levels rl ON rh.parent_role_id = rl.role_id
                )
                UPDATE role_hierarchy 
                SET level = role_levels.new_level
                FROM role_levels
                WHERE role_hierarchy.role_id = role_levels.role_id
            """, fetch=False)
            
        except Exception as e:
            print(f"Error updating role levels: {str(e)}")
    
    def _log_role_action(self, action_type: str, role_id: Optional[int], 
                        changed_by: Optional[int], old_value: Optional[Dict] = None,
                        new_value: Optional[Dict] = None, change_reason: Optional[str] = None):
        """Log role management actions for audit trail"""
        try:
            self.db.execute_query("""
                INSERT INTO role_audit_log 
                (action_type, role_id, changed_by, old_value, new_value, change_reason)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                action_type, role_id, changed_by,
                json.dumps(old_value) if old_value else None,
                json.dumps(new_value) if new_value else None,
                change_reason
            ), fetch=False)
            
        except Exception:
            pass  # Don't fail operations due to logging issues
    
    def get_role_statistics(self) -> Dict[str, Any]:
        """Get comprehensive role statistics"""
        try:
            stats = {}
            
            # Basic counts
            result = self.db.execute_query("""
                SELECT 
                    COUNT(*) as total_roles,
                    COUNT(*) FILTER (WHERE is_active = TRUE) as active_roles,
                    COUNT(*) FILTER (WHERE is_system = TRUE) as system_roles,
                    COUNT(DISTINCT parent_role_id) FILTER (WHERE parent_role_id IS NOT NULL) as roles_with_children
                FROM role_hierarchy
            """)
            
            if result:
                row = result[0] if isinstance(result, list) else result.iloc[0]
                stats.update({
                    'total_roles': row[0] if isinstance(row, (list, tuple)) else row['total_roles'],
                    'active_roles': row[1] if isinstance(row, (list, tuple)) else row['active_roles'],
                    'system_roles': row[2] if isinstance(row, (list, tuple)) else row['system_roles'],
                    'roles_with_children': row[3] if isinstance(row, (list, tuple)) else row['roles_with_children']
                })
            
            # Permission statistics
            perm_result = self.db.execute_query("""
                SELECT 
                    COUNT(*) as total_permissions,
                    COUNT(DISTINCT category) as permission_categories,
                    COUNT(*) FILTER (WHERE requires_approval = TRUE) as high_risk_permissions
                FROM permission_registry
            """)
            
            if perm_result:
                row = perm_result[0] if isinstance(perm_result, list) else perm_result.iloc[0]
                stats.update({
                    'total_permissions': row[0] if isinstance(row, (list, tuple)) else row['total_permissions'],
                    'permission_categories': row[1] if isinstance(row, (list, tuple)) else row['permission_categories'],
                    'high_risk_permissions': row[2] if isinstance(row, (list, tuple)) else row['high_risk_permissions']
                })
            
            return stats
            
        except Exception as e:
            print(f"Error getting role statistics: {str(e)}")
            return {}