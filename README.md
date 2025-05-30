# BankEase - Banking Management System

A comprehensive web-based banking management system built with Flask and MySQL that provides a complete suite of banking operations for both customers and administrators.

## Features

### Customer Features
- User registration and authentication
- Account management
  - Apply for new accounts
  - View account details and balance
  - Transfer money between accounts
  - View transaction history
- Loan management
  - Apply for loans
  - View loan details and payment schedule
  - Make loan payments
- Investment management
  - Create new investments (Fixed Deposit, Mutual Funds, etc.)
  - View investment portfolio
  - Track investment progress
  - Make investment payments
- Security features
  - Two-factor authentication
  - Fraud alerts
  - Transaction monitoring

### Admin Features
- Dashboard with overview of system activities
- Account management
  - Approve/reject account applications
  - View all accounts
  - Add funds to accounts
- Loan management
  - Approve/reject loan applications
  - View all loans
- Transaction monitoring
  - View all transactions
  - Monitor suspicious activities
- Security management
  - Configure security settings for accounts
  - Monitor security alerts

## Technology Stack

- **Backend**: Python Flask
- **Database**: MySQL
- **Authentication**: Flask-Login
- **Frontend**: HTML, CSS, JavaScript
- **Security**: Werkzeug Security

## Prerequisites

- Python 3.x
- MySQL Server
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/banking_management.git
cd banking_management
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

3. Set up MySQL database:
- Create a new database named 'bankease'
- Import the database schema (schema.sql)

4. Configure database connection:
- Update the database configuration in `app.py`:
```python
db_config = {
    'host': '127.0.0.1',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'bankease',
    'port': 3306,
    'auth_plugin': 'mysql_native_password'
}
```

5. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Database Schema

The system uses the following main tables:
- customers
- admins
- accounts
- transactions
- loans
- investments
- security
- bank

## Security Features

- Password hashing using Werkzeug Security
- Session management
- Role-based access control
- Transaction monitoring
- Fraud detection
- Two-factor authentication

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask documentation
- MySQL documentation
- Flask-Login documentation 