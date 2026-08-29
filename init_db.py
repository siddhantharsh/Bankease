"""
BankEase - PostgreSQL Database Initialization Script
Creates all tables and seeds initial data for the Render deployment.
Usage: python init_db.py
"""

import os
import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://root:root@127.0.0.1:5432/bankease')


def get_connection():
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    conn.autocommit = False
    return conn



def create_tables(cursor):
    """Create all tables in the correct order (respecting FK dependencies)."""

    # 1. Bank table (no dependencies)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bank (
            "Bank_ID" SERIAL PRIMARY KEY,
            "Bank_Name" VARCHAR(100) NOT NULL,
            "Name" VARCHAR(100),
            "Branch" VARCHAR(100) NOT NULL,
            "IFSC_Code" VARCHAR(20) NOT NULL UNIQUE
        );
    """)

    # 2. Customers table (no dependencies)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            "Customer_ID" SERIAL PRIMARY KEY,
            "Name" VARCHAR(100) NOT NULL,
            "Email" VARCHAR(100) NOT NULL UNIQUE,
            "Password" VARCHAR(255) NOT NULL DEFAULT 'password123',
            "Phone" VARCHAR(15) NOT NULL UNIQUE,
            "Address" TEXT NOT NULL,
            "Date_Of_Birth" DATE NOT NULL
        );
    """)

    # 3. Admins table (depends on bank)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            "Admin_ID" SERIAL PRIMARY KEY,
            "Bank_ID" INT NOT NULL REFERENCES bank("Bank_ID") ON DELETE CASCADE,
            "Name" VARCHAR(100) NOT NULL,
            "Email" VARCHAR(100) NOT NULL UNIQUE,
            "Password" VARCHAR(255) NOT NULL DEFAULT 'admin123',
            "Role" VARCHAR(50) NOT NULL CHECK ("Role" IN ('Manager', 'Loan Officer', 'Security Officer'))
        );
    """)

    # 4. Accounts table (depends on customers, bank)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            "Account_Number" SERIAL PRIMARY KEY,
            "Customer_ID" INT NOT NULL REFERENCES customers("Customer_ID") ON DELETE CASCADE,
            "Bank_ID" INT NOT NULL REFERENCES bank("Bank_ID") ON DELETE CASCADE,
            "Account_Type" VARCHAR(20) NOT NULL CHECK ("Account_Type" IN ('Savings', 'Current', 'Fixed Deposit')),
            "Balance" DECIMAL(12,2) NOT NULL DEFAULT 0.00 CHECK ("Balance" >= 0),
            "Status" VARCHAR(20) NOT NULL DEFAULT 'Active' CHECK ("Status" IN ('Active', 'Pending', 'Rejected', 'Closed')),
            "Date_Opened" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 5. Transactions table (depends on accounts)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            "Transaction_ID" SERIAL PRIMARY KEY,
            "Account_Number" INT NOT NULL REFERENCES accounts("Account_Number") ON DELETE CASCADE,
            "Transaction_Type" VARCHAR(20) NOT NULL CHECK ("Transaction_Type" IN ('Deposit', 'Withdrawal', 'Transfer')),
            "Amount" DECIMAL(12,2) NOT NULL,
            "Timestamp" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            "Description" TEXT,
            "Receiver_Account" INT REFERENCES accounts("Account_Number") ON DELETE SET NULL
        );
    """)

    # 6. Loans table (depends on customers, accounts)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS loans (
            "Loan_ID" SERIAL PRIMARY KEY,
            "Customer_ID" INT NOT NULL REFERENCES customers("Customer_ID") ON DELETE CASCADE,
            "Account_Number" INT REFERENCES accounts("Account_Number"),
            "Bank_ID" INT NOT NULL REFERENCES bank("Bank_ID") ON DELETE CASCADE,
            "Loan_Type" VARCHAR(20) NOT NULL CHECK ("Loan_Type" IN ('Home', 'Car', 'Personal', 'Business')),
            "Amount" DECIMAL(12,2),
            "Loan_Amount" DECIMAL(12,2) NOT NULL,
            "Interest_Rate" REAL NOT NULL,
            "Start_Date" TIMESTAMP,
            "End_Date" TIMESTAMP,
            "Application_Date" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            "Loan_Term" INT NOT NULL,
            "Status" VARCHAR(20) NOT NULL CHECK ("Status" IN ('Approved', 'Pending', 'Rejected', 'Paid'))
        );
    """)

    # 7. Security table (depends on accounts)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS security (
            "Security_ID" SERIAL PRIMARY KEY,
            "Account_Number" INT NOT NULL REFERENCES accounts("Account_Number") ON DELETE CASCADE,
            "Security_Type" VARCHAR(50) NOT NULL CHECK ("Security_Type" IN ('Two-Factor Authentication', 'Fraud Alert', 'Transaction Monitoring')),
            "Status" VARCHAR(10) NOT NULL CHECK ("Status" IN ('Active', 'Inactive')),
            "Last_Updated" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE ("Account_Number", "Security_Type")
        );
    """)

    # 8. Investments table (depends on customers, accounts)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS investments (
            "Investment_ID" SERIAL PRIMARY KEY,
            "Customer_ID" INT NOT NULL REFERENCES customers("Customer_ID") ON DELETE CASCADE,
            "Investment_Type" VARCHAR(50) NOT NULL,
            "Amount" DECIMAL(12,2),
            "Investment_Amount" DECIMAL(12,2) NOT NULL,
            "Start_Date" DATE NOT NULL,
            "Maturity_Date" DATE NOT NULL,
            "Status" VARCHAR(20) NOT NULL DEFAULT 'Active' CHECK ("Status" IN ('Active', 'Closed', 'Matured')),
            "Return_Rate" REAL DEFAULT 8.0,
            "Monthly_Payment" DECIMAL(12,2) DEFAULT 0.00,
            "Payment_Account" INT REFERENCES accounts("Account_Number"),
            "Bank_Name" VARCHAR(100),
            "Account_Number" INT
        );
    """)

    # 9. Payments table (depends on customers, accounts)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            "Payment_ID" SERIAL PRIMARY KEY,
            "Customer_ID" INT NOT NULL REFERENCES customers("Customer_ID") ON DELETE CASCADE,
            "Account_Number" INT NOT NULL REFERENCES accounts("Account_Number") ON DELETE CASCADE,
            "Payment_Amount" DECIMAL(12,2) NOT NULL,
            "Payment_Date" DATE NOT NULL,
            "Payment_Type" VARCHAR(20) NOT NULL CHECK ("Payment_Type" IN ('Credit Card', 'Bill Payment', 'Loan EMI'))
        );
    """)

    # 10. Transaction log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactionlog (
            "Log_ID" SERIAL PRIMARY KEY,
            "Transaction_ID" INT,
            "Log_Message" VARCHAR(255),
            "Log_Date" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    print("All tables created successfully.")


