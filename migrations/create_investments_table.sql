-- Create investments table if it doesn't exist
CREATE TABLE IF NOT EXISTS investments (
    Investment_ID INT AUTO_INCREMENT PRIMARY KEY,
    Customer_ID INT NOT NULL,
    Account_ID INT NOT NULL,
    Investment_Type VARCHAR(50) NOT NULL,
    Amount DECIMAL(15,2) NOT NULL,
    Start_Date DATE NOT NULL,
    End_Date DATE NOT NULL,
    Return_Rate DECIMAL(5,2) NOT NULL,
    Expected_Return DECIMAL(15,2) NOT NULL,
    Status ENUM('Active', 'Closed') DEFAULT 'Active',
    Date_Closed DATE,
    FOREIGN KEY (Customer_ID) REFERENCES customers(Customer_ID),
    FOREIGN KEY (Account_ID) REFERENCES accounts(Account_ID)
); 