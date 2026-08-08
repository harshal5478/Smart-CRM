"""
Smart CRM - Indian Lead & Customer Profitability Management System
Streamlit Professional Web Application (Rupees ₹ Edition)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import get_db_connection, close_db_connection, get_param_style, get_cursor_dict, _db_type

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="Smart CRM - Sales & Profit Management (₹)",
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
        font-size: 1.8rem;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.2;
    }
    
    .metric-label {
        font-size: 0.82rem;
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


def register_user_db(username, password, role):
    """Register a new user account"""
    conn = get_db_connection()
    if not conn:
        return False, "Database connection error."
    try:
        cursor = conn.cursor()
        param = get_param_style()
        query = f"INSERT INTO users (username, password, role) VALUES ({param}, {param}, {param})"
        cursor.execute(query, (username, password, role))
        conn.commit()
        return True, "Account created successfully! You can now sign in."
    except Exception as e:
        return False, f"Error creating account (username may already exist): {e}"
    finally:
        cursor.close()
        close_db_connection(conn)


# --- PRODUCTS DB HELPERS ---

def fetch_all_products():
    """Fetch all products in catalog"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = get_cursor_dict(conn)
        query = "SELECT * FROM products ORDER BY name ASC"
        cursor.execute(query)
        products = cursor.fetchall()
        if products and hasattr(products[0], 'keys'):
            products = [dict(p) for p in products]
        return products
    except Exception as e:
        st.error(f"Error fetching products: {e}")
        return []
    finally:
        cursor.close()
        close_db_connection(conn)


def insert_new_product(name, category, selling_price, cost_price):
    """Add a new product to catalog (Admin)"""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        param = get_param_style()
        query = f"INSERT INTO products (name, category, selling_price, cost_price) VALUES ({param}, {param}, {param}, {param})"
        cursor.execute(query, (name, category, float(selling_price), float(cost_price)))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error adding product: {e}")
        return False
    finally:
        cursor.close()
        close_db_connection(conn)


