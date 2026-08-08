"""
Database Configuration File
Auto-detects MySQL or SQLite and initializes database automatically
"""

import sqlite3
import os
from contextlib import contextmanager

# Global variable to track database type
_db_type = None
_db_path = 'smart_crm.db'


def _try_mysql():
    """Try to connect to MySQL, return connection if successful"""
    try:
        import mysql.connector
        from mysql.connector import Error
        
        DB_CONFIG = {
            'host': 'localhost',
            'database': 'smart_crm',
            'user': 'root',
            'password': '',
            'charset': 'utf8mb4',
            'autocommit': False
        }
        
        # First try to create database if it doesn't exist
        try:
            temp_config = DB_CONFIG.copy()
            temp_config.pop('database')
            temp_conn = mysql.connector.connect(**temp_config)
            temp_cursor = temp_conn.cursor()
            temp_cursor.execute("CREATE DATABASE IF NOT EXISTS smart_crm")
            temp_conn.commit()
            temp_cursor.close()
            temp_conn.close()
        except:
            pass
        
        # Now connect to the database
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection, 'mysql'
    except:
        pass
    return None, None


def _get_sqlite_connection():
    """Get SQLite connection with row factory for dictionary-like access"""
    conn = sqlite3.connect(_db_path)
    conn.row_factory = sqlite3.Row
    return conn, 'sqlite'


