-- Drop the investments table if it exists to recreate it with all columns
DROP TABLE IF EXISTS investment_payments;
DROP TABLE IF EXISTS investments;

-- Create investments table with all required columns
CREATE TABLE investments (
    Investment_ID INT PRIMARY KEY AUTO_INCREMENT,
    Customer_ID INT NOT NULL,
    Investment_Type VARCHAR(50) NOT NULL,
    Amount DECIMAL(15,2) NOT NULL,
    Monthly_Payment DECIMAL(15,2) DEFAULT 0,
    Start_Date DATE NOT NULL,
    Maturity_Date DATE NOT NULL,
    Payment_Account VARCHAR(20) NOT NULL,
    Status VARCHAR(20) DEFAULT 'Active',
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Customer_ID) REFERENCES customers(Customer_ID),
    FOREIGN KEY (Payment_Account) REFERENCES accounts(Account_Number)
);

-- Create investment_payments table
CREATE TABLE investment_payments (
    Payment_ID INT PRIMARY KEY AUTO_INCREMENT,
    Investment_ID INT NOT NULL,
    Amount DECIMAL(15,2) NOT NULL,
    Payment_Date DATE NOT NULL,
    Status VARCHAR(20) DEFAULT 'Pending',
    Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Investment_ID) REFERENCES investments(Investment_ID)
); 