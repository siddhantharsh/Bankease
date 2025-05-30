CREATE DATABASE  IF NOT EXISTS `bankease` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `bankease`;
-- MySQL dump 10.13  Distrib 8.0.38, for Win64 (x86_64)
--
-- Host: localhost    Database: bankease
-- ------------------------------------------------------
-- Server version	8.0.39

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `accounts`
--

DROP TABLE IF EXISTS `accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `accounts` (
  `Account_Number` int NOT NULL AUTO_INCREMENT,
  `Customer_ID` int NOT NULL,
  `Bank_ID` int NOT NULL,
  `Account_Type` enum('Savings','Current','Fixed Deposit') NOT NULL,
  `Balance` decimal(12,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`Account_Number`),
  KEY `Customer_ID` (`Customer_ID`),
  KEY `Bank_ID` (`Bank_ID`),
  CONSTRAINT `accounts_ibfk_1` FOREIGN KEY (`Customer_ID`) REFERENCES `customers` (`Customer_ID`) ON DELETE CASCADE,
  CONSTRAINT `accounts_ibfk_2` FOREIGN KEY (`Bank_ID`) REFERENCES `bank` (`Bank_ID`) ON DELETE CASCADE,
  CONSTRAINT `chk_balance` CHECK ((`Balance` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts`
--