def _init_database(connection, db_type):
    """Initialize database tables and sample data if needed"""
    cursor = connection.cursor()
    
    try:
        # Check if users table exists
        if db_type == 'mysql':
            cursor.execute("SHOW TABLES LIKE 'users'")
            table_exists = cursor.fetchone() is not None
        else:  # sqlite
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            # Create users table
            if db_type == 'mysql':
                users_table = """
                CREATE TABLE users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    role VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            else:  # sqlite
                users_table = """
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            
            cursor.execute(users_table)
            
            # Create leads table
            if db_type == 'mysql':
                leads_table = """
                CREATE TABLE leads (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    phone VARCHAR(20) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    city VARCHAR(50) NOT NULL,
                    source VARCHAR(50) NOT NULL,
                    status VARCHAR(50) DEFAULT 'New',
                    assigned_to INT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            else:  # sqlite
                leads_table = """
                CREATE TABLE leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    email TEXT NOT NULL,
                    city TEXT NOT NULL,
                    source TEXT NOT NULL,
                    status TEXT DEFAULT 'New',
                    assigned_to INTEGER NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
                )
                """
            
            cursor.execute(leads_table)
            
            # Create trigger for SQLite to auto-update updated_at
            if db_type == 'sqlite':
                cursor.execute("""
                    CREATE TRIGGER IF NOT EXISTS update_leads_timestamp 
                    AFTER UPDATE ON leads
                    BEGIN
                        UPDATE leads SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                    END
                """)
            
            connection.commit()
            
            # Insert sample users
            if db_type == 'mysql':
                cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                              ('admin', 'admin123', 'Admin'))
                cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                              ('harshal', 'harshal@123', 'Admin'))
                cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                              ('sales1', 'sales123', 'Sales Executive'))
            else:  # sqlite
                cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                              ('admin', 'admin123', 'Admin'))
                cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                              ('harshal', 'harshal@123', 'Admin'))
                cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                              ('sales1', 'sales123', 'Sales Executive'))
            
            # Insert sample leads
            if db_type == 'mysql':
                sample_leads = [
                    ('John Smith', '(555) 123-4567', 'john.smith@email.com', 'New York', 'Website', 'New', 2),
                    ('Sarah Johnson', '(555) 234-5678', 'sarah.j@email.com', 'Los Angeles', 'Social Media', 'Contacted', 2),
                    ('Michael Brown', '(555) 345-6789', 'm.brown@email.com', 'Chicago', 'Referral', 'In Progress', 2)
                ]
                cursor.executemany("""
                    INSERT INTO leads (name, phone, email, city, source, status, assigned_to)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, sample_leads)
            else:  # sqlite
                sample_leads = [
                    ('John Smith', '(555) 123-4567', 'john.smith@email.com', 'New York', 'Website', 'New', 2),
                    ('Sarah Johnson', '(555) 234-5678', 'sarah.j@email.com', 'Los Angeles', 'Social Media', 'Contacted', 2),
                    ('Michael Brown', '(555) 345-6789', 'm.brown@email.com', 'Chicago', 'Referral', 'In Progress', 2)
                ]
                cursor.executemany("""
                    INSERT INTO leads (name, phone, email, city, source, status, assigned_to)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, sample_leads)
            
        # Check and create products table
        if db_type == 'mysql':
            cursor.execute("SHOW TABLES LIKE 'products'")
            prod_exists = cursor.fetchone() is not None
        else:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
            prod_exists = cursor.fetchone() is not None

        if not prod_exists:
            if db_type == 'mysql':
                cursor.execute("""
                CREATE TABLE products (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(150) NOT NULL,
                    category VARCHAR(50) DEFAULT 'Software',
                    selling_price DECIMAL(10,2) NOT NULL,
                    cost_price DECIMAL(10,2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                sample_products = [
                    ('CRM Enterprise Subscription', 'Software', 45000.00, 15000.00),
                    ('Annual Maintenance & Support', 'Service', 12000.00, 3000.00),
                    ('Cloud Setup & Data Migration', 'Service', 25000.00, 8000.00),
                    ('Custom Analytics & Reports Module', 'Software Addon', 15000.00, 4000.00),
                    ('WhatsApp API Integration Pack', 'Integration', 18000.00, 5000.00)
                ]
                cursor.executemany("INSERT INTO products (name, category, selling_price, cost_price) VALUES (%s, %s, %s, %s)", sample_products)
            else:  # sqlite
                cursor.execute("""
                CREATE TABLE products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT DEFAULT 'Software',
                    selling_price REAL NOT NULL,
                    cost_price REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                sample_products = [
                    ('CRM Enterprise Subscription', 'Software', 45000.00, 15000.00),
                    ('Annual Maintenance & Support', 'Service', 12000.00, 3000.00),
                    ('Cloud Setup & Data Migration', 'Service', 25000.00, 8000.00),
                    ('Custom Analytics & Reports Module', 'Software Addon', 15000.00, 4000.00),
                    ('WhatsApp API Integration Pack', 'Integration', 18000.00, 5000.00)
                ]
                cursor.executemany("INSERT INTO products (name, category, selling_price, cost_price) VALUES (?, ?, ?, ?)", sample_products)

        # Check and create customers table
        if db_type == 'mysql':
            cursor.execute("SHOW TABLES LIKE 'customers'")
            cust_exists = cursor.fetchone() is not None
        else:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers'")
            cust_exists = cursor.fetchone() is not None

        if not cust_exists:
            if db_type == 'mysql':
                cursor.execute("""
                CREATE TABLE customers (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    company VARCHAR(100) NULL,
                    email VARCHAR(100) NOT NULL,
                    phone VARCHAR(20) NOT NULL,
                    customer_type VARCHAR(50) DEFAULT 'Regular',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                cursor.execute("""
                CREATE TABLE sales_transactions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    customer_id INT NOT NULL,
                    product_name VARCHAR(150) NOT NULL,
                    sale_amount DECIMAL(10,2) NOT NULL,
                    cost_amount DECIMAL(10,2) NOT NULL,
                    profit_amount DECIMAL(10,2) NOT NULL,
                    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                # Insert sample customers
                sample_customers = [
                    ('Reliance Retail (Rajesh Sharma)', 'Reliance Retail', 'rajesh.sharma@reliance.com', '+91 98200 12345', 'VIP'),
                    ('Tata Consultancy (Priya Nair)', 'TCS Ltd', 'priya.nair@tcs.com', '+91 98450 67890', 'Corporate'),
                    ('Apex Logistics India (Amit Patel)', 'Apex Logistics', 'amit.patel@apex.co.in', '+91 97110 54321', 'Regular')
                ]
                cursor.executemany("INSERT INTO customers (name, company, email, phone, customer_type) VALUES (%s, %s, %s, %s, %s)", sample_customers)
                
                # Insert sample sales transactions (in INR ₹)
                sample_sales = [
                    (1, 'CRM Enterprise Subscription', 45000.00, 15000.00, 30000.00),
                    (1, 'Annual Maintenance & Support', 12000.00, 3000.00, 9000.00),
                    (2, 'Cloud Setup & Data Migration', 25000.00, 8000.00, 17000.00),
                    (2, 'WhatsApp API Integration Pack', 18000.00, 5000.00, 13000.00),
                    (3, 'Custom Analytics & Reports Module', 15000.00, 4000.00, 11000.00)
                ]
                cursor.executemany("INSERT INTO sales_transactions (customer_id, product_name, sale_amount, cost_amount, profit_amount) VALUES (%s, %s, %s, %s, %s)", sample_sales)
            else:  # sqlite
                cursor.execute("""
                CREATE TABLE customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    company TEXT NULL,
                    email TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    customer_type TEXT DEFAULT 'Regular',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                cursor.execute("""
                CREATE TABLE sales_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    product_name TEXT NOT NULL,
                    sale_amount REAL NOT NULL,
                    cost_amount REAL NOT NULL,
                    profit_amount REAL NOT NULL,
                    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
                )
                """)
                sample_customers = [
                    ('Reliance Retail (Rajesh Sharma)', 'Reliance Retail', 'rajesh.sharma@reliance.com', '+91 98200 12345', 'VIP'),
                    ('Tata Consultancy (Priya Nair)', 'TCS Ltd', 'priya.nair@tcs.com', '+91 98450 67890', 'Corporate'),
                    ('Apex Logistics India (Amit Patel)', 'Apex Logistics', 'amit.patel@apex.co.in', '+91 97110 54321', 'Regular')
                ]
                cursor.executemany("INSERT INTO customers (name, company, email, phone, customer_type) VALUES (?, ?, ?, ?, ?)", sample_customers)
                
                sample_sales = [
                    (1, 'CRM Enterprise Subscription', 45000.00, 15000.00, 30000.00),
                    (1, 'Annual Maintenance & Support', 12000.00, 3000.00, 9000.00),
                    (2, 'Cloud Setup & Data Migration', 25000.00, 8000.00, 17000.00),
                    (2, 'WhatsApp API Integration Pack', 18000.00, 5000.00, 13000.00),
                    (3, 'Custom Analytics & Reports Module', 15000.00, 4000.00, 11000.00)
                ]
                cursor.executemany("INSERT INTO sales_transactions (customer_id, product_name, sale_amount, cost_amount, profit_amount) VALUES (?, ?, ?, ?, ?)", sample_sales)
            
            connection.commit()
            print("Customer and sales tables initialized successfully.")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        connection.rollback()
    finally:
        cursor.close()


def get_db_connection():
    """
    Get database connection (MySQL or SQLite)
    Auto-detects and initializes database on first run
    
    Returns:
        Database connection object (MySQL or SQLite)
        None if both fail
    """
    global _db_type
    
    # If we already know the database type, use it
    if _db_type == 'mysql':
        conn, db_type = _try_mysql()
        if conn:
            return conn
        # MySQL failed, fall back to SQLite
        _db_type = None
    
    if _db_type == 'sqlite':
        conn, db_type = _get_sqlite_connection()
        if conn:
            _init_database(conn, db_type)
            return conn
    
    # Try MySQL first
    if _db_type is None:
        conn, db_type = _try_mysql()
        if conn:
            _db_type = 'mysql'
            _init_database(conn, db_type)
            print("Connected to MySQL database.")
            return conn
        
        # Fall back to SQLite
        conn, db_type = _get_sqlite_connection()
        if conn:
            _db_type = 'sqlite'
            _init_database(conn, db_type)
            print("MySQL not available. Using SQLite database (smart_crm.db).")
            return conn
    
    print("ERROR: Could not connect to any database.")
    return None


def close_db_connection(connection):
    """
    Safely close the database connection
    
    Args:
        connection: Database connection object to close
    """
    if connection:
        try:
            if _db_type == 'mysql':
                if hasattr(connection, 'is_connected') and connection.is_connected():
                    connection.close()
            else:  # sqlite
                connection.close()
        except:
            pass


def get_param_style():
    """
    Get the parameter style for SQL queries
    Returns '%s' for MySQL, '?' for SQLite
    """
    global _db_type
    if _db_type == 'mysql':
        return '%s'
    return '?'


def get_cursor_dict(connection):
    """
    Get a cursor that returns dictionary-like rows
    Works for both MySQL and SQLite
    """
    if _db_type == 'mysql':
        return connection.cursor(dictionary=True)
    else:  # sqlite
        return connection.cursor()
