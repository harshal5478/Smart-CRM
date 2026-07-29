"""
Smart CRM - Lead Management System
Main Flask Application
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from config import get_db_connection, close_db_connection, get_param_style, get_cursor_dict
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'  # Change this in production!


# ==================== HELPER FUNCTIONS ====================

def login_required(f):
    """
    Decorator to protect routes that require authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorator to protect routes that require admin role
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'Admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def index():
    """Redirect to login if not authenticated, else to dashboard"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page and authentication"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('login.html')
        
        # Connect to database
        conn = get_db_connection()
        if not conn:
            flash('Database connection error. Please try again.', 'danger')
            return render_template('login.html')
        
        try:
            cursor = get_cursor_dict(conn)
            # Query user from database
            param = get_param_style()
            query = f"SELECT * FROM users WHERE username = {param} AND password = {param}"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            
            if user:
                # Convert to dict if SQLite (Row object)
                if hasattr(user, 'keys'):
                    user = dict(user)
                # Set session variables
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                flash(f'Welcome, {user["username"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password.', 'danger')
        except Exception as e:
            flash('Database error. Please try again.', 'danger')
        finally:
            cursor.close()
            close_db_connection(conn)
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout user and clear session"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))


# ==================== DASHBOARD ROUTES ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """Display all leads in a table"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'danger')
        return render_template('dashboard.html', leads=[])
    
    try:
        cursor = get_cursor_dict(conn)
        # Fetch all leads ordered by creation date (newest first)
        query = "SELECT * FROM leads ORDER BY created_at DESC"
        cursor.execute(query)
        leads = cursor.fetchall()
        # Convert SQLite Row objects to dicts
        if leads and hasattr(leads[0], 'keys'):
            leads = [dict(lead) for lead in leads]
        return render_template('dashboard.html', leads=leads)
    except Exception as e:
        flash('Error fetching leads.', 'danger')
        return render_template('dashboard.html', leads=[])
    finally:
        cursor.close()
        close_db_connection(conn)


# ==================== LEAD MANAGEMENT ROUTES ====================

@app.route('/add_lead', methods=['GET', 'POST'])
@login_required
def add_lead():
    """Add a new lead to the database"""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        city = request.form.get('city')
        source = request.form.get('source')
        status = request.form.get('status', 'New')
        
        # Validate required fields
        if not all([name, phone, email, city, source]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('add_lead.html')
        
        # Connect to database
        conn = get_db_connection()
        if not conn:
            flash('Database connection error.', 'danger')
            return render_template('add_lead.html')
        
        try:
            cursor = conn.cursor()
            # Insert new lead
            param = get_param_style()
            query = f"""
                INSERT INTO leads (name, phone, email, city, source, status)
                VALUES ({param}, {param}, {param}, {param}, {param}, {param})
            """
            cursor.execute(query, (name, phone, email, city, source, status))
            conn.commit()
            flash('Lead added successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'Error adding lead: {str(e)}', 'danger')
        finally:
            cursor.close()
            close_db_connection(conn)
    
    return render_template('add_lead.html')


@app.route('/update_status/<int:lead_id>', methods=['POST'])
@login_required
def update_status(lead_id):
    """Update lead status"""
    new_status = request.form.get('status')
    
    if not new_status:
        flash('Status is required.', 'danger')
        return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        cursor = conn.cursor()
        param = get_param_style()
        query = f"UPDATE leads SET status = {param} WHERE id = {param}"
        cursor.execute(query, (new_status, lead_id))
        conn.commit()
        flash('Lead status updated successfully!', 'success')
    except Exception as e:
        flash('Error updating status.', 'danger')
    finally:
        cursor.close()
        close_db_connection(conn)
    
    return redirect(url_for('dashboard'))


@app.route('/delete_lead/<int:lead_id>', methods=['POST'])
@admin_required
def delete_lead(lead_id):
    """Delete a lead (Admin only)"""
    conn = get_db_connection()
    if not conn:
        flash('Database connection error.', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        cursor = conn.cursor()
        param = get_param_style()
        query = f"DELETE FROM leads WHERE id = {param}"
        cursor.execute(query, (lead_id,))
        conn.commit()
        flash('Lead deleted successfully!', 'success')
    except Exception as e:
        flash('Error deleting lead.', 'danger')
    finally:
        cursor.close()
        close_db_connection(conn)
    
    return redirect(url_for('dashboard'))


# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