def delete_product_db(product_id):
    """Delete a product from catalog (Admin)"""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        param = get_param_style()
        query = f"DELETE FROM products WHERE id = {param}"
        cursor.execute(query, (product_id,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error deleting product: {e}")
        return False
    finally:
        cursor.close()
        close_db_connection(conn)


# --- LEADS DB HELPERS ---

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


# --- CUSTOMERS & SALES TRANSACTION DB HELPERS ---

def fetch_all_customers():
    """Fetch all customers with lifetime sales metrics"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = get_cursor_dict(conn)
        query = """
            SELECT 
                c.id, 
                c.name, 
                c.company, 
                c.email, 
                c.phone, 
                c.customer_type, 
                c.created_at,
                COUNT(st.id) AS total_orders,
                COALESCE(SUM(st.sale_amount), 0) AS lifetime_revenue,
                COALESCE(SUM(st.profit_amount), 0) AS lifetime_profit
            FROM customers c
            LEFT JOIN sales_transactions st ON c.id = st.customer_id
            GROUP BY c.id
            ORDER BY lifetime_profit DESC
        """
        cursor.execute(query)
        customers = cursor.fetchall()
        if customers and hasattr(customers[0], 'keys'):
            customers = [dict(c) for c in customers]
        return customers
    except Exception as e:
        st.error(f"Error fetching customers: {e}")
        return []
    finally:
        cursor.close()
        close_db_connection(conn)


def insert_new_customer(name, company, email, phone, customer_type):
    """Insert a new customer profile"""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        param = get_param_style()
        query = f"""
            INSERT INTO customers (name, company, email, phone, customer_type)
            VALUES ({param}, {param}, {param}, {param}, {param})
        """
        cursor.execute(query, (name, company, email, phone, customer_type))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error adding customer: {e}")
        return False
    finally:
        cursor.close()
        close_db_connection(conn)


def delete_customer_db(customer_id):
    """Delete a customer record (Admin only)"""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        param = get_param_style()
        query = f"DELETE FROM customers WHERE id = {param}"
        cursor.execute(query, (customer_id,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error deleting customer: {e}")
        return False
    finally:
        cursor.close()
        close_db_connection(conn)


def fetch_all_sales_transactions():
    """Fetch all product sales transactions with customer details"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = get_cursor_dict(conn)
        query = """
            SELECT 
                st.id,
                st.customer_id,
                c.name AS customer_name,
                c.company AS customer_company,
                st.product_name,
                st.sale_amount,
                st.cost_amount,
                st.profit_amount,
                st.sale_date
            FROM sales_transactions st
            JOIN customers c ON st.customer_id = c.id
            ORDER BY st.sale_date DESC
        """
        cursor.execute(query)
        sales = cursor.fetchall()
        if sales and hasattr(sales[0], 'keys'):
            sales = [dict(s) for s in sales]
        return sales
    except Exception as e:
        st.error(f"Error fetching sales transactions: {e}")
        return []
    finally:
        cursor.close()
        close_db_connection(conn)


def fetch_customer_sales_history(customer_id):
    """Fetch specific sales history for a customer"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = get_cursor_dict(conn)
        param = get_param_style()
        query = f"""
            SELECT id, product_name, sale_amount, cost_amount, profit_amount, sale_date
            FROM sales_transactions
            WHERE customer_id = {param}
            ORDER BY sale_date DESC
        """
        cursor.execute(query, (customer_id,))
        history = cursor.fetchall()
        if history and hasattr(history[0], 'keys'):
            history = [dict(h) for h in history]
        return history
    except Exception as e:
        st.error(f"Error fetching customer sales history: {e}")
        return []
    finally:
        cursor.close()
        close_db_connection(conn)


def insert_sale_transaction(customer_id, product_name, sale_amount, cost_amount):
    """Record a new product sale for a customer"""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        profit_amount = float(sale_amount) - float(cost_amount)
        cursor = conn.cursor()
        param = get_param_style()
        query = f"""
            INSERT INTO sales_transactions (customer_id, product_name, sale_amount, cost_amount, profit_amount)
            VALUES ({param}, {param}, {param}, {param}, {param})
        """
        cursor.execute(query, (customer_id, product_name, float(sale_amount), float(cost_amount), float(profit_amount)))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error recording sale transaction: {e}")
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
                <h1 style="font-size: 2.5rem; font-weight: 800; color: #f8fafc; margin-bottom: 8px;">💼 Smart CRM India</h1>
                <p style="color: #94a3b8; font-size: 1rem;">Sales, Customer & Profit Management Portal (₹)</p>
            </div>
        """, unsafe_allow_html=True)
        
        login_tab, signup_tab = st.tabs(["🚀 Sign In", "➕ Create Account"])
        
        with login_tab:
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
        
        with signup_tab:
            with st.form("signup_form", clear_on_submit=True):
                st.subheader("Register New User")
                new_user = st.text_input("Choose Username", placeholder="e.g. harshal")
                new_pass = st.text_input("Choose Password", type="password", placeholder="e.g. harshal@123")
                new_role = st.selectbox("Assign Role", ["Admin", "Sales Executive"])
                signup_btn = st.form_submit_button("✨ Register Account", use_container_width=True)
                
                if signup_btn:
                    if not new_user or not new_pass:
                        st.error("Please enter both username and password.")
                    else:
                        success, msg = register_user_db(new_user, new_pass, new_role)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
        
        with st.expander("🔑 View Available Accounts"):
            st.markdown("""
                * **Admin Account**: Username: `harshal` | Password: `harshal@123`
                * **Admin Account**: Username: `admin` | Password: `admin123`
                * **Sales Executive**: Username: `sales1` | Password: `sales123`
            """)


# ==================== MAIN APPLICATION APP ====================

def render_app():
    # Sidebar Profile & Logout
    with st.sidebar:
        st.markdown("### 💼 Smart CRM India (₹)")
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
        st.caption("Smart CRM v3.0 • INR (₹) Edition")

    # Header Title Banner
    st.markdown("""
        <div class="crm-header">
            <h1 class="crm-title">Smart CRM - Indian Rupee (₹) Portal</h1>
            <p class="crm-subtitle">Manage products, place customer orders in ₹, and track net profit.</p>
        </div>
    """, unsafe_allow_html=True)

    # Fetch Data
    products_list = fetch_all_products()
    df_products = pd.DataFrame(products_list) if products_list else pd.DataFrame(columns=[
        'id', 'name', 'category', 'selling_price', 'cost_price', 'created_at'
    ])

    leads_list = fetch_all_leads()
    df_leads = pd.DataFrame(leads_list) if leads_list else pd.DataFrame(columns=[
        'id', 'name', 'phone', 'email', 'city', 'source', 'status', 'created_at'
    ])

    customers_list = fetch_all_customers()
    df_customers = pd.DataFrame(customers_list) if customers_list else pd.DataFrame(columns=[
        'id', 'name', 'company', 'email', 'phone', 'customer_type', 'total_orders', 'lifetime_revenue', 'lifetime_profit'
    ])

    sales_list = fetch_all_sales_transactions()
    df_sales = pd.DataFrame(sales_list) if sales_list else pd.DataFrame(columns=[
        'id', 'customer_id', 'customer_name', 'customer_company', 'product_name', 'sale_amount', 'cost_amount', 'profit_amount', 'sale_date'
    ])

    # Top KPI Metrics Header (in ₹)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_leads_cnt = len(df_leads)
    total_customers_cnt = len(df_customers)
    total_revenue_val = df_sales['sale_amount'].sum() if not df_sales.empty else 0.0
    total_cost_val = df_sales['cost_amount'].sum() if not df_sales.empty else 0.0
    total_profit_val = df_sales['profit_amount'].sum() if not df_sales.empty else 0.0

    col1.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#6366f1;">{total_leads_cnt}</div><div class="metric-label">Active Leads</div></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#3b82f6;">{total_customers_cnt}</div><div class="metric-label">Total Customers</div></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#34d399;">₹{total_revenue_val:,.2f}</div><div class="metric-label">Gross Revenue</div></div>', unsafe_allow_html=True)
    col4.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#f87171;">₹{total_cost_val:,.2f}</div><div class="metric-label">Total Product Cost</div></div>', unsafe_allow_html=True)
    col5.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#10b981;">₹{total_profit_val:,.2f}</div><div class="metric-label">Net Profit</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Simplified Navigation Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📦 Products Catalog", 
        "🛒 Create Order / Record Sale", 
        "👥 Customers & Sales Ledger", 
        "📋 Leads Directory", 
        "📈 Financial Analytics", 
        "⚙️ System Status"
    ])

    # ==================== TAB 1: PRODUCTS CATALOG (ADD / REMOVE PRODUCTS) ====================
    with tab1:
        st.subheader("Product Catalog & Pricing (₹)")
        st.caption("Admin can add or remove products from the company catalog.")
        
        # Display Products Table
        if not df_products.empty:
            prod_display = df_products[['id', 'name', 'category', 'selling_price', 'cost_price']].rename(columns={
                'id': 'ID',
                'name': 'Product / Service Name',
                'category': 'Category',
                'selling_price': 'Selling Price (₹)',
                'cost_price': 'Product Cost (₹)'
            })
            # Add calculated Profit per unit
            prod_display['Profit per Unit (₹)'] = prod_display['Selling Price (₹)'] - prod_display['Product Cost (₹)']
            
            st.dataframe(
                prod_display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID": st.column_config.NumberColumn(format="%d"),
                    "Selling Price (₹)": st.column_config.NumberColumn(format="₹%.2f"),
                    "Product Cost (₹)": st.column_config.NumberColumn(format="₹%.2f"),
                    "Profit per Unit (₹)": st.column_config.NumberColumn(format="₹%.2f")
                }
            )
        else:
            st.info("No products found in catalog. Add a product below.")

        st.markdown("---")

        p_col1, p_col2 = st.columns(2)

        # Admin: Add New Product Form
        with p_col1:
            with st.expander("➕ Add New Product to Catalog", expanded=True):
                with st.form("add_product_form", clear_on_submit=True):
                    p_name = st.text_input("Product / Service Name *", placeholder="e.g. ERP Software Subscription")
                    p_cat = st.selectbox("Category", ["Software", "Service", "Hardware", "Integration", "Software Addon", "Consulting", "Other"])
                    p_sell = st.number_input("Selling Price (₹) *", min_value=0.0, value=25000.0, step=1000.0)
                    p_cost = st.number_input("Product Cost (₹) *", min_value=0.0, value=8000.0, step=500.0)
                    
                    unit_profit = p_sell - p_cost
                    st.info(f"💡 Profit per unit: **₹{unit_profit:,.2f}**")
                    
                    submit_prod = st.form_submit_button("➕ Save Product to Catalog", use_container_width=True, type="primary")
                    if submit_prod:
                        if not p_name:
                            st.error("Please enter Product Name.")
                        else:
                            if insert_new_product(p_name, p_cat, p_sell, p_cost):
                                st.success(f"Product '{p_name}' added to catalog successfully!")
                                st.rerun()

        # Admin: Delete Product Option
        with p_col2:
            with st.expander("🗑️ Remove Product from Catalog", expanded=True):
                if st.session_state['role'] == 'Admin':
                    if not df_products.empty:
                        prod_opts = {f"#{p['id']} - {p['name']} (₹{p['selling_price']:,.2f})": p['id'] for _, p in df_products.iterrows()}
                        del_prod_label = st.selectbox("Select Product to Remove", list(prod_opts.keys()))
                        del_prod_id = prod_opts[del_prod_label]
                        
                        st.warning("⚠️ Warning: Removing a product will remove it from future order selections!")
                        if st.button("Delete Product", use_container_width=True, type="secondary"):
                            if delete_product_db(del_prod_id):
                                st.success("Product removed from catalog!")
                                st.rerun()
                    else:
                        st.write("No products available to delete.")
                else:
                    st.error("🔒 Access Denied: Admin privileges are required to remove products.")

    # ==================== TAB 2: CREATE ORDER / RECORD SALE ====================
    with tab2:
        st.subheader("Create Customer Order / Record Sale (₹)")
        st.caption("Select an existing Customer and choose a Product from your Catalog. Pricing and Net Profit in Rupees (₹) are calculated automatically.")
        
        with st.form("create_order_form", clear_on_submit=True):
            if not df_customers.empty and not df_products.empty:
                # Customer selector
                cust_order_opts = {f"#{c['id']} - {c['name']} ({c['company']})": c['id'] for _, c in df_customers.iterrows()}
                sel_cust_label = st.selectbox("1. Select Target Customer *", list(cust_order_opts.keys()))
                sel_cust_id = cust_order_opts[sel_cust_label]
                
                # Product selector from Catalog
                prod_order_opts = {f"{p['name']} — Selling Price: ₹{p['selling_price']:,.2f} (Cost: ₹{p['cost_price']:,.2f})": p['id'] for _, p in df_products.iterrows()}
                sel_prod_label = st.selectbox("2. Select Product / Service from Catalog *", list(prod_order_opts.keys()))
                sel_prod_id = prod_order_opts[sel_prod_label]
                
                # Get selected product details
                chosen_product = df_products[df_products['id'] == sel_prod_id].iloc[0]
                
                ocol1, ocol2, ocol3 = st.columns(3)
                with ocol1:
                    quantity = st.number_input("Quantity *", min_value=1, value=1, step=1)
                with ocol2:
                    override_price = st.number_input("Selling Price per Unit (₹)", min_value=0.0, value=float(chosen_product['selling_price']), step=500.0)
                with ocol3:
                    override_cost = st.number_input("Cost Price per Unit (₹)", min_value=0.0, value=float(chosen_product['cost_price']), step=500.0)
                
                total_sale_amt = override_price * quantity
                total_cost_amt = override_cost * quantity
                total_profit_amt = total_sale_amt - total_cost_amt
                
                st.success(f"💰 Order Summary: Total Amount = **₹{total_sale_amt:,.2f}** | Total Cost = **₹{total_cost_amt:,.2f}** | **Net Profit = ₹{total_profit_amt:,.2f}**")
                
                submit_order = st.form_submit_button("🛍️ Place & Record Order", use_container_width=True, type="primary")
                if submit_order:
                    prod_description = f"{chosen_product['name']} (x{quantity})" if quantity > 1 else chosen_product['name']
                    if insert_sale_transaction(sel_cust_id, prod_description, total_sale_amt, total_cost_amt):
                        st.success(f"Order for '{chosen_product['name']}' placed successfully! Net Profit: ₹{total_profit_amt:,.2f}")
                        st.rerun()
            else:
                if df_customers.empty:
                    st.warning("Please add at least one Customer in the 'Customers & Sales Ledger' tab.")
                if df_products.empty:
                    st.warning("Please add at least one Product in the 'Products Catalog' tab.")

    # ==================== TAB 3: CUSTOMERS & SALES LEDGER ====================
    with tab3:
        st.subheader("Customer Directory & Lifetime Sales Ledger (₹)")
        st.caption("View repeat customer purchase histories, total sales orders, and net profit generated per customer in ₹.")
        
        # Display Customers Table
        if not df_customers.empty:
            cust_display_df = df_customers[['id', 'name', 'company', 'email', 'phone', 'customer_type', 'total_orders', 'lifetime_revenue', 'lifetime_profit']].rename(columns={
                'id': 'ID',
                'name': 'Customer Name',
                'company': 'Company',
                'email': 'Email',
                'phone': 'Phone',
                'customer_type': 'Tier',
                'total_orders': 'Orders Placed',
                'lifetime_revenue': 'Lifetime Revenue (₹)',
                'lifetime_profit': 'Net Profit Generated (₹)'
            })
            
            st.dataframe(
                cust_display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ID": st.column_config.NumberColumn(format="%d"),
                    "Lifetime Revenue (₹)": st.column_config.NumberColumn(format="₹%.2f"),
                    "Net Profit Generated (₹)": st.column_config.NumberColumn(format="₹%.2f")
                }
            )
        else:
            st.info("No customer records found. Add a customer below.")

        st.markdown("---")

        cust_act_col1, cust_act_col2 = st.columns(2)

        # Customer Deep-Dive Timeline Expander
        with cust_act_col1:
            with st.expander("🔍 View Complete Customer Purchase Timeline", expanded=True):
                if not df_customers.empty:
                    cust_options = {f"#{c['id']} - {c['name']} ({c['company']})": c['id'] for _, c in df_customers.iterrows()}
                    sel_cust_label = st.selectbox("Select Customer to Inspect History", list(cust_options.keys()))
                    sel_cust_id = cust_options[sel_cust_label]
                    
                    history = fetch_customer_sales_history(sel_cust_id)
                    if history:
                        df_hist = pd.DataFrame(history)
                        st.markdown(f"##### Purchase History for Customer #{sel_cust_id}")
                        st.dataframe(
                            df_hist[['product_name', 'sale_amount', 'cost_amount', 'profit_amount', 'sale_date']].rename(columns={
                                'product_name': 'Product / Service Sold',
                                'sale_amount': 'Sale Price (₹)',
                                'cost_amount': 'Cost (₹)',
                                'profit_amount': 'Net Profit (₹)',
                                'sale_date': 'Sale Date'
                            }),
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "Sale Price (₹)": st.column_config.NumberColumn(format="₹%.2f"),
                                "Cost (₹)": st.column_config.NumberColumn(format="₹%.2f"),
                                "Net Profit (₹)": st.column_config.NumberColumn(format="₹%.2f")
                            }
                        )
                        cust_profit_total = df_hist['profit_amount'].sum()
                        st.success(f"💰 Total Net Profit from this Customer: **₹{cust_profit_total:,.2f}** over **{len(df_hist)}** orders.")
                    else:
                        st.info("No sales recorded yet for this customer.")
                else:
                    st.write("No customers available.")

        # Create New Customer Form
        with cust_act_col2:
            with st.expander("➕ Add New Customer Account", expanded=True):
                with st.form("new_customer_form", clear_on_submit=True):
                    c_name = st.text_input("Customer / Contact Name *", placeholder="e.g. Rajesh Sharma")
                    c_company = st.text_input("Company Name", placeholder="e.g. Reliance Retail")
                    c_email = st.text_input("Email Address *", placeholder="e.g. rajesh.s@company.in")
                    c_phone = st.text_input("Phone Number *", placeholder="e.g. +91 98200 12345")
                    c_type = st.selectbox("Customer Tier", ["Regular", "VIP", "Corporate"])
                    
                    submit_cust = st.form_submit_button("➕ Save Customer Profile", use_container_width=True, type="primary")
                    if submit_cust:
                        if not all([c_name, c_email, c_phone]):
                            st.error("Please fill in all required fields.")
                        else:
                            if insert_new_customer(c_name, c_company, c_email, c_phone, c_type):
                                st.success(f"Customer '{c_name}' created successfully!")
                                st.rerun()

    # ==================== TAB 4: LEADS DIRECTORY & ACTIONS ====================
    with tab4:
        st.subheader("Sales Leads Pipeline")
        
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

        # Add Lead & Update Status
        l_col1, l_col2 = st.columns(2)
        
        with l_col1:
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

        with l_col2:
            with st.expander("➕ Add New Lead Record", expanded=False):
                with st.form("add_lead_form", clear_on_submit=True):
                    name_in = st.text_input("Full Name *", placeholder="e.g. Vikram Malhotra")
                    phone_in = st.text_input("Phone Number *", placeholder="e.g. +91 98111 22334")
                    email_in = st.text_input("Email Address *", placeholder="e.g. vikram@m.com")
                    city_in = st.text_input("City *", placeholder="e.g. Mumbai")
                    source_in = st.selectbox("Lead Source *", ["Website", "Social Media", "Referral", "Cold Call", "Event", "Partner", "Other"])
                    status_in = st.selectbox("Initial Status", ["New", "Contacted", "In Progress", "Converted", "Lost"])
                    
                    submit_lead = st.form_submit_button("➕ Save Lead Record", use_container_width=True, type="primary")
                    if submit_lead:
                        if not all([name_in, phone_in, email_in, city_in]):
                            st.error("Please fill in all required fields.")
                        else:
                            if insert_new_lead(name_in, phone_in, email_in, city_in, source_in, status_in):
                                st.success(f"Lead '{name_in}' added successfully!")
                                st.rerun()

    # ==================== TAB 5: FINANCIAL ANALYTICS (IN ₹) ====================
    with tab5:
        st.subheader("Financial Overview & Profitability Analytics (₹)")
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("#### Top Profit-Generating Customers (₹)")
            if not df_customers.empty and df_customers['lifetime_profit'].sum() > 0:
                fig_cust_profit = px.bar(
                    df_customers.sort_values(by='lifetime_profit', ascending=True).tail(5),
                    y='name',
                    x='lifetime_profit',
                    orientation='h',
                    text='lifetime_profit',
                    color='lifetime_profit',
                    color_continuous_scale='Greens',
                    labels={'name': 'Customer', 'lifetime_profit': 'Net Profit (₹)'}
                )
                fig_cust_profit.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#f8fafc',
                    margin=dict(t=20, b=20, l=20, r=20)
                )
                st.plotly_chart(fig_cust_profit, use_container_width=True)
            else:
                st.info("Record orders to view customer profit ranking.")
                
        with chart_col2:
            st.markdown("#### Financial Breakdown (Revenue vs Cost vs Profit)")
            if not df_sales.empty:
                fin_summary_df = pd.DataFrame([
                    {'Category': 'Gross Revenue', 'Amount': total_revenue_val},
                    {'Category': 'Product Cost', 'Amount': total_cost_val},
                    {'Category': 'Net Profit', 'Amount': total_profit_val}
                ])
                fig_fin = px.bar(
                    fin_summary_df,
                    x='Category',
                    y='Amount',
                    color='Category',
                    text='Amount',
                    color_discrete_map={'Gross Revenue': '#3b82f6', 'Product Cost': '#ef4444', 'Net Profit': '#10b981'}
                )
                fig_fin.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#f8fafc',
                    yaxis=dict(showgrid=True, gridcolor='#334155'),
                    margin=dict(t=20, b=20, l=20, r=20)
                )
                st.plotly_chart(fig_fin, use_container_width=True)

    # ==================== TAB 6: SYSTEM STATUS ====================
    with tab6:
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
