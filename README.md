# Smart CRM - Lead Management System

A simple and beginner-friendly Customer Relationship Management (CRM) system for managing leads, built with Flask and MySQL.

## Features

- **User Authentication**: Login system with role-based access (Admin, Sales Executive)
- **Lead Management**: Add, view, update, and delete leads
- **Dashboard**: View all leads with statistics
- **Role-Based Permissions**: Admin can delete leads, Sales Executives can view and update

## Tech Stack

- **Frontend**: HTML, CSS, Bootstrap 5, JavaScript
- **Backend**: Python (Flask)
- **Database**: MySQL

## Project Structure

```
smart_crm_project/
│
├── app.py              # Main Flask backend
├── config.py           # MySQL connection configuration
├── requirements.txt    # Python dependencies
│
├── static/
│   ├── css/style.css   # Custom styles
│   └── js/script.js    # Custom JavaScript
│
├── templates/
│   ├── base.html       # Base template
│   ├── login.html      # Login page
│   ├── dashboard.html  # Dashboard with leads table
│   └── add_lead.html   # Add new lead form
│
└── sql/
    └── database.sql    # Database schema
```

## Installation & Setup

### 1. Prerequisites

- Python 3.7 or higher
- MySQL Server installed and running
- pip (Python package manager)

### 2. Database Setup

1. Open MySQL command line or MySQL Workbench
2. Run the SQL script to create the database:
   ```bash
   mysql -u root -p < sql/database.sql
   ```
   Or manually execute the SQL commands in `sql/database.sql`

### 3. Configure Database Connection

Edit `config.py` and update the database credentials:

```python
DB_CONFIG = {
    'host': 'localhost',
    'database': 'smart_crm',
    'user': 'root',        # Your MySQL username
    'password': '',        # Your MySQL password
    ...
}
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Default Login Credentials

- **Admin**: 
  - Username: `admin`
  - Password: `admin123`

- **Sales Executive**: 
  - Username: `sales1`
  - Password: `sales123`

## Usage

1. **Login**: Access the application and login with your credentials
2. **Dashboard**: View all leads in a table format with statistics
3. **Add Lead**: Click "Add New Lead" to create a new lead entry
4. **Update Status**: Change lead status using the dropdown in the dashboard
5. **Delete Lead**: (Admin only) Click the delete button to remove a lead

## Lead Fields

- **Name**: Lead's full name (required)
- **Phone**: Contact phone number (required)
- **Email**: Email address (required)
- **City**: City location (required)
- **Source**: Lead source (Website, Social Media, Referral, etc.)
- **Status**: Current status (New, Contacted, In Progress, Converted, Lost)

## Security Notes

⚠️ **Important**: This is a basic implementation for learning purposes. For production use:

- Use password hashing (bcrypt, werkzeug.security)
- Implement CSRF protection
- Use environment variables for sensitive data
- Add input validation and sanitization
- Use HTTPS
- Implement proper session management

## Troubleshooting

### Database Connection Error
- Ensure MySQL server is running
- Verify credentials in `config.py`
- Check if database `smart_crm` exists

### Module Not Found Error
- Run `pip install -r requirements.txt`
- Ensure you're using Python 3.7+

### Port Already in Use
- Change the port in `app.py`: `app.run(port=5001)`

## License

This project is for educational purposes.
