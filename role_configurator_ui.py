"""
Visual Interface for Dynamic Role Permission Configurator
Interactive UI with drag-and-drop hierarchy and permission matrix
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import json
from typing import Dict, List, Any, Optional


def render_role_hierarchy_visualization(role_configurator, roles_data: List[Dict]) -> None:
    """Render interactive role hierarchy visualization"""
    if not roles_data:
        st.info("No roles configured yet. Create your first role below.")
        return
    
    # Create hierarchy tree visualization
    fig = go.Figure()
    
    # Prepare data for tree layout
    node_ids = []
    node_labels = []
    node_parents = []
    node_colors = []
    node_sizes = []
    node_info = []
    
    for role in roles_data:
        node_ids.append(f"role_{role['role_id']}")
        node_labels.append(f"{role.get('icon', '👤')} {role['display_name']}")
        
        parent_id = f"role_{role['parent_role_id']}" if role['parent_role_id'] else ""
        node_parents.append(parent_id)
        
        node_colors.append(role.get('color', '#667eea'))
        node_sizes.append(max(30 - role.get('level', 0) * 5, 15))
        
        # Get role permissions count
        permissions = role_configurator.get_role_permissions(role['role_id'])
        node_info.append(f"Level: {role.get('level', 0)}<br>Permissions: {len(permissions)}<br>Active: {'Yes' if role.get('is_active', True) else 'No'}")
    
    # Create treemap for hierarchy visualization
    if len(roles_data) > 1:
        fig = go.Figure(go.Treemap(
            ids=node_ids,
            labels=node_labels,
            parents=node_parents,
            values=[1] * len(node_ids),  # Equal size for all nodes
            text=node_info,
            textinfo="label+text",
            hovertemplate='<b>%{label}</b><br>%{text}<extra></extra>',
            marker=dict(
                colors=node_colors,
                line=dict(width=2, color='white')
            )
        ))
        
        fig.update_layout(
            title="Role Hierarchy Structure",
            font_size=12,
            height=400,
            margin=dict(t=50, l=25, r=25, b=25)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Alternative: Network graph for complex hierarchies
    if len(roles_data) > 5:
        with st.expander("🌐 Network View"):
            render_role_network_graph(roles_data)


def render_role_network_graph(roles_data: List[Dict]) -> None:
    """Render network graph for role relationships"""
    # Create network graph
    fig = go.Figure()
    
    # Nodes
    node_trace = go.Scatter(
        x=[], y=[], mode='markers+text',
        marker=dict(size=[], color=[], line=dict(width=2, color='white')),
        text=[], textposition="middle center",
        hoverinfo='text', hovertext=[]
    )
    
    # Edges
    edge_trace = go.Scatter(
        x=[], y=[], mode='lines',
        line=dict(width=2, color='rgba(128,128,128,0.5)'),
        hoverinfo='none'
    )
    
    # Calculate positions (simple circular layout)
    import math
    n = len(roles_data)
    for i, role in enumerate(roles_data):
        angle = 2 * math.pi * i / n
        x = math.cos(angle)
        y = math.sin(angle)
        
        node_trace['x'] += (x,)
        node_trace['y'] += (y,)
        node_trace['text'] += (f"{role.get('icon', '👤')}<br>{role['display_name'][:10]}",)
        node_trace['marker']['size'] += (max(40 - role.get('level', 0) * 8, 20),)
        node_trace['marker']['color'] += (role.get('color', '#667eea'),)
        node_trace['hovertext'] += (f"Role: {role['display_name']}<br>Level: {role.get('level', 0)}",)
        
        # Add edges to parent
        if role['parent_role_id']:
            for j, parent_role in enumerate(roles_data):
                if parent_role['role_id'] == role['parent_role_id']:
                    parent_angle = 2 * math.pi * j / n
                    parent_x = math.cos(parent_angle)
                    parent_y = math.sin(parent_angle)
                    
                    edge_trace['x'] += (x, parent_x, None)
                    edge_trace['y'] += (y, parent_y, None)
                    break
    
    fig.add_trace(edge_trace)
    fig.add_trace(node_trace)
    
    fig.update_layout(
        title="Role Relationship Network",
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20,l=5,r=5,t=40),
        annotations=[
            dict(text="Interactive role hierarchy network", 
                 showarrow=False, xref="paper", yref="paper",
                 x=0.005, y=-0.002, xanchor='left', yanchor='bottom',
                 font=dict(color='gray', size=12))
        ],
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_permission_matrix(role_configurator, roles_data: List[Dict], permissions_by_category: Dict) -> None:
    """Render interactive permission matrix"""
    if not roles_data or not permissions_by_category:
        st.info("No roles or permissions available for matrix view.")
        return
    
    st.markdown("### 🎯 Permission Matrix")
    
    # Create matrix data
    matrix_data = []
    role_names = [role['display_name'] for role in roles_data]
    
    for category, permissions in permissions_by_category.items():
        category_info = role_configurator.permission_categories.get(category, {})
        
        with st.expander(f"{category_info.get('icon', '🔧')} {category_info.get('name', category.title())}"):
            # Create permission matrix for this category
            perm_matrix = []
            perm_labels = []
            
            for perm in permissions:
                perm_row = []
                perm_labels.append(f"{perm['permission_name']}")
                
                for role in roles_data:
                    role_permissions = role_configurator.get_role_permissions(role['role_id'])
                    has_permission = perm['permission_key'] in role_permissions
                    perm_row.append(1 if has_permission else 0)
                
                perm_matrix.append(perm_row)
            
            if perm_matrix:
                # Create heatmap
                fig = go.Figure(data=go.Heatmap(
                    z=perm_matrix,
                    x=role_names,
                    y=perm_labels,
                    colorscale=[[0, '#ffebee'], [1, '#4caf50']],
                    showscale=False,
                    hovertemplate='<b>%{y}</b><br>Role: %{x}<br>Access: %{customdata}<extra></extra>',
                    customdata=[['Granted' if val else 'Denied' for val in row] for row in perm_matrix]
                ))
                
                fig.update_layout(
                    title=f"{category_info.get('name', category.title())} Permissions",
                    height=max(200, len(perm_labels) * 25),
                    margin=dict(l=250, r=50, t=50, b=50)
                )
                
                st.plotly_chart(fig, use_container_width=True)


def render_role_creation_interface(role_configurator) -> None:
    """Render role creation and editing interface"""
    st.markdown("### ➕ Create New Role")
    
    with st.form("create_role_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            role_name = st.text_input("Role Name (unique)", placeholder="e.g., content_manager")
            display_name = st.text_input("Display Name", placeholder="e.g., Content Manager")
            description = st.text_area("Description", placeholder="Describe this role's purpose...")
            
        with col2:
            # Get existing roles for parent selection
            roles_data = role_configurator.get_role_hierarchy()
            parent_options = ["None"] + [f"{role['display_name']} (Level {role.get('level', 0)})" for role in roles_data]
            parent_role = st.selectbox("Parent Role", parent_options)
            
            color = st.color_picker("Role Color", value="#667eea")
            icon = st.text_input("Icon (emoji)", value="👤", max_chars=2)
            priority = st.number_input("Priority", min_value=0, max_value=100, value=0)
        
        col3, col4 = st.columns(2)
        
        with col3:
            max_users = st.number_input("Max Users (0 = unlimited)", min_value=0, value=0)
            auto_assign = st.checkbox("Auto-assign to new users")
            
        with col4:
            inherit_permissions = st.checkbox("Inherit parent permissions", value=True)
            is_active = st.checkbox("Active", value=True)
        
        # Permission selection
        st.markdown("#### Select Permissions")
        permissions_by_category = role_configurator.get_permissions_by_category()
        selected_permissions = []
        
        for category, permissions in permissions_by_category.items():
            category_info = role_configurator.permission_categories.get(category, {})
            
            with st.expander(f"{category_info.get('icon', '🔧')} {category_info.get('name', category.title())}"):
                for perm in permissions:
                    danger_level = perm.get('danger_level', 1)
                    danger_color = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴", 5: "⚫"}
                    
                    col_perm1, col_perm2 = st.columns([3, 1])
                    
                    with col_perm1:
                        if st.checkbox(
                            f"{perm['permission_name']}", 
                            key=f"perm_{perm['permission_key']}",
                            help=perm.get('description', '')
                        ):
                            selected_permissions.append(perm['permission_key'])
                    
                    with col_perm2:
                        st.markdown(f"{danger_color.get(danger_level, '⚪')} Level {danger_level}")
        
        # Template quick selection
        st.markdown("#### 🎯 Or use a template")
        templates = role_configurator.get_role_templates()
        template_options = ["None"] + [f"{t['display_name']} - {t['description']}" for t in templates]
        selected_template = st.selectbox("Role Template", template_options)
        
        submitted = st.form_submit_button("Create Role", type="primary")
        
        if submitted:
            if not role_name or not display_name:
                st.error("Role name and display name are required.")
                return
            
            # Determine parent role ID
            parent_role_id = None
            if parent_role != "None":
                for role in roles_data:
                    if f"{role['display_name']} (Level {role.get('level', 0)})" == parent_role:
                        parent_role_id = role['role_id']
                        break
            
            # Create role data
            role_data = {
                'role_name': role_name,
                'display_name': display_name,
                'description': description,
                'parent_role_id': parent_role_id,
                'color': color,
                'icon': icon,
                'priority': priority,
                'max_users': max_users if max_users > 0 else None,
                'auto_assign': auto_assign,
                'inherit_permissions': inherit_permissions,
                'is_active': is_active,
                'created_by': st.session_state.get('user_id')
            }
            
            # Handle template application
            if selected_template != "None" and templates:
                template_name = templates[template_options.index(selected_template) - 1]['template_name']
                role_id = role_configurator.apply_role_template(template_name, role_name, display_name, st.session_state.get('user_id'))
                
                if role_id:
                    st.success(f"Role '{display_name}' created successfully from template!")
                    st.rerun()
                else:
                    st.error("Failed to create role from template.")
            else:
                # Create role manually
                role_id = role_configurator.create_role(role_data)
                
                if role_id:
                    # Assign selected permissions
                    if selected_permissions:
                        role_configurator.assign_permissions_to_role(role_id, selected_permissions, st.session_state.get('user_id'))
                    
                    st.success(f"Role '{display_name}' created successfully!")
                    st.rerun()
                else:
                    st.error("Failed to create role. Role name might already exist.")


def render_role_management_dashboard(role_configurator) -> None:
    """Render comprehensive role management dashboard"""
    st.markdown("### 📊 Role Management Dashboard")
    
    # Get statistics
    stats = role_configurator.get_role_statistics()
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Roles", stats.get('total_roles', 0))
    
    with col2:
        st.metric("Active Roles", stats.get('active_roles', 0))
    
    with col3:
        st.metric("Permission Categories", stats.get('permission_categories', 0))
    
    with col4:
        st.metric("Total Permissions", stats.get('total_permissions', 0))
    
    # Role distribution chart
    roles_data = role_configurator.get_role_hierarchy()
    
    if roles_data:
        # Level distribution
        level_counts = {}
        for role in roles_data:
            level = role.get('level', 0)
            level_counts[f"Level {level}"] = level_counts.get(f"Level {level}", 0) + 1
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_levels = px.pie(
                values=list(level_counts.values()),
                names=list(level_counts.keys()),
                title="Roles by Hierarchy Level"
            )
            st.plotly_chart(fig_levels, use_container_width=True)
        
        with col2:
            # Permission distribution by role
            perm_counts = []
            role_names = []
            
            for role in roles_data[:10]:  # Top 10 roles
                permissions = role_configurator.get_role_permissions(role['role_id'])
                perm_counts.append(len(permissions))
                role_names.append(role['display_name'])
            
            if perm_counts:
                fig_perms = px.bar(
                    x=role_names,
                    y=perm_counts,
                    title="Permission Count by Role",
                    labels={'x': 'Roles', 'y': 'Permission Count'}
                )
                fig_perms.update_xaxis(tickangle=45)
                st.plotly_chart(fig_perms, use_container_width=True)


def render_bulk_operations_interface(role_configurator) -> None:
    """Render bulk operations interface"""
    st.markdown("### ⚡ Bulk Operations")
    
    tabs = st.tabs(["🔄 Mass Updates", "📋 Export/Import", "🗑️ Cleanup"])
    
    with tabs[0]:
        st.markdown("#### Mass Permission Updates")
        
        roles_data = role_configurator.get_role_hierarchy()
        role_options = [f"{role['display_name']} (ID: {role['role_id']})" for role in roles_data]
        
        selected_roles = st.multiselect("Select Roles", role_options)
        
        if selected_roles:
            permissions_by_category = role_configurator.get_permissions_by_category()
            
            operation = st.radio("Operation", ["Add Permissions", "Remove Permissions", "Replace Permissions"])
            
            selected_permissions = []
            for category, permissions in permissions_by_category.items():
                category_info = role_configurator.permission_categories.get(category, {})
                
                with st.expander(f"{category_info.get('icon', '🔧')} {category_info.get('name', category.title())}"):
                    for perm in permissions:
                        if st.checkbox(f"{perm['permission_name']}", key=f"bulk_{perm['permission_key']}"):
                            selected_permissions.append(perm['permission_key'])
            
            if st.button("Execute Bulk Operation", type="primary"):
                if selected_permissions:
                    success_count = 0
                    for role_option in selected_roles:
                        role_id = int(role_option.split("ID: ")[1].split(")")[0])
                        
                        if operation == "Add Permissions":
                            if role_configurator.assign_permissions_to_role(role_id, selected_permissions, st.session_state.get('user_id')):
                                success_count += 1
                        # Add other operations as needed
                    
                    st.success(f"Bulk operation completed for {success_count} roles!")
                else:
                    st.warning("Please select at least one permission.")
    
    with tabs[1]:
        st.markdown("#### Export/Import Roles")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Export Roles**")
            roles_data = role_configurator.get_role_hierarchy()
            
            if st.button("Export All Roles"):
                export_data = {
                    'roles': roles_data,
                    'permissions': role_configurator.get_permissions_by_category(),
                    'export_timestamp': pd.Timestamp.now().isoformat()
                }
                
                st.download_button(
                    label="Download Role Configuration",
                    data=json.dumps(export_data, indent=2, default=str),
                    file_name=f"role_config_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col2:
            st.markdown("**Import Roles**")
            uploaded_file = st.file_uploader("Upload role configuration", type=['json'])
            
            if uploaded_file:
                try:
                    import_data = json.loads(uploaded_file.read())
                    st.json(import_data, expanded=False)
                    
                    if st.button("Import Configuration"):
                        st.info("Import functionality would be implemented here.")
                        # Implementation would go here
                        
                except json.JSONDecodeError:
                    st.error("Invalid JSON file.")
    
    with tabs[2]:
        st.markdown("#### Cleanup Operations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Inactive Roles**")
            if st.button("Remove Inactive Roles"):
                st.warning("This will permanently delete all inactive roles. This action cannot be undone.")
                if st.checkbox("I understand this action is permanent"):
                    # Implementation would go here
                    st.info("Cleanup functionality would be implemented here.")
        
        with col2:
            st.markdown("**Orphaned Permissions**")
            if st.button("Clean Orphaned Permissions"):
                st.info("This will remove permission assignments for deleted roles.")
                # Implementation would go here


def show_role_configurator_interface(role_configurator) -> None:
    """Main interface for role configuration system"""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem; color: white;">
        <h1 style="margin: 0; font-size: 2.5rem;">🎭 Dynamic Role Permission Configurator</h1>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1.2rem;">
            Advanced role management with visual hierarchy and granular permissions
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main tabs
    tabs = st.tabs([
        "🏗️ Dashboard", 
        "🌳 Hierarchy", 
        "🎯 Permissions", 
        "➕ Create Role", 
        "⚡ Bulk Ops"
    ])
    
    # Get base data
    roles_data = role_configurator.get_role_hierarchy()
    permissions_by_category = role_configurator.get_permissions_by_category()
    
    with tabs[0]:
        render_role_management_dashboard(role_configurator)
    
    with tabs[1]:
        st.markdown("### 🌳 Role Hierarchy Visualization")
        render_role_hierarchy_visualization(role_configurator, roles_data)
        
        # Role details table
        if roles_data:
            st.markdown("### 📋 Role Details")
            df = pd.DataFrame(roles_data)
            
            if not df.empty:
                # Select relevant columns for display
                display_columns = ['display_name', 'level', 'color', 'icon', 'is_active', 'created_at']
                available_columns = [col for col in display_columns if col in df.columns]
                
                if available_columns:
                    st.dataframe(
                        df[available_columns].style.format({
                            'created_at': lambda x: pd.to_datetime(x).strftime('%Y-%m-%d %H:%M') if pd.notnull(x) else ''
                        }),
                        use_container_width=True
                    )
    
    with tabs[2]:
        st.markdown("### 🎯 Permission Management")
        render_permission_matrix(role_configurator, roles_data, permissions_by_category)
    
    with tabs[3]:
        render_role_creation_interface(role_configurator)
    
    with tabs[4]:
        render_bulk_operations_interface(role_configurator)