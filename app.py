"""
Smart CRM - Lead Management System
Streamlit Professional Web Application
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import get_db_connection, close_db_connection, get_param_style, get_cursor_dict, _db_type

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="Smart CRM - Lead Management",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS INJECTION ====================
st.markdown("""
    <style>
    /* Main Layout Styling */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Hide Streamlit default branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Header Styling */
    .crm-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    
    .crm-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .crm-subtitle {
        color: #94a3b8;
        font-size: 1rem;
        margin-top: 4px;
    }

    /* Metric Cards */
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px 20px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #6366f1;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.2;
    }
    
    .metric-label {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-top: 6px;
    }
    
    /* Custom Badges */
    .badge-admin {
        background-color: rgba(239, 68, 68, 0.2);
        color: #fca5a5;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .badge-sales {
        background-color: rgba(59, 130, 246, 0.2);
        color: #93c5fd;
        border: 1px solid rgba(59, 130, 246, 0.4);
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    /* Login Box */
    .login-container {
        max-width: 420px;
        margin: 60px auto;
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 36px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
    }
    </style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE INIT ====================
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'role' not in st.session_state:
    st.session_state['role'] = None


# ==================== DATABASE QUERY HELPERS ====================

def fetch_user_by_credentials(username, password):
    """Authenticate user against database"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = get_cursor_dict(conn)
        param = get_param_style()
        query = f"SELECT id, username, role FROM users WHERE username = {param} AND password = {param}"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        if user and hasattr(user, 'keys'):
            user = dict(user)
        return user
    except Exception as e:
        st.error(f"Database error during authentication: {e}")
        return None
    finally:
        cursor.close()
        close_db_connection(conn)


def fetch_all_leads():
    """Fetch all leads ordered by created_at DESC"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = get_cursor_dict(conn)
        query = "SELECT * FROM leads ORDER BY created_at DESC"
        cursor.execute(query)
        leads = cursor.fetchall()
        if leads and hasattr(leads[0], 'keys'):
            leads = [dict(lead) for lead in leads]
        return leads
    except Exception as e:
        st.error(f"Error fetching leads: {e}")
        return []
    finally:
        cursor.close()
        close_db_connection(conn)


def insert_new_lead(name, phone, email, city, source, status):
    """Insert new lead record into database"""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        param = get_param_style()
        query = f"""
            INSERT INTO leads (name, phone, email, city, source, status)
            VALUES ({param}, {param}, {param}, {param}, {param}, {param})
        """
        cursor.execute(query, (name, phone, email, city, source, status))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error adding lead: {e}")
        return False
    finally:
        cursor.close()
        close_db_connection(conn)


def update_lead_status_db(lead_id, new_status):
    """Update lead status in database"""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        param = get_param_style()
        query = f"UPDATE leads SET status = {param} WHERE id = {param}"
        cursor.execute(query, (new_status, lead_id))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error updating lead status: {e}")
        return False
    finally:
        cursor.close()
        close_db_connection(conn)


def delete_lead_db(lead_id):
    """Delete a lead from database (Admin only)"""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        param = get_param_style()
        query = f"DELETE FROM leads WHERE id = {param}"
        cursor.execute(query, (lead_id,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error deleting lead: {e}")
        return False
    finally:
        cursor.close()
        close_db_connection(conn)


def fetch_all_users():
    """Fetch user accounts list (Admin view)"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = get_cursor_dict(conn)
        cursor.execute("SELECT id, username, role, created_at FROM users ORDER BY id ASC")
        users = cursor.fetchall()
        if users and hasattr(users[0], 'keys'):
            users = [dict(u) for u in users]
        return users
    except Exception as e:
        return []
    finally:
        cursor.close()
        close_db_connection(conn)


# ==================== VIEW: LOGIN SCREEN ====================

def render_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style="text-align: center; margin-bottom: 24px;">
                <h1 style="font-size: 2.5rem; font-weight: 800; color: #f8fafc; margin-bottom: 8px;">💼 Smart CRM</h1>
                <p style="color: #94a3b8; font-size: 1rem;">Enterprise Lead Management Portal</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            st.subheader("Sign In to Your Account")
            username_input = st.text_input("Username", placeholder="Enter your username")
            password_input = st.text_input("Password", type="password", placeholder="Enter your password")
            submit_btn = st.form_submit_button("🚀 Sign In", use_container_width=True)
            
            if submit_btn:
                if not username_input or not password_input:
                    st.error("Please enter both username and password.")
                else:
                    user = fetch_user_by_credentials(username_input, password_input)
                    if user:
                        st.session_state['user_id'] = user['id']
                        st.session_state['username'] = user['username']
                        st.session_state['role'] = user['role']
                        st.success(f"Welcome back, {user['username']}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
        
        with st.expander("🔑 View Demo Credentials"):
            st.markdown("""
                * **Admin Account**: Username: `admin` | Password: `admin123`
                * **Sales Executive Account**: Username: `sales1` | Password: `sales123`
            """)


# ==================== MAIN APPLICATION APP ====================

def render_app():
    # Sidebar Profile & Logout
    with st.sidebar:
        st.markdown("### 💼 Smart CRM System")
        st.markdown("---")
        
        role_class = "badge-admin" if st.session_state['role'] == "Admin" else "badge-sales"
        st.markdown(f"""
            <div style="background: #1e293b; padding: 16px; border-radius: 12px; border: 1px solid #334155; margin-bottom: 20px;">
                <div style="font-size: 0.85rem; color: #94a3b8; font-weight: 600;">Logged in as</div>
                <div style="font-size: 1.2rem; font-weight: 700; color: #f8fafc; margin-bottom: 8px;">👤 {st.session_state['username']}</div>
                <span class="{role_class}">{st.session_state['role']}</span>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔴 Sign Out", use_container_width=True):
            st.session_state['user_id'] = None
            st.session_state['username'] = None
            st.session_state['role'] = None
            st.rerun()
            
        st.markdown("---")
        st.caption("Smart CRM v2.0 • Streamlit Edition")

    # Header Title Banner
    st.markdown("""
        <div class="crm-header">
            <h1 class="crm-title">Smart CRM Dashboard</h1>
            <p class="crm-subtitle">Manage, track, and convert sales leads effortlessly.</p>
        </div>
    """, unsafe_allow_html=True)

    # Fetch data
    leads_list = fetch_all_leads()
    df_leads = pd.DataFrame(leads_list) if leads_list else pd.DataFrame(columns=[
        'id', 'name', 'phone', 'email', 'city', 'source', 'status', 'created_at'
    ])

    # Top KPI Metrics Header
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    total_count = len(df_leads)
    new_count = len(df_leads[df_leads['status'] == 'New']) if not df_leads.empty else 0
    contacted_count = len(df_leads[df_leads['status'] == 'Contacted']) if not df_leads.empty else 0
    in_progress_count = len(df_leads[df_leads['status'] == 'In Progress']) if not df_leads.empty else 0
    converted_count = len(df_leads[df_leads['status'] == 'Converted']) if not df_leads.empty else 0
    lost_count = len(df_leads[df_leads['status'] == 'Lost']) if not df_leads.empty else 0

    col1.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#6366f1;">{total_count}</div><div class="metric-label">Total Leads</div></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#3b82f6;">{new_count}</div><div class="metric-label">New</div></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#f59e0b;">{contacted_count}</div><div class="metric-label">Contacted</div></div>', unsafe_allow_html=True)
    col4.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#a855f7;">{in_progress_count}</div><div class="metric-label">In Progress</div></div>', unsafe_allow_html=True)
    col5.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#10b981;">{converted_count}</div><div class="metric-label">Converted</div></div>', unsafe_allow_html=True)
    col6.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#ef4444;">{lost_count}</div><div class="metric-label">Lost</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Navigation Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Leads Directory", 
        "➕ Add New Lead", 
        "📈 Analytics & Insights", 
        "⚙️ System Status"
    ])

    # ==================== TAB 1: LEADS DIRECTORY & ACTIONS ====================
    with tab1:
        st.subheader("Manage Sales Leads")
        
        # Search & Filter Controls
        fcol1, fcol2, fcol3 = st.columns([2, 1, 1])
        with fcol1:
            search_query = st.text_input("🔍 Search Leads", placeholder="Search by name, phone, email, or city...")
        with fcol2:
            status_options = ["All"] + list(df_leads['status'].unique()) if not df_leads.empty else ["All"]
            status_filter = st.selectbox("Filter by Status", status_options)
        with fcol3:
            source_options = ["All"] + list(df_leads['source'].unique()) if not df_leads.empty else ["All"]
            source_filter = st.selectbox("Filter by Source", source_options)

        # Apply Filters
        filtered_df = df_leads.copy()
        if not filtered_df.empty:
            if search_query:
                q = search_query.lower()
                filtered_df = filtered_df[
                    filtered_df['name'].str.lower().str.contains(q) |
                    filtered_df['email'].str.lower().str.contains(q) |
                    filtered_df['phone'].str.lower().str.contains(q) |
                    filtered_df['city'].str.lower().str.contains(q)
                ]
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df['status'] == status_filter]
            if source_filter != "All":
                filtered_df = filtered_df[filtered_df['source'] == source_filter]

        # Display Table
        if not filtered_df.empty:
            display_df = filtered_df[['id', 'name', 'phone', 'email', 'city', 'source', 'status', 'created_at']].rename(columns={
                'id': 'ID',
                'name': 'Full Name',
                'phone': 'Phone',
                'email': 'Email',
                'city': 'City',
                'source': 'Source',
                'status': 'Status',
                'created_at': 'Date Added'
            })
            st.dataframe(
                display_df, 
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID": st.column_config.NumberColumn(format="%d"),
                    "Date Added": st.column_config.DatetimeColumn(format="YYYY-MM-DD HH:mm")
                }
            )
        else:
            st.info("No leads match your search/filter criteria.")

        st.markdown("---")

        # Interactive Lead Action Drawer
        act_col1, act_col2 = st.columns(2)
        
        with act_col1:
            with st.expander("⚡ Update Lead Status", expanded=False):
                if not df_leads.empty:
                    lead_choices = {f"#{row['id']} - {row['name']} ({row['status']})": row['id'] for _, row in df_leads.iterrows()}
                    selected_lead_label = st.selectbox("Select Lead to Update", list(lead_choices.keys()), key="update_lead_select")
                    selected_lead_id = lead_choices[selected_lead_label]
                    
                    new_status_val = st.selectbox(
                        "New Status", 
                        ["New", "Contacted", "In Progress", "Converted", "Lost"],
                        key="update_status_val"
                    )
                    
                    if st.button("Update Status", use_container_width=True, type="primary"):
                        if update_lead_status_db(selected_lead_id, new_status_val):
                            st.success(f"Status updated successfully for Lead #{selected_lead_id}!")
                            st.rerun()
                else:
                    st.write("No leads available.")

        with act_col2:
            with st.expander("🗑️ Delete Lead Record", expanded=False):
                if st.session_state['role'] == 'Admin':
                    if not df_leads.empty:
                        delete_choices = {f"#{row['id']} - {row['name']} ({row['status']})": row['id'] for _, row in df_leads.iterrows()}
                        del_lead_label = st.selectbox("Select Lead to Delete", list(delete_choices.keys()), key="del_lead_select")
                        del_lead_id = delete_choices[del_lead_label]
                        
                        st.warning("⚠️ Warning: Deleting a lead is permanent!")
                        if st.button("Delete Lead", use_container_width=True, type="secondary"):
                            if delete_lead_db(del_lead_id):
                                st.success(f"Lead #{del_lead_id} deleted successfully!")
                                st.rerun()
                    else:
                        st.write("No leads available.")
                else:
                    st.error("🔒 Access Denied: Admin privileges are required to delete lead records.")

    # ==================== TAB 2: ADD NEW LEAD ====================
    with tab2:
        st.subheader("Add New Lead Record")
        st.caption("Fill in the details below to add a new customer prospect.")
        
        with st.form("add_lead_form", clear_on_submit=True):
            form_col1, form_col2 = st.columns(2)
            with form_col1:
                name_in = st.text_input("Full Name *", placeholder="e.g. Alex Morgan")
                phone_in = st.text_input("Phone Number *", placeholder="e.g. (555) 019-2834")
                email_in = st.text_input("Email Address *", placeholder="e.g. alex.m@company.com")
            with form_col2:
                city_in = st.text_input("City *", placeholder="e.g. San Francisco")
                source_in = st.selectbox("Lead Source *", ["Website", "Social Media", "Referral", "Cold Call", "Event", "Partner", "Other"])
                status_in = st.selectbox("Initial Status", ["New", "Contacted", "In Progress", "Converted", "Lost"])
            
            submit_lead = st.form_submit_button("➕ Save Lead Record", use_container_width=True, type="primary")
            
            if submit_lead:
                if not all([name_in, phone_in, email_in, city_in]):
                    st.error("Please fill in all required fields marked with *.")
                else:
                    if insert_new_lead(name_in, phone_in, email_in, city_in, source_in, status_in):
                        st.success(f"Lead '{name_in}' added successfully!")
                        st.rerun()

    # ==================== TAB 3: ANALYTICS & VISUALS ====================
    with tab3:
        st.subheader("Sales Pipeline & Lead Insights")
        
        if not df_leads.empty:
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.markdown("#### Lead Status Breakdown")
                status_counts = df_leads['status'].value_counts().reset_index()
                status_counts.columns = ['Status', 'Count']
                
                fig_status = px.pie(
                    status_counts, 
                    names='Status', 
                    values='Count',
                    hole=0.4,
                    color='Status',
                    color_discrete_map={
                        'New': '#3b82f6',
                        'Contacted': '#f59e0b',
                        'In Progress': '#a855f7',
                        'Converted': '#10b981',
                        'Lost': '#ef4444'
                    }
                )
                fig_status.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#f8fafc',
                    margin=dict(t=20, b=20, l=20, r=20)
                )
                st.plotly_chart(fig_status, use_container_width=True)
                
            with chart_col2:
                st.markdown("#### Lead Acquisition Sources")
                source_counts = df_leads['source'].value_counts().reset_index()
                source_counts.columns = ['Source', 'Count']
                
                fig_source = px.bar(
                    source_counts,
                    x='Source',
                    y='Count',
                    color='Source',
                    text='Count'
                )
                fig_source.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#f8fafc',
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='#334155'),
                    margin=dict(t=20, b=20, l=20, r=20)
                )
                st.plotly_chart(fig_source, use_container_width=True)
                
            st.markdown("---")
            
            # Conversion Metrics Card
            conversion_rate = (converted_count / total_count * 100) if total_count > 0 else 0
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(59, 130, 246, 0.15) 100%); border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 12px; padding: 20px; text-align: center;">
                    <h3 style="color: #10b981; margin: 0; font-size: 1.2rem;">🏆 Overall Conversion Efficiency</h3>
                    <div style="font-size: 2.8rem; font-weight: 800; color: #f8fafc; margin: 8px 0;">{conversion_rate:.1f}%</div>
                    <p style="color: #94a3b8; margin: 0;">{converted_count} leads converted out of {total_count} total leads.</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Add leads to view analytical charts.")

    # ==================== TAB 4: SYSTEM STATUS ====================
    with tab4:
        st.subheader("System Infrastructure & Database Connection")
        
        db_mode_str = "MySQL (Primary Database)" if _db_type == 'mysql' else "SQLite (Local Auto-Fallback Database)"
        st.success(f"Connected to Database Mode: **{db_mode_str}**")
        
        if st.session_state['role'] == 'Admin':
            st.markdown("#### Registered User Accounts")
            users = fetch_all_users()
            if users:
                df_users = pd.DataFrame(users)
                st.dataframe(df_users, use_container_width=True, hide_index=True)
        else:
            st.info("Registered accounts view is restricted to Admin users.")


# ==================== APPLICATION ROUTING ====================

def main():
    if st.session_state['user_id'] is None:
        render_login()
    else:
        render_app()


if __name__ == '__main__':
    main()