def seed_data(cursor):
    """Insert initial seed data."""

    # Check if data already exists
    cursor.execute('SELECT COUNT(*) as count FROM bank')
    if cursor.fetchone()['count'] > 0:
        print("Data already exists, skipping seed.")
        return

    # Banks
    cursor.execute("""
        INSERT INTO bank ("Bank_ID", "Bank_Name", "Name", "Branch", "IFSC_Code") VALUES
        (1, 'State Bank of India', 'State Bank of India', 'Mumbai Main Branch', 'SBIN0001234'),
        (2, 'HDFC Bank', 'HDFC Bank', 'Bangalore Indiranagar', 'HDFC0005678'),
        (3, 'ICICI Bank', 'ICICI Bank', 'Delhi Connaught Place', 'ICIC0004321'),
        (4, 'Axis Bank', 'Axis Bank', 'Chennai T Nagar', 'AXIS0008765');
    """)
    # Reset sequence
    cursor.execute("SELECT setval(pg_get_serial_sequence('bank', 'Bank_ID'), 4);")

    # Customers
    cursor.execute("""
        INSERT INTO customers ("Customer_ID", "Name", "Email", "Password", "Phone", "Address", "Date_Of_Birth") VALUES
        (1, 'Amit Sharma', 'amit.sharma92@mail.in', 'password123', '9876543210', '123, MG Road, Mumbai, Maharashtra', '1992-05-14'),
        (2, 'Priya Verma', 'priya.verma88@mail.in', 'password123', '9823456789', '56, Lake View Street, Bangalore, Karnataka', '1988-09-22'),
        (3, 'Rahul Mehta', 'rahul.mehta95@mail.in', 'password123', '9898765432', '78, Green Park, Delhi', '1995-11-05'),
        (4, 'Sneha Iyer', 'sneha.iyer90@mail.in', 'password123', '9786543210', '45, Besant Nagar, Chennai, Tamil Nadu', '1990-07-18');
    """)
    cursor.execute("SELECT setval(pg_get_serial_sequence('customers', 'Customer_ID'), 4);")

    # Admins
    cursor.execute("""
        INSERT INTO admins ("Admin_ID", "Bank_ID", "Name", "Email", "Password", "Role") VALUES
        (1, 1, 'Rajesh Khanna', 'rajesh.khanna@mail.in', 'admin123', 'Manager'),
        (2, 2, 'Neha Kapoor', 'neha.kapoor@mail.in', 'admin123', 'Loan Officer'),
        (3, 3, 'Vikas Gupta', 'vikas.gupta@mail.in', 'admin123', 'Security Officer'),
        (4, 4, 'Anita Das', 'anita.das@mail.in', 'admin123', 'Manager');
    """)
    cursor.execute("SELECT setval(pg_get_serial_sequence('admins', 'Admin_ID'), 4);")

    # Accounts
    cursor.execute("""
        INSERT INTO accounts ("Account_Number", "Customer_ID", "Bank_ID", "Account_Type", "Balance", "Status", "Date_Opened") VALUES
        (1, 1, 1, 'Savings', 50000.00, 'Active', CURRENT_TIMESTAMP),
        (2, 2, 2, 'Current', 75000.50, 'Active', CURRENT_TIMESTAMP),
        (3, 3, 3, 'Savings', 120000.75, 'Active', CURRENT_TIMESTAMP),
        (4, 4, 4, 'Fixed Deposit', 250000.00, 'Active', CURRENT_TIMESTAMP);
    """)
    cursor.execute("SELECT setval(pg_get_serial_sequence('accounts', 'Account_Number'), 4);")

    # Transactions
    cursor.execute("""
        INSERT INTO transactions ("Transaction_ID", "Account_Number", "Transaction_Type", "Amount", "Timestamp", "Description", "Receiver_Account") VALUES
        (1, 1, 'Deposit', 10000.00, CURRENT_TIMESTAMP, 'Initial deposit', NULL),
        (2, 2, 'Withdrawal', 5000.00, CURRENT_TIMESTAMP, 'ATM Withdrawal', NULL),
        (3, 3, 'Transfer', 20000.00, CURRENT_TIMESTAMP, 'Transfer to 1', 1),
        (4, 4, 'Deposit', 15000.00, CURRENT_TIMESTAMP, 'Cash deposit', NULL);
    """)
    cursor.execute("SELECT setval(pg_get_serial_sequence('transactions', 'Transaction_ID'), 4);")

    # Loans
    cursor.execute("""
        INSERT INTO loans ("Loan_ID", "Customer_ID", "Account_Number", "Bank_ID", "Loan_Type", "Amount", "Loan_Amount", "Interest_Rate", "Start_Date", "End_Date", "Loan_Term", "Status") VALUES
        (1, 1, 1, 1, 'Home', 2500000.00, 2500000.00, 6.5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '240 months', 240, 'Approved'),
        (2, 2, 2, 2, 'Car', 800000.00, 800000.00, 7.2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '60 months', 60, 'Pending'),
        (3, 3, 3, 3, 'Personal', 300000.00, 300000.00, 10.5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '36 months', 36, 'Rejected'),
        (4, 4, 4, 4, 'Business', 1500000.00, 1500000.00, 8.0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '120 months', 120, 'Approved');
    """)
    cursor.execute("SELECT setval(pg_get_serial_sequence('loans', 'Loan_ID'), 4);")

    # Security
    cursor.execute("""
        INSERT INTO security ("Security_ID", "Account_Number", "Security_Type", "Status", "Last_Updated") VALUES
        (1, 1, 'Two-Factor Authentication', 'Active', CURRENT_TIMESTAMP),
        (2, 2, 'Fraud Alert', 'Active', CURRENT_TIMESTAMP),
        (3, 3, 'Transaction Monitoring', 'Inactive', CURRENT_TIMESTAMP),
        (4, 4, 'Two-Factor Authentication', 'Active', CURRENT_TIMESTAMP);
    """)
    cursor.execute("SELECT setval(pg_get_serial_sequence('security', 'Security_ID'), 4);")

    # Investments
    cursor.execute("""
        INSERT INTO investments ("Investment_ID", "Customer_ID", "Investment_Type", "Amount", "Investment_Amount", "Start_Date", "Maturity_Date", "Status", "Return_Rate", "Monthly_Payment", "Payment_Account", "Bank_Name", "Account_Number") VALUES
        (1, 1, 'Stocks', 100000.00, 100000.00, '2023-01-01', '2028-01-01', 'Active', 12.0, 8333.33, 1, 'State Bank of India', 1),
        (2, 2, 'Mutual Funds', 200000.00, 200000.00, '2022-06-15', '2027-06-15', 'Active', 10.0, 16666.67, 2, 'HDFC Bank', 2),
        (3, 3, 'Bonds', 50000.00, 50000.00, '2021-03-10', '2026-03-10', 'Active', 8.0, 4166.67, 3, 'ICICI Bank', 3),
        (4, 4, 'Stocks', 250000.00, 250000.00, '2020-12-20', '2025-12-20', 'Active', 12.0, 20833.33, 4, 'Axis Bank', 4);
    """)
    cursor.execute("SELECT setval(pg_get_serial_sequence('investments', 'Investment_ID'), 4);")

    # Payments
    cursor.execute("""
        INSERT INTO payments ("Payment_ID", "Customer_ID", "Account_Number", "Payment_Amount", "Payment_Date", "Payment_Type") VALUES
        (1, 1, 1, 5000.00, '2024-02-01', 'Credit Card'),
        (2, 2, 2, 8000.00, '2024-02-05', 'Bill Payment'),
        (3, 3, 3, 12000.00, '2024-02-10', 'Loan EMI'),
        (4, 4, 4, 15000.00, '2024-02-15', 'Credit Card');
    """)
    cursor.execute("SELECT setval(pg_get_serial_sequence('payments', 'Payment_ID'), 4);")

    print("Seed data inserted successfully.")


if __name__ == '__main__':
    conn = get_connection()
    cursor = conn.cursor()
    try:
        create_tables(cursor)
        seed_data(cursor)
        conn.commit()
        print("Database initialization complete!")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

