import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any

def show_role_management(role_manager, current_user_id: int):
    """Display role management interface for administrators"""
    
    st.title("🔐 Advanced Role & Permission Management")
    
    # Check if user has permission to access role management
    if not role_manager.has_permission(current_user_id, 'roles.view'):
        st.error("🚫 Access Denied: You don't have permission to view role management.")
        return
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 User Roles", 
        "🛡️ Role Management", 
        "⚙️ Custom Roles", 
        "📊 Permission Overview",
        "📋 Audit Log"
    ])
    
    with tab1:
        show_user_roles_tab(role_manager, current_user_id)
    
    with tab2:
        show_role_management_tab(role_manager, current_user_id)
    
    with tab3:
        show_custom_roles_tab(role_manager, current_user_id)
    
    with tab4:
        show_permission_overview_tab(role_manager, current_user_id)
    
    with tab5:
        show_audit_log_tab(role_manager, current_user_id)

def show_user_roles_tab(role_manager, current_user_id: int):
    """Show user role assignment interface"""
    st.header("👥 User Role Management")
    
    if not role_manager.has_permission(current_user_id, 'roles.assign'):
        st.warning("⚠️ You can view roles but cannot assign/remove them.")
    
    # Search for users
    col1, col2 = st.columns([2, 1])
    
    with col1:
        user_search = st.text_input("🔍 Search for user by username or email", key="user_search")
    
    with col2:
        if st.button("🔍 Search Users"):
            if user_search:
                # Search for users in database
                users_result = role_manager.db.execute_query("""
                    SELECT user_id, username, email, display_name, role
                    FROM users 
                    WHERE username ILIKE %s OR email ILIKE %s
                    ORDER BY username
                    LIMIT 20
                """, (f"%{user_search}%", f"%{user_search}%"))
                
                if not users_result.empty:
                    st.session_state['searched_users'] = users_result
                else:
                    st.info("No users found matching your search.")
    
    # Display searched users
    if 'searched_users' in st.session_state:
        st.subheader("Search Results")
        
        for _, user in st.session_state['searched_users'].iterrows():
            with st.expander(f"👤 {user['username']} ({user['email']})"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Show current roles
                    user_roles = role_manager.get_user_roles(user['user_id'])
                    
                    st.write("**Current Roles:**")
                    if user_roles:
                        for role in user_roles:
                            if role['is_active']:
                                color = role['color']
                                expires_text = ""
                                if role['expires_at']:
                                    expires_text = f" (expires: {role['expires_at'].strftime('%Y-%m-%d')})"
                                
                                st.markdown(f"""
                                <div style="
                                    background-color: {color}20; 
                                    border-left: 4px solid {color}; 
                                    padding: 8px; 
                                    margin: 4px 0;
                                    border-radius: 4px;
                                ">
                                    <strong>{role['display_name']}</strong>{expires_text}<br>
                                    <small>{role['description']}</small>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("No active roles assigned")
                
                with col2:
                    if role_manager.has_permission(current_user_id, 'roles.assign'):
                        # Role assignment form
                        available_roles = role_manager.get_all_roles()
                        role_options = [(r['name'], r['display_name']) for r in available_roles]
                        
                        selected_role = st.selectbox(
                            "Assign Role:",
                            options=[r[0] for r in role_options],
                            format_func=lambda x: next(r[1] for r in role_options if r[0] == x),
                            key=f"role_select_{user['user_id']}"
                        )
                        
                        # Optional expiration date
                        add_expiration = st.checkbox("Set expiration date", key=f"exp_check_{user['user_id']}")
                        expiration_date = None
                        
                        if add_expiration:
                            expiration_date = st.date_input(
                                "Expires on:",
                                value=datetime.now().date() + timedelta(days=30),
                                key=f"exp_date_{user['user_id']}"
                            )
                        
                        col_assign, col_remove = st.columns(2)
                        
                        with col_assign:
                            if st.button("➕ Assign", key=f"assign_{user['user_id']}"):
                                exp_datetime = datetime.combine(expiration_date, datetime.min.time()) if expiration_date else None
                                result = role_manager.assign_role_to_user(
                                    current_user_id, 
                                    user['user_id'], 
                                    selected_role,
                                    exp_datetime
                                )
                                if result['success']:
                                    st.success(result['message'])
                                    st.rerun()
                                else:
                                    st.error(result['error'])
                        
                        with col_remove:
                            if st.button("➖ Remove", key=f"remove_{user['user_id']}"):
                                result = role_manager.remove_role_from_user(
                                    current_user_id,
                                    user['user_id'],
                                    selected_role
                                )
                                if result['success']:
                                    st.success(result['message'])
                                    st.rerun()
                                else:
                                    st.error(result['error'])

def show_role_management_tab(role_manager, current_user_id: int):
    """Show existing role management"""
    st.header("🛡️ System Roles Overview")
    
    roles = role_manager.get_all_roles()
    
    if not roles:
        st.info("No roles found in the system.")
        return
    
    # Display roles in a grid
    cols_per_row = 2
    for i in range(0, len(roles), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, role in enumerate(roles[i:i+cols_per_row]):
            with cols[j]:
                # Role card
                st.markdown(f"""
                <div style="
                    border: 2px solid {role['color']};
                    border-radius: 8px;
                    padding: 16px;
                    margin: 8px 0;
                    background: linear-gradient(135deg, {role['color']}10, {role['color']}05);
                ">
                    <h4 style="color: {role['color']}; margin: 0;">
                        {role['display_name']} 
                        <span style="font-size: 0.7em; color: #666;">
                            (Priority: {role['priority']})
                        </span>
                    </h4>
                    <p style="margin: 8px 0; color: #666; font-size: 0.9em;">
                        {role['description']}
                    </p>
                    <div style="display: flex; gap: 8px; align-items: center; font-size: 0.8em;">
                        <span style="background: {'#28a745' if not role['is_system'] else '#6c757d'}; 
                                     color: white; padding: 2px 6px; border-radius: 12px;">
                            {'Custom' if not role['is_system'] else 'System'}
                        </span>
                        <span style="color: #666;">
                            Created: {role['created_at'].strftime('%Y-%m-%d') if role['created_at'] else 'N/A'}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Show permissions for this role
                if st.button(f"View Permissions", key=f"view_perms_{role['id']}"):
                    permissions = role_manager.get_role_permissions(role['name'])
                    
                    if permissions:
                        st.write(f"**Permissions for {role['display_name']}:**")
                        
                        # Group permissions by category
                        perm_categories = {}
                        for perm in permissions:
                            category = perm.split('.')[0].title()
                            if category not in perm_categories:
                                perm_categories[category] = []
                            perm_categories[category].append(perm)
                        
                        for category, perms in perm_categories.items():
                            st.write(f"**{category}:**")
                            for perm in perms:
                                st.write(f"  • {perm}")
                    else:
                        st.info("No permissions assigned to this role.")

def show_custom_roles_tab(role_manager, current_user_id: int):
    """Show custom role creation interface"""
    st.header("⚙️ Create Custom Roles")
    
    if not role_manager.has_permission(current_user_id, 'roles.create'):
        st.error("🚫 Access Denied: You don't have permission to create custom roles.")
        return
    
    with st.form("create_custom_role"):
        st.subheader("Create New Custom Role")
        
        col1, col2 = st.columns(2)
        
        with col1:
            role_name = st.text_input(
                "Role Name (lowercase, no spaces)", 
                help="Internal name for the role (e.g., 'content_creator')"
            )
            display_name = st.text_input(
                "Display Name",
                help="User-friendly name (e.g., 'Content Creator')"
            )
            description = st.text_area(
                "Description",
                help="Describe what this role is for"
            )
        
        with col2:
            color = st.color_picker("Role Color", value="#4CAF50")
            priority = st.slider(
                "Priority Level", 
                min_value=1, 
                max_value=89, 
                value=30,
                help="Higher priority roles have more authority (max 89 for custom roles)"
            )
        
        st.subheader("Select Permissions")
        
        # Get permission categories
        perm_categories = role_manager.get_permission_categories()
        selected_permissions = []
        
        # Create columns for permission categories
        num_categories = len(perm_categories)
        cols_per_row = 3
        
        for i in range(0, num_categories, cols_per_row):
            cols = st.columns(cols_per_row)
            categories_slice = list(perm_categories.items())[i:i+cols_per_row]
            
            for j, (category, permissions) in enumerate(categories_slice):
                if j < len(cols):
                    with cols[j]:
                        st.write(f"**{category}**")
                        
                        # Select all checkbox for category
                        select_all = st.checkbox(f"Select All {category}", key=f"select_all_{category}")
                        
                        for perm in permissions:
                            default_checked = select_all
                            if st.checkbox(
                                perm['description'], 
                                value=default_checked,
                                key=f"perm_{perm['name']}"
                            ):
                                selected_permissions.append(perm['name'])
        
        # Form submission
        if st.form_submit_button("🎯 Create Custom Role"):
            if not role_name or not display_name:
                st.error("Role name and display name are required.")
            elif not role_name.islower() or ' ' in role_name:
                st.error("Role name must be lowercase and contain no spaces.")
            elif not selected_permissions:
                st.error("Please select at least one permission.")
            else:
                result = role_manager.create_custom_role(
                    creator_id=current_user_id,
                    role_name=role_name,
                    display_name=display_name,
                    description=description,
                    permissions=selected_permissions,
                    color=color,
                    priority=priority
                )
                
                if result['success']:
                    st.success(f"✅ {result['message']}")
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")

def show_permission_overview_tab(role_manager, current_user_id: int):
    """Show comprehensive permission overview"""
    st.header("📊 Permission System Overview")
    
    # Permission categories overview
    perm_categories = role_manager.get_permission_categories()
    
    st.subheader("📋 Available Permissions by Category")
    
    for category, permissions in perm_categories.items():
        with st.expander(f"🔧 {category} ({len(permissions)} permissions)"):
            for perm in permissions:
                st.write(f"**{perm['name']}**")
                st.write(f"└── {perm['description']}")
                st.write("")
    
    # Role hierarchy visualization
    st.subheader("🏗️ Role Hierarchy & Priority Levels")
    
    roles = role_manager.get_all_roles()
    if roles:
        # Create a dataframe for better visualization
        role_data = []
        for role in roles:
            permissions_count = len(role_manager.get_role_permissions(role['name']))
            role_data.append({
                'Role': role['display_name'],
                'Priority': role['priority'],
                'Type': 'System' if role['is_system'] else 'Custom',
                'Permissions': permissions_count,
                'Color': role['color']
            })
        
        df = pd.DataFrame(role_data)
        df = df.sort_values('Priority', ascending=False)
        
        # Display as a styled table
        st.dataframe(
            df,
            column_config={
                "Priority": st.column_config.NumberColumn(
                    "Priority",
                    help="Higher numbers have more authority"
                ),
                "Permissions": st.column_config.NumberColumn(
                    "Permissions",
                    help="Number of permissions assigned"
                )
            },
            hide_index=True
        )
    
    # Current user's permissions
    st.subheader("🔐 Your Current Permissions")
    
    user_permissions = role_manager.get_user_permissions(current_user_id)
    user_roles = role_manager.get_user_roles(current_user_id)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Your Roles:**")
        for role in user_roles:
            if role['is_active']:
                st.markdown(f"""
                <div style="
                    background-color: {role['color']}20; 
                    border-left: 4px solid {role['color']}; 
                    padding: 8px; 
                    margin: 4px 0;
                    border-radius: 4px;
                ">
                    <strong>{role['display_name']}</strong><br>
                    <small>Priority: {role['priority']}</small>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.write(f"**Your Permissions ({len(user_permissions)}):**")
        if user_permissions:
            # Group by category
            user_perm_categories = {}
            for perm in user_permissions:
                category = perm.split('.')[0].title()
                if category not in user_perm_categories:
                    user_perm_categories[category] = []
                user_perm_categories[category].append(perm)
            
            for category, perms in user_perm_categories.items():
                st.write(f"**{category}:** {', '.join([p.split('.')[1] for p in perms])}")
        else:
            st.info("No permissions assigned")

def show_audit_log_tab(role_manager, current_user_id: int):
    """Show permission audit log"""
    st.header("📋 Permission Audit Log")
    
    if not role_manager.has_permission(current_user_id, 'logs.view'):
        st.error("🚫 Access Denied: You don't have permission to view audit logs.")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        days_back = st.selectbox(
            "Time Period",
            options=[1, 7, 30, 90],
            format_func=lambda x: f"Last {x} day{'s' if x > 1 else ''}",
            index=1
        )
    
    with col2:
        action_filter = st.selectbox(
            "Action Type",
            options=["All", "role_created", "role_assigned", "role_removed", "permission_checked"],
            index=0
        )
    
    with col3:
        if st.button("🔄 Refresh Log"):
            st.rerun()
    
    # Get audit log data
    try:
        query = """
            SELECT 
                pa.timestamp,
                u.username,
                pa.action,
                pa.target_type,
                pa.target_id,
                pa.permission_used,
                pa.success,
                pa.ip_address
            FROM permission_audit pa
            LEFT JOIN users u ON pa.user_id = u.user_id
            WHERE pa.timestamp >= CURRENT_TIMESTAMP - INTERVAL '%s days'
        """
        params = [days_back]
        
        if action_filter != "All":
            query += " AND pa.action = %s"
            params.append(action_filter)
        
        query += " ORDER BY pa.timestamp DESC LIMIT 100"
        
        audit_result = role_manager.db.execute_query(query, params)
        
        if not audit_result.empty:
            # Format the data for display
            audit_data = []
            for _, row in audit_result.iterrows():
                audit_data.append({
                    'Timestamp': row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'User': row['username'] or 'Unknown',
                    'Action': row['action'],
                    'Target': f"{row['target_type']} #{row['target_id']}" if row['target_id'] else 'N/A',
                    'Permission': row['permission_used'],
                    'Success': '✅' if row['success'] else '❌',
                    'IP Address': str(row['ip_address']) if row['ip_address'] else 'N/A'
                })
            
            # Display as dataframe
            df = pd.DataFrame(audit_data)
            st.dataframe(df, hide_index=True, use_container_width=True)
            
            # Summary statistics
            st.subheader("📊 Audit Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Actions", len(audit_data))
            
            with col2:
                success_rate = (audit_result['success'].sum() / len(audit_result)) * 100
                st.metric("Success Rate", f"{success_rate:.1f}%")
            
            with col3:
                unique_users = audit_result['username'].nunique()
                st.metric("Active Users", unique_users)
            
            with col4:
                unique_actions = audit_result['action'].nunique()
                st.metric("Action Types", unique_actions)
        else:
            st.info("No audit log entries found for the selected criteria.")
            
    except Exception as e:
        st.error(f"Failed to load audit log: {str(e)}")

def check_permission_decorator(permission_required: str):
    """Decorator to check permissions before executing functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Assuming role_manager and current_user_id are available in the context
            if 'role_manager' in st.session_state and 'current_user_id' in st.session_state:
                role_manager = st.session_state['role_manager']
                current_user_id = st.session_state['current_user_id']
                
                if role_manager.has_permission(current_user_id, permission_required):
                    return func(*args, **kwargs)
                else:
                    st.error(f"🚫 Access Denied: This action requires '{permission_required}' permission.")
                    return None
            else:
                st.error("🚫 Authentication required.")
                return None
        return wrapper
    return decorator