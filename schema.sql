CREATE TABLE IF NOT EXISTS investments (
    Investment_ID INT AUTO_INCREMENT PRIMARY KEY,
    Customer_ID INT NOT NULL,
    Investment_Type VARCHAR(50) NOT NULL,
    Amount DECIMAL(15,2) NOT NULL,
    Start_Date DATE NOT NULL,
    Maturity_Date DATE NOT NULL,
    Status VARCHAR(20) NOT NULL DEFAULT 'Active',
    Return_Rate DECIMAL(5,2) NOT NULL,
    Monthly_Payment DECIMAL(15,2) NOT NULL,
    Payment_Account VARCHAR(20) NOT NULL,
    Bank_Name VARCHAR(100) NOT NULL,
    Account_Number VARCHAR(20) NOT NULL,
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Updated_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (Customer_ID) REFERENCES customers(Customer_ID),
    FOREIGN KEY (Account_Number) REFERENCES accounts(Account_Number)
);

CREATE TABLE investment_payments (
    Payment_ID INT PRIMARY KEY AUTO_INCREMENT,
    Investment_ID INT NOT NULL,
    Amount DECIMAL(15,2) NOT NULL,
    Payment_Date DATE NOT NULL,
    Status VARCHAR(20) DEFAULT 'Pending',
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Investment_ID) REFERENCES investments(Investment_ID)
); 