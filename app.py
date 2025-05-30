from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import mysql.connector
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database configuration
db_config = {
    'host': '127.0.0.1',  # Using IP address instead of localhost
    'user': 'root',
    'password': 'root',
    'database': 'bankease',
    'port': 3306,
    'auth_plugin': 'mysql_native_password'  # Explicitly set authentication plugin
}

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, role):
        self.id = id
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    # Check if user is admin
    cursor.execute("SELECT Admin_ID FROM admins WHERE Admin_ID = %s", (user_id,))
    admin = cursor.fetchone()
    if admin:
        return User(admin['Admin_ID'], 'admin')
    
    # Check if user is customer
    cursor.execute("SELECT Customer_ID FROM customers WHERE Customer_ID = %s", (user_id,))
    customer = cursor.fetchone()
    if customer:
        return User(customer['Customer_ID'], 'customer')
    
    cursor.close()
    conn.close()
    return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/erd')
def erd():
    return render_template('erd.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Check admin login
        cursor.execute("SELECT Admin_ID FROM admins WHERE Email = %s AND Password = %s", (email, password))
        admin = cursor.fetchone()
        if admin:
            user = User(admin['Admin_ID'], 'admin')
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        
        # Check customer login
        cursor.execute("SELECT Customer_ID FROM customers WHERE Email = %s AND Password = %s", (email, password))
        customer = cursor.fetchone()
        if customer:
            user = User(customer['Customer_ID'], 'customer')
            login_user(user)
            return redirect(url_for('customer_dashboard'))
        
        flash('Invalid credentials')
        cursor.close()
        conn.close()
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']  # Get password from form
        phone = request.form['phone']
        address = request.form['address']
        dob = request.form['dob']
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO customers (Name, Email, Password, Phone, Address, Date_Of_Birth)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, email, password, phone, address, dob))
            conn.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}')
        finally:
            cursor.close()
            conn.close()
    
    return render_template('register.html')