LOCK TABLES `accounts` WRITE;
/*!40000 ALTER TABLE `accounts` DISABLE KEYS */;
INSERT INTO `accounts` VALUES (1,1,1,'Savings',50000.00),(2,2,2,'Current',75000.50),(3,3,3,'Savings',120000.75),(4,4,4,'Fixed Deposit',250000.00);
/*!40000 ALTER TABLE `accounts` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `check_balance_before_update` BEFORE UPDATE ON `accounts` FOR EACH ROW BEGIN
    IF NEW.Balance < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Account balance cannot be negative.';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Temporary view structure for view `activesecurityaccountsummary`
--

DROP TABLE IF EXISTS `activesecurityaccountsummary`;
/*!50001 DROP VIEW IF EXISTS `activesecurityaccountsummary`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `activesecurityaccountsummary` AS SELECT 
 1 AS `Customer_ID`,
 1 AS `Customer_Name`,
 1 AS `Account_Number`,
 1 AS `Balance`,
 1 AS `Security_Type`,
 1 AS `Status`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `admins`
--

DROP TABLE IF EXISTS `admins`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admins` (
  `Admin_ID` int NOT NULL AUTO_INCREMENT,
  `Bank_ID` int NOT NULL,
  `Name` varchar(100) NOT NULL,
  `Email` varchar(100) NOT NULL,
  `Role` enum('Manager','Loan Officer','Security Officer') NOT NULL,
  PRIMARY KEY (`Admin_ID`),
  UNIQUE KEY `Email` (`Email`),
  KEY `Bank_ID` (`Bank_ID`),
  CONSTRAINT `admins_ibfk_1` FOREIGN KEY (`Bank_ID`) REFERENCES `bank` (`Bank_ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admins`
--

LOCK TABLES `admins` WRITE;
/*!40000 ALTER TABLE `admins` DISABLE KEYS */;
INSERT INTO `admins` VALUES (1,1,'Rajesh Khanna','rajesh.khanna@mail.in','Manager'),(2,2,'Neha Kapoor','neha.kapoor@mail.in','Loan Officer'),(3,3,'Vikas Gupta','vikas.gupta@mail.in','Security Officer'),(4,4,'Anita Das','anita.das@mail.in','Manager');
/*!40000 ALTER TABLE `admins` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `bank`
--

DROP TABLE IF EXISTS `bank`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `bank` (
  `Bank_ID` int NOT NULL AUTO_INCREMENT,
  `Bank_Name` varchar(100) NOT NULL,
  `Branch` varchar(100) NOT NULL,
  `IFSC_Code` varchar(20) NOT NULL,
  PRIMARY KEY (`Bank_ID`),
  UNIQUE KEY `IFSC_Code` (`IFSC_Code`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bank`
--

LOCK TABLES `bank` WRITE;
/*!40000 ALTER TABLE `bank` DISABLE KEYS */;
INSERT INTO `bank` VALUES (1,'State Bank of India','Mumbai Main Branch','SBIN0001234'),(2,'HDFC Bank','Bangalore Indiranagar','HDFC0005678'),(3,'ICICI Bank','Delhi Connaught Place','ICIC0004321'),(4,'Axis Bank','Chennai T Nagar','AXIS0008765');
/*!40000 ALTER TABLE `bank` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `customerloansummary`
--

DROP TABLE IF EXISTS `customerloansummary`;
/*!50001 DROP VIEW IF EXISTS `customerloansummary`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `customerloansummary` AS SELECT 
 1 AS `Customer_ID`,
 1 AS `Name`,
 1 AS `Total_Loan_Amount`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `Customer_ID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) NOT NULL,
  `Email` varchar(100) NOT NULL,
  `Phone` varchar(15) NOT NULL,
  `Address` text NOT NULL,
  `Date_Of_Birth` date NOT NULL,
  PRIMARY KEY (`Customer_ID`),
  UNIQUE KEY `Email` (`Email`),
  UNIQUE KEY `Phone` (`Phone`)
) ENGINE=InnoDB AUTO_INCREMENT=102 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
INSERT INTO `customers` VALUES (1,'Amit Sharma','amit.sharma92@mail.in','9876543210','123, MG Road, Mumbai, Maharashtra','1992-05-14'),(2,'Priya Verma','priya.verma88@mail.in','9823456789','56, Lake View Street, Bangalore, Karnataka','1988-09-22'),(3,'Rahul Mehta','rahul.mehta95@mail.in','9898765432','78, Green Park, Delhi','1995-11-05'),(4,'Sneha Iyer','sneha.iyer90@mail.in','9786543210','45, Besant Nagar, Chennai, Tamil Nadu','1990-07-18');
/*!40000 ALTER TABLE `customers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `highvalueaccounts`
--

DROP TABLE IF EXISTS `highvalueaccounts`;
/*!50001 DROP VIEW IF EXISTS `highvalueaccounts`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `highvalueaccounts` AS SELECT 
 1 AS `Account_Number`,
 1 AS `Name`,
 1 AS `Balance`,
 1 AS `Bank_Name`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `investments`
--

DROP TABLE IF EXISTS `investments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `investments` (
  `Investment_ID` int NOT NULL AUTO_INCREMENT,
  `Customer_ID` int NOT NULL,
  `Investment_Type` enum('Stocks','Mutual Funds','Bonds') NOT NULL,
  `Investment_Amount` decimal(12,2) NOT NULL,
  `Start_Date` date NOT NULL,
  `Maturity_Date` date NOT NULL,
  PRIMARY KEY (`Investment_ID`),
  KEY `Customer_ID` (`Customer_ID`),
  CONSTRAINT `investments_ibfk_1` FOREIGN KEY (`Customer_ID`) REFERENCES `customers` (`Customer_ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `investments`
--

LOCK TABLES `investments` WRITE;
/*!40000 ALTER TABLE `investments` DISABLE KEYS */;
INSERT INTO `investments` VALUES (1,1,'Stocks',100000.00,'2023-01-01','2028-01-01'),(2,2,'Mutual Funds',200000.00,'2022-06-15','2027-06-15'),(3,3,'Bonds',50000.00,'2021-03-10','2026-03-10'),(4,4,'Stocks',250000.00,'2020-12-20','2025-12-20');
/*!40000 ALTER TABLE `investments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `loans`
--

DROP TABLE IF EXISTS `loans`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `loans` (
  `Loan_ID` int NOT NULL AUTO_INCREMENT,
  `Customer_ID` int NOT NULL,
  `Bank_ID` int NOT NULL,
  `Loan_Type` enum('Home','Car','Personal','Business') NOT NULL,
  `Loan_Amount` decimal(12,2) NOT NULL,
  `Interest_Rate` float NOT NULL,
  `Loan_Term` int NOT NULL,
  `Status` enum('Approved','Pending','Rejected') NOT NULL,
  PRIMARY KEY (`Loan_ID`),
  KEY `Customer_ID` (`Customer_ID`),
  KEY `Bank_ID` (`Bank_ID`),
  CONSTRAINT `loans_ibfk_1` FOREIGN KEY (`Customer_ID`) REFERENCES `customers` (`Customer_ID`) ON DELETE CASCADE,
  CONSTRAINT `loans_ibfk_2` FOREIGN KEY (`Bank_ID`) REFERENCES `bank` (`Bank_ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `loans`
--

LOCK TABLES `loans` WRITE;
/*!40000 ALTER TABLE `loans` DISABLE KEYS */;
INSERT INTO `loans` VALUES (1,1,1,'Home',2500000.00,6.5,240,'Approved'),(2,2,2,'Car',800000.00,7.2,60,'Pending'),(3,3,3,'Personal',300000.00,10.5,36,'Rejected'),(4,4,4,'Business',1500000.00,8,120,'Approved');
/*!40000 ALTER TABLE `loans` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payments`
--

DROP TABLE IF EXISTS `payments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payments` (
  `Payment_ID` int NOT NULL AUTO_INCREMENT,
  `Customer_ID` int NOT NULL,
  `Account_Number` int NOT NULL,
  `Payment_Amount` decimal(12,2) NOT NULL,
  `Payment_Date` date NOT NULL,
  `Payment_Type` enum('Credit Card','Bill Payment','Loan EMI') NOT NULL,
  PRIMARY KEY (`Payment_ID`),
  KEY `Customer_ID` (`Customer_ID`),
  KEY `Account_Number` (`Account_Number`),
  CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`Customer_ID`) REFERENCES `customers` (`Customer_ID`) ON DELETE CASCADE,
  CONSTRAINT `payments_ibfk_2` FOREIGN KEY (`Account_Number`) REFERENCES `accounts` (`Account_Number`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payments`
--

LOCK TABLES `payments` WRITE;
/*!40000 ALTER TABLE `payments` DISABLE KEYS */;
INSERT INTO `payments` VALUES (1,1,1,5000.00,'2024-02-01','Credit Card'),(2,2,2,8000.00,'2024-02-05','Bill Payment'),(3,3,3,12000.00,'2024-02-10','Loan EMI'),(4,4,4,15000.00,'2024-02-15','Credit Card');
/*!40000 ALTER TABLE `payments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `security`
--

DROP TABLE IF EXISTS `security`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `security` (
  `Security_ID` int NOT NULL AUTO_INCREMENT,
  `Customer_ID` int NOT NULL,
  `Security_Type` enum('Two-Factor Authentication','Fraud Alert','Transaction Monitoring') NOT NULL,
  `Status` enum('Active','Inactive') NOT NULL,
  `Last_Updated` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Security_ID`),
  KEY `Customer_ID` (`Customer_ID`),
  CONSTRAINT `security_ibfk_1` FOREIGN KEY (`Customer_ID`) REFERENCES `customers` (`Customer_ID`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `security`
--

LOCK TABLES `security` WRITE;
/*!40000 ALTER TABLE `security` DISABLE KEYS */;
INSERT INTO `security` VALUES (1,1,'Two-Factor Authentication','Active','2025-03-07 01:20:18'),(2,2,'Fraud Alert','Active','2025-03-07 01:20:18'),(3,3,'Transaction Monitoring','Inactive','2025-03-07 01:20:18'),(4,4,'Two-Factor Authentication','Active','2025-03-07 01:20:18');
/*!40000 ALTER TABLE `security` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transactionlog`
--

DROP TABLE IF EXISTS `transactionlog`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transactionlog` (
  `Log_ID` int NOT NULL AUTO_INCREMENT,
  `Transaction_ID` int DEFAULT NULL,
  `Log_Message` varchar(255) DEFAULT NULL,
  `Log_Date` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`Log_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transactionlog`
--

LOCK TABLES `transactionlog` WRITE;
/*!40000 ALTER TABLE `transactionlog` DISABLE KEYS */;
/*!40000 ALTER TABLE `transactionlog` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transactions`
--

DROP TABLE IF EXISTS `transactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transactions` (
  `Transaction_ID` int NOT NULL AUTO_INCREMENT,
  `Account_Number` int NOT NULL,
  `Transaction_Type` enum('Deposit','Withdrawal','Transfer') NOT NULL,
  `Amount` decimal(12,2) NOT NULL,
  `Timestamp` datetime DEFAULT CURRENT_TIMESTAMP,
  `Receiver_Account` int DEFAULT NULL,
  PRIMARY KEY (`Transaction_ID`),
  KEY `Account_Number` (`Account_Number`),
  KEY `Receiver_Account` (`Receiver_Account`),
  CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`Account_Number`) REFERENCES `accounts` (`Account_Number`) ON DELETE CASCADE,
  CONSTRAINT `transactions_ibfk_2` FOREIGN KEY (`Receiver_Account`) REFERENCES `accounts` (`Account_Number`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transactions`
--

LOCK TABLES `transactions` WRITE;
/*!40000 ALTER TABLE `transactions` DISABLE KEYS */;
INSERT INTO `transactions` VALUES (1,1,'Deposit',10000.00,'2025-03-07 01:19:01',NULL),(2,2,'Withdrawal',5000.00,'2025-03-07 01:19:01',NULL),(3,3,'Transfer',20000.00,'2025-03-07 01:19:01',1),(4,4,'Deposit',15000.00,'2025-03-07 01:19:01',NULL);
/*!40000 ALTER TABLE `transactions` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `log_transaction_after_insert` AFTER INSERT ON `transactions` FOR EACH ROW BEGIN
    INSERT INTO TransactionLog (Transaction_ID, Log_Message)
    VALUES (NEW.Transaction_ID, CONCAT('New transaction of type ', NEW.Transaction_Type, ' of amount ', NEW.Amount, ' inserted.'));
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Dumping events for database 'bankease'
--

--
-- Dumping routines for database 'bankease'
--
/*!50003 DROP PROCEDURE IF EXISTS `HighBalanceAccountsCursor` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `HighBalanceAccountsCursor`()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE acc_no INT;
    DECLARE acc_balance DECIMAL(10,2);

    -- Cursor and handler declarations must be BEFORE other statements
    DECLARE cur CURSOR FOR
        SELECT Account_Number, Balance FROM Accounts WHERE Balance > 50000;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    -- Now we can safely drop and create the temp table
    DROP TEMPORARY TABLE IF EXISTS TempHighBalance;
    CREATE TEMPORARY TABLE TempHighBalance (
        AccountNumber INT,
        Balance DECIMAL(10,2)
    );

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO acc_no, acc_balance;
        IF done THEN
            LEAVE read_loop;
        END IF;

        INSERT INTO TempHighBalance (AccountNumber, Balance)
        VALUES (acc_no, acc_balance);
    END LOOP;

    CLOSE cur;

    -- Show the result
    SELECT * FROM TempHighBalance;

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `Show_Active_Security_Customers` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `Show_Active_Security_Customers`()
BEGIN
    -- Step 1: Declare variables and cursor FIRST
    DECLARE done INT DEFAULT FALSE;
    DECLARE c_name VARCHAR(100);

    DECLARE cur CURSOR FOR
        SELECT DISTINCT c.Name 
        FROM Customers c
        JOIN Security s ON c.Customer_ID = s.Customer_ID
        WHERE s.Status = 'Active';

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    -- Step 2: Now drop and create temp table
    DROP TEMPORARY TABLE IF EXISTS Active_Security_Customers;

    CREATE TEMPORARY TABLE Active_Security_Customers (
        Customer_Name VARCHAR(100) PRIMARY KEY
    );

    -- Step 3: Cursor logic
    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO c_name;
        IF done THEN
            LEAVE read_loop;
        END IF;

        INSERT IGNORE INTO Active_Security_Customers VALUES (c_name);
    END LOOP;

    CLOSE cur;

    SELECT * FROM Active_Security_Customers;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `SimpleCustomerCursor` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `SimpleCustomerCursor`()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE c_name VARCHAR(100);
    DECLARE cur CURSOR FOR SELECT Name FROM Customers;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO c_name;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Here you can do something with c_name, e.g., SELECT it
        SELECT c_name AS CustomerName;
    END LOOP;

    CLOSE cur;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Final view structure for view `activesecurityaccountsummary`
--

/*!50001 DROP VIEW IF EXISTS `activesecurityaccountsummary`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `activesecurityaccountsummary` AS select `c`.`Customer_ID` AS `Customer_ID`,`c`.`Name` AS `Customer_Name`,`a`.`Account_Number` AS `Account_Number`,`a`.`Balance` AS `Balance`,`s`.`Security_Type` AS `Security_Type`,`s`.`Status` AS `Status` from ((`customers` `c` join `accounts` `a` on((`c`.`Customer_ID` = `a`.`Customer_ID`))) join `security` `s` on((`c`.`Customer_ID` = `s`.`Customer_ID`))) where (`s`.`Status` = 'Active') order by `a`.`Balance` desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `customerloansummary`
--

/*!50001 DROP VIEW IF EXISTS `customerloansummary`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `customerloansummary` AS select `c`.`Customer_ID` AS `Customer_ID`,`c`.`Name` AS `Name`,sum(`l`.`Loan_Amount`) AS `Total_Loan_Amount` from (`customers` `c` join `loans` `l` on((`c`.`Customer_ID` = `l`.`Customer_ID`))) group by `c`.`Customer_ID`,`c`.`Name` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `highvalueaccounts`
--

/*!50001 DROP VIEW IF EXISTS `highvalueaccounts`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `highvalueaccounts` AS select `a`.`Account_Number` AS `Account_Number`,`c`.`Name` AS `Name`,`a`.`Balance` AS `Balance`,`b`.`Bank_Name` AS `Bank_Name` from ((`accounts` `a` join `customers` `c` on((`a`.`Customer_ID` = `c`.`Customer_ID`))) join `bank` `b` on((`a`.`Bank_ID` = `b`.`Bank_ID`))) where (`a`.`Balance` > 100000) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-04 16:46:14
