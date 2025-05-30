-- Add Date_Opened column to accounts table
ALTER TABLE accounts
ADD COLUMN Date_Opened DATETIME DEFAULT CURRENT_TIMESTAMP; 