@app.route('/apply/account', methods=['GET', 'POST'])
@login_required
def apply_account():
    if not isinstance(current_user, User):
        flash('Access denied. Please log in as a customer.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        bank_id = request.form.get('bank_id')
        account_type = request.form.get('account_type')
        initial_deposit = request.form.get('initial_deposit')
        
        if not bank_id or not account_type or initial_deposit is None:
            flash('Please fill in all required fields', 'danger')
            return redirect(url_for('apply_account'))
        try:
            initial_deposit = float(initial_deposit)
            if initial_deposit < 0:
                flash('Initial deposit cannot be negative', 'danger')
                return redirect(url_for('apply_account'))
            # Insert new account
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO accounts (Customer_ID, Bank_ID, Account_Type, Balance, Status, Date_Opened)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (current_user.id, bank_id, account_type, initial_deposit, 'Pending', datetime.now()))
            conn.commit()
            flash('Account application submitted successfully! Please wait for admin approval.', 'success')
            cursor.close()
            conn.close()
            return redirect(url_for('customer_dashboard'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('apply_account'))
    
    # Get available banks for the form
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT Bank_ID, Name FROM bank")
    banks = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('apply_account.html', banks=banks)

@app.route('/apply/loan', methods=['GET', 'POST'])
@login_required
def apply_loan():
    if not isinstance(current_user, User) or current_user.role != 'customer':
        flash('Access denied. Please log in as a customer.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        loan_type = request.form.get('loan_type')
        amount = request.form.get('amount')
        account_number = request.form.get('account_number')
        duration = request.form.get('duration')  # Get duration from form
        
        if not all([loan_type, amount, account_number, duration]):
            flash('Please fill in all fields', 'danger')
            return redirect(url_for('apply_loan'))
        
        try:
            # Verify account belongs to customer
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT Account_Number 
                FROM accounts 
                WHERE Account_Number = %s AND Customer_ID = %s AND Status = 'Active'
            """, (account_number, current_user.id))
            account = cursor.fetchone()
            
            if not account:
                flash('Invalid account or account not active', 'danger')
                return redirect(url_for('apply_loan'))
            
            # Calculate start and end dates
            current_time = datetime.now()
            start_date = current_time
            end_date = start_date + timedelta(days=int(duration) * 30)  # Convert months to days
            
            # Insert new loan application
            cursor.execute("""
                INSERT INTO loans (
                    Customer_ID, Account_Number, Loan_Type, Amount, 
                    Interest_Rate, Start_Date, End_Date, Status, Application_Date
                ) VALUES (%s, %s, %s, %s, 8.5, %s, %s, 'Pending', %s)
            """, (
                current_user.id, account_number, loan_type, amount,
                start_date, end_date, current_time
            ))
            conn.commit()
            
            flash('Loan application submitted successfully!', 'success')
            return redirect(url_for('customer_dashboard'))
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('apply_loan'))
        finally:
            cursor.close()
            conn.close()
    
    # Get customer's active accounts for the form
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.*, b.Name as Bank_Name 
        FROM accounts a 
        JOIN bank b ON a.Bank_ID = b.Bank_ID 
        WHERE a.Customer_ID = %s AND a.Status = 'Active'
    """, (current_user.id,))
    accounts = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('apply_loan.html', accounts=accounts)

@app.route('/admin/approve/account/<int:account_id>')
@login_required
def approve_account(account_id):
    if not isinstance(current_user, User) or current_user.role != 'admin':
        flash('Access denied. Please log in as an admin.', 'danger')
        return redirect(url_for('login'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE accounts 
            SET Status = 'Active' 
            WHERE Account_Number = %s
        """, (account_id,))
        conn.commit()
        flash('Account approved successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject/account/<int:account_id>')
@login_required
def reject_account(account_id):
    if not isinstance(current_user, User) or current_user.role != 'admin':
        flash('Access denied. Please log in as an admin.', 'danger')
        return redirect(url_for('login'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE accounts 
            SET Status = 'Rejected' 
            WHERE Account_Number = %s
        """, (account_id,))
        conn.commit()
        flash('Account rejected successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/approve/loan/<int:loan_id>')
@login_required
def approve_loan(loan_id):
    if not isinstance(current_user, User) or current_user.role != 'admin':
        flash('Access denied. Please log in as an admin.', 'danger')
        return redirect(url_for('login'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get loan details
        cursor.execute("""
            SELECT l.*, a.Account_Number 
            FROM loans l 
            JOIN accounts a ON l.Customer_ID = a.Customer_ID
            WHERE l.Loan_ID = %s AND l.Status = 'Pending'
            LIMIT 1
        """, (loan_id,))
        loan = cursor.fetchone()
        
        if not loan:
            flash('Loan not found or already processed', 'danger')
            return redirect(url_for('admin_dashboard'))
        
        # Update loan status to Approved
        cursor.execute("""
            UPDATE loans 
            SET Status = 'Approved'
            WHERE Loan_ID = %s
        """, (loan_id,))
        
        # Add loan amount to customer's account
        cursor.execute("""
            UPDATE accounts 
            SET Balance = Balance + %s 
            WHERE Account_Number = %s
        """, (loan['Amount'], loan['Account_Number']))
        
        # Record the loan disbursement transaction
        cursor.execute("""
            INSERT INTO transactions (Account_Number, Transaction_Type, Amount, Description, Timestamp)
            VALUES (%s, 'Deposit', %s, %s, NOW())
        """, (loan['Account_Number'], loan['Amount'], f"Loan Disbursement for Loan #{loan_id}"))
        
        conn.commit()
        flash('Loan approved and amount disbursed successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject/loan/<int:loan_id>')
@login_required
def reject_loan(loan_id):
    if not isinstance(current_user, User) or current_user.role != 'admin':
        flash('Access denied. Please log in as an admin.', 'danger')
        return redirect(url_for('login'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE loans 
            SET Status = 'Rejected' 
            WHERE Loan_ID = %s
        """, (loan_id,))
        conn.commit()
        flash('Loan rejected successfully!', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    # Get pending accounts with formatted date
    cursor.execute("""
        SELECT a.*, c.Name, c.Email, b.Name as Bank_Name,
               DATE_FORMAT(a.Date_Opened, '%Y-%m-%d %H:%i:%s') as Date_Applied
        FROM accounts a 
        JOIN customers c ON a.Customer_ID = c.Customer_ID 
        JOIN bank b ON a.Bank_ID = b.Bank_ID
        WHERE a.Status = 'Pending'
        ORDER BY a.Date_Opened DESC
    """)
    pending_accounts = cursor.fetchall()
    
    # Get pending loans
    cursor.execute("""
        SELECT l.*, c.Name, c.Email, 
               DATE_FORMAT(l.Application_Date, '%Y-%m-%d %H:%i:%s') as Date_Applied
        FROM loans l 
        JOIN customers c ON l.Customer_ID = c.Customer_ID 
        WHERE l.Status = 'Pending'
        ORDER BY l.Application_Date DESC
    """)
    pending_loans = cursor.fetchall()
    
    # Get recent transactions
    cursor.execute("""
        SELECT t.*, 
               a.Account_Number as From_Account,
               CASE 
                   WHEN t.Transaction_Type = 'Transfer' AND t.Description LIKE 'Transfer to%' THEN 
                       REGEXP_SUBSTR(t.Description, '[0-9]+')
                   ELSE NULL 
               END as To_Account,
               DATE_FORMAT(t.Timestamp, '%Y-%m-%d %H:%i:%s') as Date
        FROM transactions t 
        JOIN accounts a ON t.Account_Number = a.Account_Number 
        ORDER BY t.Timestamp DESC 
        LIMIT 5
    """)
    recent_transactions = cursor.fetchall()
    
    # Get active loans count
    cursor.execute("SELECT COUNT(*) as count FROM loans WHERE Status = 'Approved'")
    active_loans = cursor.fetchone()['count']
    
    # Get active investments count
    cursor.execute("SELECT COUNT(*) as count FROM investments WHERE Status = 'Active'")
    active_investments = cursor.fetchone()['count']
    
    # Get today's transactions count
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM transactions 
        WHERE DATE(Timestamp) = CURDATE()
    """)
    today_transactions = cursor.fetchone()['count']
    
    cursor.close()
    conn.close()
    
    return render_template('admin_dashboard.html', 
                         pending_accounts=pending_accounts,
                         pending_loans=pending_loans,
                         recent_transactions=recent_transactions,
                         active_loans=active_loans,
                         active_investments=active_investments,
                         today_transactions=today_transactions)

@app.route('/customer/dashboard')
@login_required
def customer_dashboard():
    if not isinstance(current_user, User):
        flash('Access denied. Please log in as a customer.', 'danger')
        return redirect(url_for('login'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    # Fetch customer name
    cursor.execute("SELECT Name FROM customers WHERE Customer_ID = %s", (current_user.id,))
    customer_row = cursor.fetchone()
    customer_name = customer_row['Name'] if customer_row else ''
    
    # Get customer's active accounts with bank names
    cursor.execute("""
        SELECT a.*, b.Name 
        FROM accounts a 
        JOIN bank b ON a.Bank_ID = b.Bank_ID 
        WHERE a.Customer_ID = %s AND a.Status = 'Active'
    """, (current_user.id,))
    accounts = cursor.fetchall()
    
    # Get customer's pending accounts
    cursor.execute("""
        SELECT a.*, b.Name 
        FROM accounts a 
        JOIN bank b ON a.Bank_ID = b.Bank_ID 
        WHERE a.Customer_ID = %s AND a.Status = 'Pending'
    """, (current_user.id,))
    pending_accounts = cursor.fetchall()
    
    # Get customer's loans with bank names
    cursor.execute("""
        SELECT l.*, b.Name 
        FROM loans l 
        JOIN accounts a ON l.Account_Number = a.Account_Number 
        JOIN bank b ON a.Bank_ID = b.Bank_ID 
        WHERE l.Customer_ID = %s
    """, (current_user.id,))
    loans = cursor.fetchall()
    
    # Get customer's investments
    cursor.execute("""
        SELECT i.*, c.Name as Customer_Name
        FROM investments i
        JOIN customers c ON i.Customer_ID = c.Customer_ID
        WHERE i.Customer_ID = %s
        ORDER BY i.Start_Date DESC
    """, (current_user.id,))
    investments = cursor.fetchall()
    
    # Calculate days remaining and progress for each investment
    for investment in investments:
        investment['days_remaining'] = (investment['Maturity_Date'] - datetime.now().date()).days
        investment['progress'] = min(100, max(0, 100 - (investment['days_remaining'] / 
            ((investment['Maturity_Date'] - investment['Start_Date']).days) * 100)))
    
    cursor.close()
    conn.close()
    
    return render_template('customer_dashboard.html', 
                         accounts=accounts, 
                         pending_accounts=pending_accounts,
                         loans=loans,
                         investments=investments,
                         customer_name=customer_name)

@app.route('/customer/transactions/<int:account_id>')
@login_required
def view_transactions(account_id):
    if not isinstance(current_user, User):
        flash('Access denied. Please log in as a customer.', 'danger')
        return redirect(url_for('login'))
    
    # Verify account belongs to customer
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.*, b.Name 
        FROM accounts a 
        JOIN bank b ON a.Bank_ID = b.Bank_ID 
        WHERE a.Account_Number = %s AND a.Customer_ID = %s
    """, (account_id, current_user.id))
    account = cursor.fetchone()
    
    if not account:
        flash('Account not found or access denied', 'danger')
        return redirect(url_for('customer_dashboard'))
    
    # Get transactions for the account with account details for transfers
    cursor.execute("""
        SELECT t.*, 
               CASE 
                   WHEN t.Transaction_Type = 'Transfer' AND t.Description LIKE 'Transfer from%' THEN 
                       REGEXP_SUBSTR(t.Description, '[0-9]+')
                   WHEN t.Transaction_Type = 'Transfer' AND t.Description LIKE 'Transfer to%' THEN 
                       REGEXP_SUBSTR(t.Description, '[0-9]+')
                   ELSE NULL 
               END as Related_Account,
               CASE 
                   WHEN t.Transaction_Type = 'Transfer' AND t.Description LIKE 'Transfer from%' THEN 'To'
                   WHEN t.Transaction_Type = 'Transfer' AND t.Description LIKE 'Transfer to%' THEN 'From'
                   ELSE NULL 
               END as Transfer_Direction
        FROM transactions t 
        WHERE t.Account_Number = %s 
        ORDER BY t.Timestamp DESC 
        LIMIT 50
    """, (account_id,))
    transactions = cursor.fetchall()
    
    # Get account details for transfers
    for transaction in transactions:
        if transaction['Related_Account']:
            cursor.execute("""
                SELECT a.Account_Number, c.Name as Customer_Name, b.Name as Bank_Name
                FROM accounts a
                JOIN customers c ON a.Customer_ID = c.Customer_ID
                JOIN bank b ON a.Bank_ID = b.Bank_ID
                WHERE a.Account_Number = %s
            """, (transaction['Related_Account'],))
            related_account = cursor.fetchone()
            if related_account:
                transaction['Related_Account_Details'] = related_account
            else:
                transaction['Related_Account_Details'] = {
                    'Account_Number': transaction['Related_Account'],
                    'Customer_Name': 'Unknown',
                    'Bank_Name': 'Unknown'
                }
    
    cursor.close()
    conn.close()
    
    return render_template('view_transactions.html', account=account, transactions=transactions)

@app.route('/customer/transfer/<int:account_id>', methods=['GET', 'POST'])
@login_required
def transfer_money(account_id):
    if not isinstance(current_user, User):
        flash('Access denied. Please log in as a customer.', 'danger')
        return redirect(url_for('login'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    try:
        # Verify account belongs to customer
        cursor.execute("""
            SELECT a.*, b.Name 
            FROM accounts a 
            JOIN bank b ON a.Bank_ID = b.Bank_ID 
            WHERE a.Account_Number = %s AND a.Customer_ID = %s
        """, (account_id, current_user.id))
        source_account = cursor.fetchone()
        if not source_account:
            flash('Account not found or access denied', 'danger')
            return redirect(url_for('customer_dashboard'))
        if request.method == 'POST':
            target_account = request.form.get('target_account')
            amount = request.form.get('amount')
            description = request.form.get('description')
            if not all([target_account, amount, description]):
                flash('Please fill in all fields', 'danger')
                return redirect(url_for('transfer_money', account_id=account_id))
            try:
                amount = float(amount)
                if amount <= 0:
                    flash('Amount must be positive', 'danger')
                    return redirect(url_for('transfer_money', account_id=account_id))
                if amount > source_account['Balance']:
                    flash('Insufficient funds', 'danger')
                    return redirect(url_for('transfer_money', account_id=account_id))
                # Verify target account exists and is not the same as source
                cursor.execute("SELECT * FROM accounts WHERE Account_Number = %s", (target_account,))
                target = cursor.fetchone()
                if not target:
                    flash('Invalid account number', 'danger')
                    return redirect(url_for('transfer_money', account_id=account_id))
                if int(target_account) == int(account_id):
                    flash('Cannot transfer to the same account', 'danger')
                    return redirect(url_for('transfer_money', account_id=account_id))
                # Update source account balance
                cursor.execute("""
                    UPDATE accounts 
                    SET Balance = Balance - %s 
                    WHERE Account_Number = %s
                """, (amount, account_id))
                # Update target account balance
                cursor.execute("""
                    UPDATE accounts 
                    SET Balance = Balance + %s 
                    WHERE Account_Number = %s
                """, (amount, target_account))
                # Record transaction for source account
                cursor.execute("""
                    INSERT INTO transactions (Account_Number, Transaction_Type, Amount, Description, Timestamp)
                    VALUES (%s, 'Transfer', %s, %s, %s)
                """, (account_id, amount, f"Transfer to {target_account}: {description}", datetime.now()))
                # Record transaction for target account
                cursor.execute("""
                    INSERT INTO transactions (Account_Number, Transaction_Type, Amount, Description, Timestamp)
                    VALUES (%s, 'Transfer', %s, %s, %s)
                """, (target_account, amount, f"Transfer from {account_id}: {description}", datetime.now()))
                conn.commit()
                flash('Transfer successful!', 'success')
                return redirect(url_for('customer_dashboard'))
            except Exception as e:
                conn.rollback()
                flash(f'Error: {str(e)}', 'danger')
                return redirect(url_for('transfer_money', account_id=account_id))
        return render_template('transfer_money.html', source_account=source_account)
    finally:
        cursor.close()
        conn.close()

@app.route('/customer/security', methods=['GET', 'POST'])
@login_required
def view_security():
    if not isinstance(current_user, User):
        flash('Access denied. Please log in as a customer.', 'danger')
        return redirect(url_for('login'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Verify current password
        cursor.execute("SELECT * FROM customers WHERE Customer_ID = %s", (current_user.id,))
        customer = cursor.fetchone()
        if not check_password_hash(customer['Password'], current_password):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('view_security'))
        
        # Verify new password
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return redirect(url_for('view_security'))
        
        # Update password
        hashed_password = generate_password_hash(new_password)
        cursor.execute("UPDATE customers SET Password = %s WHERE Customer_ID = %s", 
                      (hashed_password, current_user.id))
        conn.commit()
        
        flash('Password updated successfully', 'success')
        return redirect(url_for('customer_dashboard'))
    
    # Get customer's active accounts
    cursor.execute("""
        SELECT a.*, b.Name as Bank_Name 
        FROM accounts a 
        JOIN bank b ON a.Bank_ID = b.Bank_ID 
        WHERE a.Customer_ID = %s AND a.Status = 'Active'
    """, (current_user.id,))
    accounts = cursor.fetchall()
    
    # Get current security settings for each account
    security_settings = {}
    for account in accounts:
        cursor.execute("""
            SELECT Security_Type, Status 
            FROM security 
            WHERE Account_Number = %s
        """, (account['Account_Number'],))
        security_records = cursor.fetchall()
        
        # Convert to dictionary format for easier template access
        account_settings = {}
        for record in security_records:
            account_settings[record['Security_Type']] = record['Status']
        
        security_settings[account['Account_Number']] = account_settings
    
    cursor.close()
    conn.close()
    
    return render_template('security_settings.html', 
                         accounts=accounts,
                         security_settings=security_settings)

@app.route('/customer/security/update/<int:account_number>', methods=['POST'])
@login_required
def update_security_settings(account_number):
    if not isinstance(current_user, User):
        flash('Access denied. Please log in as a customer.', 'danger')
        return redirect(url_for('login'))
    
    # Verify account belongs to customer
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM accounts 
        WHERE Account_Number = %s AND Customer_ID = %s AND Status = 'Active'
    """, (account_number, current_user.id))
    account = cursor.fetchone()
    
    if not account:
        flash('Account not found or access denied', 'danger')
        return redirect(url_for('view_security'))
    
    try:
        # Get form data
        two_factor = 'Active' if request.form.get('two_factor') == 'on' else 'Inactive'
        fraud_alert = 'Active' if request.form.get('fraud_alert') == 'on' else 'Inactive'
        transaction_monitoring = 'Active' if request.form.get('transaction_monitoring') == 'on' else 'Inactive'
        
        # Update Two-Factor Authentication
        cursor.execute("""
            INSERT INTO security (Account_Number, Security_Type, Status, Last_Updated)
            VALUES (%s, 'Two-Factor Authentication', %s, NOW())
            ON DUPLICATE KEY UPDATE Status = %s, Last_Updated = NOW()
        """, (account_number, two_factor, two_factor))
        
        # Update Fraud Alert
        cursor.execute("""
            INSERT INTO security (Account_Number, Security_Type, Status, Last_Updated)
            VALUES (%s, 'Fraud Alert', %s, NOW())
            ON DUPLICATE KEY UPDATE Status = %s, Last_Updated = NOW()
        """, (account_number, fraud_alert, fraud_alert))
        
        # Update Transaction Monitoring
        cursor.execute("""
            INSERT INTO security (Account_Number, Security_Type, Status, Last_Updated)
            VALUES (%s, 'Transaction Monitoring', %s, NOW())
            ON DUPLICATE KEY UPDATE Status = %s, Last_Updated = NOW()
        """, (account_number, transaction_monitoring, transaction_monitoring))
        
        conn.commit()
        flash('Security settings updated successfully', 'success')
        
    except Exception as e:
        conn.rollback()
        flash(f'Error updating security settings: {str(e)}', 'danger')
        
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('view_security'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/customer/pay_loan/<int:loan_id>', methods=['GET', 'POST'])
@login_required
def pay_loan(loan_id):
    if not isinstance(current_user, User):
        flash('Access denied. Please log in as a customer.', 'danger')
        return redirect(url_for('login'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get loan details with bank name
        cursor.execute("""
            SELECT l.*, a.Account_Number as Loan_Account, a.Balance as Loan_Account_Balance, b.Name as Bank_Name,
                   DATEDIFF(l.End_Date, l.Start_Date) as Duration_Days
            FROM loans l 
            JOIN accounts a ON l.Account_Number = a.Account_Number 
            JOIN bank b ON a.Bank_ID = b.Bank_ID
            WHERE l.Loan_ID = %s AND l.Customer_ID = %s AND l.Status = 'Approved'
        """, (loan_id, current_user.id))
        loan = cursor.fetchone()
        
        if not loan:
            flash('Loan not found or access denied', 'danger')
            return redirect(url_for('customer_dashboard'))
        
        # Calculate EMI
        principal = float(loan['Amount'])
        interest_rate = float(loan['Interest_Rate']) / 100  # Convert to decimal
        duration_months = float(loan['Duration_Days']) / 30  # Convert days to months
        
        # EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
        monthly_interest = interest_rate / 12
        emi = principal * monthly_interest * (1 + monthly_interest) ** duration_months
        emi = emi / ((1 + monthly_interest) ** duration_months - 1)
        emi = round(emi, 2)
        
        # Calculate payment schedule
        payment_schedule = []
        remaining_principal = principal
        current_date = loan['Start_Date']
        
        for month in range(int(duration_months)):
            interest_payment = round(remaining_principal * monthly_interest, 2)
            principal_payment = round(emi - interest_payment, 2)
            remaining_principal = round(remaining_principal - principal_payment, 2)
            
            payment_schedule.append({
                'month': month + 1,
                'date': current_date.strftime('%Y-%m-%d'),
                'emi': emi,
                'principal': principal_payment,
                'interest': interest_payment,
                'remaining': remaining_principal
            })
            current_date = current_date.replace(day=1) + timedelta(days=32)
            current_date = current_date.replace(day=1)
        
        # Get payment history with bank names
        cursor.execute("""
            SELECT t.*, a.Account_Number, b.Name as Bank_Name
            FROM transactions t
            JOIN accounts a ON t.Account_Number = a.Account_Number
            JOIN bank b ON a.Bank_ID = b.Bank_ID
            WHERE t.Description LIKE %s
            ORDER BY t.Timestamp DESC
        """, (f'Loan Payment for Loan #{loan_id}%',))
        payment_history = cursor.fetchall()
        
        # Get all active accounts for payment
        cursor.execute("""
            SELECT a.*, b.Name as Bank_Name
            FROM accounts a 
            JOIN bank b ON a.Bank_ID = b.Bank_ID 
            WHERE a.Customer_ID = %s AND a.Status = 'Active'
        """, (current_user.id,))
        accounts = cursor.fetchall()
        
        if request.method == 'POST':
            amount = request.form.get('amount')
            payment_account = request.form.get('payment_account')
            
            if not amount or not payment_account:
                flash('Please fill in all fields', 'danger')
                return redirect(url_for('pay_loan', loan_id=loan_id))
            
            try:
                amount = float(amount)
                if amount <= 0:
                    flash('Amount must be positive', 'danger')
                    return redirect(url_for('pay_loan', loan_id=loan_id))
                
                # Verify payment account belongs to customer and has sufficient balance
                cursor.execute("""
                    SELECT Balance FROM accounts 
                    WHERE Account_Number = %s AND Customer_ID = %s AND Status = 'Active'
                """, (payment_account, current_user.id))
                payment_account_balance = cursor.fetchone()
                
                if not payment_account_balance:
                    flash('Invalid payment account', 'danger')
                    return redirect(url_for('pay_loan', loan_id=loan_id))
                
                if amount > float(payment_account_balance['Balance']):
                    flash('Insufficient funds in selected account', 'danger')
                    return redirect(url_for('pay_loan', loan_id=loan_id))
                
                if amount > float(loan['Amount']):
                    flash('Payment amount cannot exceed loan amount', 'danger')
                    return redirect(url_for('pay_loan', loan_id=loan_id))
                
                # Update payment account balance
                cursor.execute("""
                    UPDATE accounts 
                    SET Balance = Balance - %s 
                    WHERE Account_Number = %s
                """, (amount, payment_account))
                
                # Update loan amount
                cursor.execute("""
                    UPDATE loans 
                    SET Amount = Amount - %s 
                    WHERE Loan_ID = %s
                """, (amount, loan_id))
                
                # Fetch updated loan amount
                cursor.execute("SELECT Amount FROM loans WHERE Loan_ID = %s", (loan_id,))
                remaining_amount = cursor.fetchone()['Amount']
                
                # If loan is fully paid, update status
                if float(remaining_amount) <= 0:
                    cursor.execute("UPDATE loans SET Status = 'Paid' WHERE Loan_ID = %s", (loan_id,))
                
                # Record transaction for payment account
                cursor.execute("""
                    INSERT INTO transactions (Account_Number, Transaction_Type, Amount, Description, Timestamp)
                    VALUES (%s, 'Withdrawal', %s, %s, %s)
                """, (payment_account, amount, f"Loan Payment for Loan #{loan_id}", datetime.now()))
                
                conn.commit()
                flash('Payment successful!', 'success')
                return redirect(url_for('customer_dashboard'))
                
            except ValueError:
                flash('Invalid amount', 'danger')
                return redirect(url_for('pay_loan', loan_id=loan_id))
            except Exception as e:
                conn.rollback()
                flash(f'Error: {str(e)}', 'danger')
                return redirect(url_for('pay_loan', loan_id=loan_id))
        
        return render_template('pay_loan.html', 
                             loan=loan, 
                             accounts=accounts,
                             emi=emi,
                             total_payment=round(emi * duration_months, 2),
                             payment_schedule=payment_schedule,
                             payment_history=payment_history)
        
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/accounts')
@login_required
def view_all_accounts():
    if not isinstance(current_user, User) or current_user.role != 'admin':
        flash('Access denied. Please log in as an admin.', 'danger')
        return redirect(url_for('login'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.*, c.Name as Customer_Name, b.Name as Bank_Name 
        FROM accounts a 
        JOIN customers c ON a.Customer_ID = c.Customer_ID 
        JOIN bank b ON a.Bank_ID = b.Bank_ID
    """)
    accounts = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('admin_accounts.html', accounts=accounts)

@app.route('/admin/loans')
@login_required
def view_all_loans():
    if not isinstance(current_user, User) or current_user.role != 'admin':
        flash('Access denied. Please log in as an admin.', 'danger')
        return redirect(url_for('login'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT l.*, c.Name as Customer_Name, b.Name as Bank_Name 
        FROM loans l 
        JOIN customers c ON l.Customer_ID = c.Customer_ID 
        JOIN accounts a ON l.Account_Number = a.Account_Number 
        JOIN bank b ON a.Bank_ID = b.Bank_ID
    """)
    loans = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('admin_loans.html', loans=loans)

@app.route('/admin/transactions')
@login_required
def view_all_transactions():
    if not isinstance(current_user, User) or current_user.role != 'admin':
        flash('Access denied. Please log in as an admin.', 'danger')
        return redirect(url_for('login'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT t.*, a.Account_Number, a.Balance, c.Name as Customer_Name, b.Name as Bank_Name 
        FROM transactions t 
        JOIN accounts a ON t.Account_Number = a.Account_Number 
        JOIN customers c ON a.Customer_ID = c.Customer_ID 
        JOIN bank b ON a.Bank_ID = b.Bank_ID 
        ORDER BY t.Timestamp DESC 
        LIMIT 100
    """)
    transactions = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('admin_transactions.html', transactions=transactions)

@app.route('/admin/add_amount/<int:account_id>', methods=['GET', 'POST'])
@login_required
def add_amount(account_id):
    if not isinstance(current_user, User) or current_user.role != 'admin':
        flash('Access denied. Please log in as an admin.', 'danger')
        return redirect(url_for('login'))
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT a.*, c.Name as Customer_Name, b.Name as Bank_Name FROM accounts a JOIN customers c ON a.Customer_ID = c.Customer_ID JOIN bank b ON a.Bank_ID = b.Bank_ID WHERE a.Account_Number = %s", (account_id,))
    account = cursor.fetchone()
    if not account:
        flash('Account not found', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        amount = request.form.get('amount')
        try:
            amount = float(amount)
            if amount <= 0:
                flash('Amount must be positive', 'danger')
                return redirect(url_for('add_amount', account_id=account_id))
            cursor.execute("UPDATE accounts SET Balance = Balance + %s WHERE Account_Number = %s", (amount, account_id))
            # Record the deposit as a transaction
            cursor.execute("""
                INSERT INTO transactions (Account_Number, Transaction_Type, Amount, Timestamp)
                VALUES (%s, 'Deposit', %s, %s)
            """, (account_id, amount, datetime.now()))
            conn.commit()
            flash(f'₹{amount} added to account {account_id} successfully!', 'success')
            cursor.close()
            conn.close()
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            conn.rollback()
            flash(f'Error: {str(e)}', 'danger')
            cursor.close()
            conn.close()
            return redirect(url_for('add_amount', account_id=account_id))
    cursor.close()
    conn.close()
    return render_template('admin_add_amount.html', account=account)

@app.route('/admin/account/<int:account_id>/transactions')
@login_required
def admin_view_transactions(account_id):
    if not isinstance(current_user, User) or current_user.role != 'admin':
        flash('Access denied. Please log in as an admin.', 'danger')
        return redirect(url_for('login'))
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.*, b.Name 
        FROM accounts a 
        JOIN bank b ON a.Bank_ID = b.Bank_ID 
        WHERE a.Account_Number = %s
    """, (account_id,))
    account = cursor.fetchone()
    if not account:
        flash('Account not found', 'danger')
        cursor.close()
        conn.close()
        return redirect(url_for('view_all_accounts'))
    
    # Get transactions with related account details for transfers
    cursor.execute("""
        SELECT t.*, 
               CASE 
                   WHEN t.Transaction_Type = 'Transfer' AND t.Description LIKE 'Transfer from%' THEN 
                       REGEXP_SUBSTR(t.Description, '[0-9]+')
                   WHEN t.Transaction_Type = 'Transfer' AND t.Description LIKE 'Transfer to%' THEN 
                       REGEXP_SUBSTR(t.Description, '[0-9]+')
                   ELSE NULL 
               END as Related_Account,
               CASE 
                   WHEN t.Transaction_Type = 'Transfer' AND t.Description LIKE 'Transfer from%' THEN 'To'
                   WHEN t.Transaction_Type = 'Transfer' AND t.Description LIKE 'Transfer to%' THEN 'From'
                   ELSE NULL 
               END as Transfer_Direction
        FROM transactions t 
        WHERE t.Account_Number = %s 
        ORDER BY t.Timestamp DESC 
        LIMIT 50
    """, (account_id,))
    transactions = cursor.fetchall()
    
    # Get account details for transfers
    for transaction in transactions:
        if transaction['Related_Account']:
            cursor.execute("""
                SELECT a.Account_Number, c.Name as Customer_Name, b.Name as Bank_Name
                FROM accounts a
                JOIN customers c ON a.Customer_ID = c.Customer_ID
                JOIN bank b ON a.Bank_ID = b.Bank_ID
                WHERE a.Account_Number = %s
            """, (transaction['Related_Account'],))
            related_account = cursor.fetchone()
            if related_account:
                transaction['Related_Account_Details'] = related_account
            else:
                transaction['Related_Account_Details'] = {
                    'Account_Number': transaction['Related_Account'],
                    'Customer_Name': 'Unknown',
                    'Bank_Name': 'Unknown'
                }
    
    cursor.close()
    conn.close()
    return render_template('view_transactions.html', account=account, transactions=transactions)

@app.route('/admin/security', methods=['GET'])
@login_required
def admin_security_settings():
    if not isinstance(current_user, User) or current_user.role != 'admin':
        flash('Access denied. Please log in as an admin.', 'danger')
        return redirect(url_for('login'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get all accounts with their security settings
        cursor.execute("""
            SELECT a.Account_Number, a.Customer_ID, c.Name as Customer_Name, b.Name as Bank_Name,
                   GROUP_CONCAT(
                       CONCAT(s.Security_Type, ':', s.Status)
                       ORDER BY s.Security_Type
                   ) as Security_Settings
            FROM accounts a
            JOIN customers c ON a.Customer_ID = c.Customer_ID
            JOIN bank b ON a.Bank_ID = b.Bank_ID
            LEFT JOIN security s ON a.Account_Number = s.Account_Number
            WHERE a.Status = 'Active'
            GROUP BY a.Account_Number
        """)
        accounts = cursor.fetchall()
        
        # Process security settings for each account
        for account in accounts:
            security_settings = {}
            if account['Security_Settings']:
                for setting in account['Security_Settings'].split(','):
                    security_type, status = setting.split(':')
                    security_settings[security_type] = status
            account['Security_Settings'] = security_settings
        
        return render_template('admin_security_settings.html', accounts=accounts)
        
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/security/update/<int:account_number>', methods=['POST'])
@login_required
def admin_update_security(account_number):
    if not isinstance(current_user, User) or current_user.role != 'admin':
        flash('Access denied. Please log in as an admin.', 'danger')
        return redirect(url_for('login'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get form data
        two_factor = 'Active' if request.form.get('two_factor') == 'on' else 'Inactive'
        fraud_alert = 'Active' if request.form.get('fraud_alert') == 'on' else 'Inactive'
        transaction_monitoring = 'Active' if request.form.get('transaction_monitoring') == 'on' else 'Inactive'
        
        # Update Two-Factor Authentication
        cursor.execute("""
            INSERT INTO security (Account_Number, Security_Type, Status, Last_Updated)
            VALUES (%s, 'Two-Factor Authentication', %s, NOW())
            ON DUPLICATE KEY UPDATE Status = %s, Last_Updated = NOW()
        """, (account_number, two_factor, two_factor))
        
        # Update Fraud Alert
        cursor.execute("""
            INSERT INTO security (Account_Number, Security_Type, Status, Last_Updated)
            VALUES (%s, 'Fraud Alert', %s, NOW())
            ON DUPLICATE KEY UPDATE Status = %s, Last_Updated = NOW()
        """, (account_number, fraud_alert, fraud_alert))
        
        # Update Transaction Monitoring
        cursor.execute("""
            INSERT INTO security (Account_Number, Security_Type, Status, Last_Updated)
            VALUES (%s, 'Transaction Monitoring', %s, NOW())
            ON DUPLICATE KEY UPDATE Status = %s, Last_Updated = NOW()
        """, (account_number, transaction_monitoring, transaction_monitoring))
        
        conn.commit()
        flash('Security settings updated successfully', 'success')
        
    except Exception as e:
        conn.rollback()
        flash(f'Error updating security settings: {str(e)}', 'danger')
        
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('admin_security_settings'))

@app.route('/admin/investments')
@login_required
def admin_view_investments():
    if not isinstance(current_user, User) or current_user.role != 'admin':
        flash('Access denied. Please log in as an admin.', 'danger')
        return redirect(url_for('login'))
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # First, let's check if the investments table exists and has the correct structure
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM investments
        """)
        count = cursor.fetchone()
        print(f"Number of investments found: {count['count'] if count else 0}")
        
        # If no investments exist, let's add a sample investment
        if count['count'] == 0:
            # Get a sample customer and account
            cursor.execute("SELECT Customer_ID FROM customers LIMIT 1")
            customer = cursor.fetchone()
            if customer:
                cursor.execute("SELECT Account_ID FROM accounts WHERE Customer_ID = %s LIMIT 1", (customer['Customer_ID'],))
                account = cursor.fetchone()
                if account:
                    cursor.execute("""
                        INSERT INTO investments (
                            Customer_ID, Investment_Type, Amount, 
                            Start_Date, Maturity_Date, Monthly_Payment
                        ) VALUES (
                            %s, 'Fixed Deposit', 10000.00,
                            CURDATE(), DATE_ADD(CURDATE(), INTERVAL 1 YEAR),
                            1000.00
                        )
                    """, (customer['Customer_ID'],))
                    conn.commit()
        
        # Get all investments with customer and account details
        cursor.execute("""
            SELECT i.*, 
                   c.Name as Customer_Name,
                   a.Account_Number,
                   b.Name as Bank_Name,
                   DATE_FORMAT(i.Start_Date, '%Y-%m-%d') as Start_Date,
                   DATE_FORMAT(i.Maturity_Date, '%Y-%m-%d') as Maturity_Date
            FROM investments i
            JOIN customers c ON i.Customer_ID = c.Customer_ID
            JOIN accounts a ON i.Payment_Account = a.Account_Number
            JOIN bank b ON a.Bank_ID = b.Bank_ID
            ORDER BY i.Start_Date DESC
        """)
        investments = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('admin_investments.html', investments=investments)
    except mysql.connector.Error as err:
        print(f"Database error in admin_view_investments: {str(err)}")
        flash(f'Database error: {str(err)}', 'danger')
        return redirect(url_for('admin_dashboard'))
    except Exception as e:
        print(f"Error in admin_view_investments: {str(e)}")
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('admin_dashboard'))

@app.route('/customer/investments')
@login_required
def view_investments():
    if not isinstance(current_user, User):
        flash('Access denied. Please log in as a customer.', 'danger')
        return redirect(url_for('login'))
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Get all investments for the current customer
        cursor.execute("""
            SELECT i.*, 
                   a.Account_Number,
                   b.Name as Bank_Name,
                   DATE_FORMAT(i.Start_Date, '%Y-%m-%d') as Start_Date,
                   DATE_FORMAT(i.Maturity_Date, '%Y-%m-%d') as Maturity_Date
            FROM investments i
            JOIN accounts a ON i.Payment_Account = a.Account_Number
            JOIN bank b ON a.Bank_ID = b.Bank_ID
            WHERE i.Customer_ID = %s
            ORDER BY i.Start_Date DESC
        """, (current_user.id,))
        investments = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('customer_investments.html', investments=investments)
    except mysql.connector.Error as err:
        print(f"Database error in view_investments: {str(err)}")
        flash(f'Database error: {str(err)}', 'danger')
        return redirect(url_for('customer_dashboard'))
    except Exception as e:
        print(f"Error in view_investments: {str(e)}")
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('customer_dashboard'))

@app.route('/customer/investments/<int:investment_id>/close', methods=['POST'])
@login_required
def close_investment(investment_id):
    if not isinstance(current_user, User):
        flash('Access denied. Please log in as a customer.', 'danger')
        return redirect(url_for('login'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get investment details
        cursor.execute("""
            SELECT i.*, a.Account_Number, a.Bank_Name
            FROM investments i
            JOIN accounts a ON i.Payment_Account = a.Account_Number
            WHERE i.Investment_ID = %s AND i.Customer_ID = %s AND i.Status = 'Active'
            LIMIT 1
        """, (investment_id, current_user.id))
        investment = cursor.fetchone()
        
        if not investment:
            flash('Investment not found or access denied', 'danger')
            return redirect(url_for('view_investments'))
        
        # Calculate return amount (including any interest/returns)
        return_amount = float(investment['Amount'])
        
        # Update investment status
        cursor.execute("""
            UPDATE investments 
            SET Status = 'Closed'
            WHERE Investment_ID = %s
        """, (investment_id,))
        
        # Add amount back to the original payment account
        cursor.execute("""
            UPDATE accounts 
            SET Balance = Balance + %s 
            WHERE Account_Number = %s
        """, (return_amount, investment['Payment_Account']))
        
        # Record transaction with detailed description
        cursor.execute("""
            INSERT INTO transactions (
                Account_Number, Transaction_Type, Amount, Description, Timestamp
            ) VALUES (%s, 'Deposit', %s, %s, %s)
        """, (
            investment['Payment_Account'],
            return_amount,
            f"Investment closure - {investment['Investment_Type']} (ID: {investment_id}) returned to {investment['Bank_Name']} account",
            datetime.now()
        ))
        
        conn.commit()
        flash('Investment closed successfully! Amount has been returned to your account.', 'success')
        return redirect(url_for('view_investments'))
        
    except Exception as e:
        conn.rollback()
        flash(f'Error closing investment: {str(e)}', 'danger')
        return redirect(url_for('view_investments'))
        
    finally:
        cursor.close()
        conn.close()

@app.route('/customer/investments/new', methods=['GET', 'POST'])
@login_required
def new_investment():
    if not isinstance(current_user, User):
        flash('Access denied. Please log in as a customer.', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        investment_type = request.form['investment_type']
        amount = float(request.form['amount'])
        duration_months = int(request.form['duration_months'])
        account_number = request.form['account_number']
        
        # Get account details with bank name
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT a.*, b.Name as Bank_Name 
            FROM accounts a 
            JOIN bank b ON a.Bank_ID = b.Bank_ID 
            WHERE a.Account_Number = %s AND a.Customer_ID = %s
        """, (account_number, current_user.id))
        account = cursor.fetchone()
        
        if not account:
            flash('Invalid account selected', 'danger')
            return redirect(url_for('new_investment'))
        
        if amount > account['Balance']:
            flash('Insufficient funds in selected account', 'danger')
            return redirect(url_for('new_investment'))
        
        # Calculate investment details
        start_date = datetime.now().strftime('%Y-%m-%d')
        maturity_date = (datetime.now() + timedelta(days=30*duration_months)).strftime('%Y-%m-%d')
        
        # Calculate return rate based on investment type
        if investment_type == 'Stocks':
            return_rate = 12.0  # 12% expected return
        elif investment_type == 'Mutual Fund':
            return_rate = 10.0  # 10% expected return
        else:  # Bonds
            return_rate = 8.0   # 8% expected return
        
        # Calculate monthly payment
        monthly_payment = amount / duration_months
        
        try:
            # Start transaction
            cursor.execute("START TRANSACTION")
            
            # Create investment
            cursor.execute("""
                INSERT INTO investments (
                    Customer_ID, Investment_Type, Amount, Start_Date, 
                    Maturity_Date, Status, Return_Rate, Monthly_Payment,
                    Payment_Account, Bank_Name, Account_Number
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                current_user.id, investment_type, amount, start_date,
                maturity_date, 'Active', return_rate, monthly_payment,
                account_number, account['Bank_Name'], account_number
            ))
            
            investment_id = cursor.lastrowid
            
            # Deduct amount from account
            cursor.execute("""
                UPDATE accounts 
                SET Balance = Balance - %s 
                WHERE Account_Number = %s
            """, (amount, account_number))
            
            # Record transaction
            cursor.execute("""
                INSERT INTO transactions (
                    Account_Number, Transaction_Type, Amount, Description, Timestamp
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                account_number, 'Withdrawal', -amount,
                f'Investment in {investment_type} (ID: {investment_id})',
                datetime.now()
            ))
            
            # Commit transaction
            conn.commit()
            
            flash('Investment created successfully!', 'success')
            return redirect(url_for('view_investments'))
            
        except Exception as e:
            # Rollback transaction on error
            conn.rollback()
            flash(f'Error creating investment: {str(e)}', 'danger')
            return redirect(url_for('new_investment'))
            
        finally:
            cursor.close()
            conn.close()
    
    # GET request - show form
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.*, b.Name as Bank_Name 
        FROM accounts a 
        JOIN bank b ON a.Bank_ID = b.Bank_ID 
        WHERE a.Customer_ID = %s AND a.Status = 'Active'
    """, (current_user.id,))
    accounts = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('new_investment.html', accounts=accounts)

@app.route('/customer/investments/<int:investment_id>')
@login_required
def view_investment_details(investment_id):
    if not isinstance(current_user, User):
        flash('Access denied. Please log in as a customer.', 'danger')
        return redirect(url_for('login'))
    
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Get investment details with customer and account information
        cursor.execute("""
            SELECT i.*, 
                   c.Name as Customer_Name, 
                   a.Account_Number, 
                   b.Name as Bank_Name,
                   DATEDIFF(i.Maturity_Date, CURDATE()) as days_remaining,
                   DATEDIFF(i.Maturity_Date, i.Start_Date) as total_days,
                   (DATEDIFF(CURDATE(), i.Start_Date) / DATEDIFF(i.Maturity_Date, i.Start_Date) * 100) as progress,
                   DATE_FORMAT(i.Start_Date, '%Y-%m-%d') as Start_Date,
                   DATE_FORMAT(i.Maturity_Date, '%Y-%m-%d') as Maturity_Date,
                   CASE 
                       WHEN i.Investment_Type = 'Fixed Deposit' THEN 5.5
                       WHEN i.Investment_Type = 'Recurring Deposit' THEN 6.0
                       WHEN i.Investment_Type = 'Mutual Fund' THEN 8.0
                       ELSE 4.0
                   END as Return_Rate,
                   CASE 
                       WHEN i.Investment_Type = 'Fixed Deposit' THEN 20
                       WHEN i.Investment_Type = 'Recurring Deposit' THEN 25
                       WHEN i.Investment_Type = 'Mutual Fund' THEN 60
                       ELSE 15
                   END as Risk_Level,
                   CASE 
                       WHEN i.Investment_Type = 'Fixed Deposit' THEN 15
                       WHEN i.Investment_Type = 'Recurring Deposit' THEN 20
                       WHEN i.Investment_Type = 'Mutual Fund' THEN 70
                       ELSE 10
                   END as Volatility
            FROM investments i
            JOIN customers c ON i.Customer_ID = c.Customer_ID
            JOIN accounts a ON i.Payment_Account = a.Account_Number
            JOIN bank b ON a.Bank_ID = b.Bank_ID
            WHERE i.Investment_ID = %s AND i.Customer_ID = %s
        """, (investment_id, current_user.id))
        
        investment = cursor.fetchone()
        
        if not investment:
            flash('Investment not found', 'danger')
            return redirect(url_for('view_investments'))
        
        # Calculate additional investment metrics
        investment['Monthly_Payment'] = investment['Amount'] / 12 if not investment['Monthly_Payment'] else investment['Monthly_Payment']
        investment['Expected_Return'] = investment['Amount'] * (1 + (investment['Return_Rate'] / 100))
        investment['Profit'] = investment['Expected_Return'] - investment['Amount']
        
        # Get payment history
        cursor.execute("""
            SELECT t.*, DATE_FORMAT(t.Timestamp, '%Y-%m-%d %H:%i') as Formatted_Time
            FROM transactions t
            WHERE t.Account_Number = %s 
            AND t.Description LIKE %s
            ORDER BY t.Timestamp DESC
        """, (investment['Account_Number'], f"Investment payment for Investment #{investment_id}%"))
        payment_history = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('investment_details.html', 
                             investment=investment,
                             payment_history=payment_history)
        
    except Exception as e:
        print(f"Error in view_investment_details: {str(e)}")
        flash('An error occurred while fetching investment details', 'danger')
        return redirect(url_for('view_investments'))

@app.route('/customer/investments/<int:investment_id>/pay', methods=['GET', 'POST'])
@login_required
def pay_investment(investment_id):
    if not isinstance(current_user, User):
        flash('Access denied. Please log in as a customer.', 'danger')
        return redirect(url_for('login'))
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get investment details
        cursor.execute("""
            SELECT i.*, a.Account_Number, b.Name as Bank_Name
            FROM investments i
            JOIN accounts a ON i.Payment_Account = a.Account_Number
            JOIN bank b ON a.Bank_ID = b.Bank_ID
            WHERE i.Investment_ID = %s AND i.Customer_ID = %s AND i.Status = 'Active'
        """, (investment_id, current_user.id))
        investment = cursor.fetchone()
        
        if not investment:
            flash('Investment not found or access denied', 'danger')
            return redirect(url_for('view_investments'))
        
        if request.method == 'POST':
            amount = request.form.get('amount')
            payment_type = request.form.get('payment_type')
            
            if not amount or not payment_type:
                flash('Please fill in all fields', 'danger')
                return redirect(url_for('pay_investment', investment_id=investment_id))
            
            try:
                amount = float(amount)
                if amount <= 0:
                    flash('Amount must be positive', 'danger')
                    return redirect(url_for('pay_investment', investment_id=investment_id))
                
                # Verify account has sufficient balance
                cursor.execute("""
                    SELECT Balance FROM accounts 
                    WHERE Account_Number = %s AND Customer_ID = %s AND Status = 'Active'
                """, (investment['Account_Number'], current_user.id))
                account = cursor.fetchone()
                
                if not account:
                    flash('Invalid account or account not active', 'danger')
                    return redirect(url_for('pay_investment', investment_id=investment_id))
                
                if amount > float(account['Balance']):
                    flash('Insufficient funds in selected account', 'danger')
                    return redirect(url_for('pay_investment', investment_id=investment_id))
                
                # Deduct amount from account
                cursor.execute("""
                    UPDATE accounts 
                    SET Balance = Balance - %s 
                    WHERE Account_Number = %s
                """, (amount, investment['Account_Number']))
                
                # Update investment amount
                cursor.execute("""
                    UPDATE investments 
                    SET Amount = Amount + %s 
                    WHERE Investment_ID = %s
                """, (amount, investment_id))
                
                # Record transaction
                cursor.execute("""
                    INSERT INTO transactions (
                        Account_Number, Transaction_Type, Amount, Description, Timestamp
                    ) VALUES (%s, 'Withdrawal', %s, %s, %s)
                """, (
                    investment['Account_Number'],
                    amount,
                    f"Investment payment for Investment #{investment_id} - {payment_type}",
                    datetime.now()
                ))
                
                conn.commit()
                flash('Payment successful!', 'success')
                return redirect(url_for('view_investment_details', investment_id=investment_id))
                
            except ValueError:
                flash('Invalid amount', 'danger')
                return redirect(url_for('pay_investment', investment_id=investment_id))
            except Exception as e:
                conn.rollback()
                flash(f'Error: {str(e)}', 'danger')
                return redirect(url_for('pay_investment', investment_id=investment_id))
        
        # Get customer's active accounts for the form
        cursor.execute("""
            SELECT a.*, b.Name as Bank_Name 
            FROM accounts a 
            JOIN bank b ON a.Bank_ID = b.Bank_ID 
            WHERE a.Customer_ID = %s AND a.Status = 'Active'
        """, (current_user.id,))
        accounts = cursor.fetchall()
        
        return render_template('pay_investment.html', 
                             investment=investment,
                             accounts=accounts)
        
    except Exception as e:
        print(f"Error in pay_investment: {str(e)}")
        flash('An error occurred while processing payment', 'danger')
        return redirect(url_for('view_investments'))
        
    finally:
        cursor.close()
        conn.close()

def update_transaction_timestamps():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    try:
        # Get all transactions from today
        cursor.execute("""
            SELECT * FROM transactions 
            WHERE DATE(Timestamp) = CURDATE()
            ORDER BY Transaction_ID
        """)
        transactions = cursor.fetchall()
        
        # Get yesterday's date
        yesterday = datetime.now() - timedelta(days=1)
        
        # Update each transaction's timestamp to yesterday
        for transaction in transactions:
            # Create a new timestamp with yesterday's date and the same time
            new_timestamp = datetime.combine(yesterday.date(), transaction['Timestamp'].time())
            
            # Update the transaction timestamp
            cursor.execute("""
                UPDATE transactions 
                SET Timestamp = %s 
                WHERE Transaction_ID = %s
            """, (new_timestamp, transaction['Transaction_ID']))
        
        conn.commit()
        print("Transaction timestamps updated to yesterday's date")
    except Exception as e:
        print(f"Error updating timestamps: {str(e)}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    update_transaction_timestamps()  # This will run when the app starts
    app.run(debug=True) 