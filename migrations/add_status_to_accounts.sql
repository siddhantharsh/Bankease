-- Add Status column to accounts table
ALTER TABLE accounts
ADD COLUMN Status ENUM('Active', 'Pending', 'Rejected') NOT NULL DEFAULT 'Pending'; 