-- Add unique constraint to prevent duplicate security settings for the same account and type
ALTER TABLE security
ADD CONSTRAINT unique_account_security_type UNIQUE (Account_Number, Security_Type); 