-- Drop existing security table
DROP TABLE IF EXISTS `security`;

-- Create new security table with account-specific settings
CREATE TABLE `security` (
  `Security_ID` int NOT NULL AUTO_INCREMENT,
  `Account_Number` int NOT NULL,
  `Security_Type` enum('Two-Factor Authentication','Fraud Alert','Transaction Monitoring') NOT NULL,
  `Status` enum('Active','Inactive') NOT NULL,
  `Last_Updated` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Security_ID`),
  KEY `Account_Number` (`Account_Number`),
  CONSTRAINT `security_ibfk_1` FOREIGN KEY (`Account_Number`) REFERENCES `accounts` (`Account_Number`) ON DELETE CASCADE,
  CONSTRAINT `unique_account_security_type` UNIQUE (`Account_Number`, `Security_Type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci; 