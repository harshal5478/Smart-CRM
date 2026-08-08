-- Smart CRM Database Schema
-- Complete database setup script
-- Run this once to create database, tables, and sample data

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS smart_crm;

-- Use the database
USE smart_crm;

-- Drop tables if they exist (for clean reinstall)
DROP TABLE IF EXISTS leads;
DROP TABLE IF EXISTS users;

-- Users table for authentication
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('Admin', 'Sales Executive') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Leads table for lead management
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default users
INSERT INTO users (username, password, role) VALUES
('admin', 'admin123', 'Admin'),
('sales1', 'sales123', 'Sales Executive');

-- Insert sample leads
INSERT INTO leads (name, phone, email, city, source, status, assigned_to) VALUES
('John Smith', '(555) 123-4567', 'john.smith@email.com', 'New York', 'Website', 'New', 2),
('Sarah Johnson', '(555) 234-5678', 'sarah.j@email.com', 'Los Angeles', 'Social Media', 'Contacted', 2),
('Michael Brown', '(555) 345-6789', 'm.brown@email.com', 'Chicago', 'Referral', 'In Progress', 2);
