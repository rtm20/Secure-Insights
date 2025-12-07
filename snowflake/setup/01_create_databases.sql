-- ============================================================================
-- SecureInsights Platform - Database Setup Script
-- Creates all necessary databases, schemas, and warehouses
-- ============================================================================

-- Set context
USE ROLE ACCOUNTADMIN;

-- ============================================================================
-- PART 1: Create Warehouses
-- ============================================================================

-- Main compute warehouse for queries
CREATE WAREHOUSE IF NOT EXISTS SECURE_INSIGHTS_WH
    WITH WAREHOUSE_SIZE = 'SMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Main warehouse for SecureInsights platform';

-- Separate warehouse for data loading
CREATE WAREHOUSE IF NOT EXISTS DATA_LOADING_WH
    WITH WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Warehouse for data loading operations';

-- ============================================================================
-- PART 2: Create Databases for Each Organization
-- ============================================================================

-- Bank Database
CREATE DATABASE IF NOT EXISTS BANK_DB
    COMMENT = 'Metro Bank - Private customer and transaction data';

CREATE SCHEMA IF NOT EXISTS BANK_DB.TRANSACTIONS
    COMMENT = 'Banking transactions and account data';

CREATE SCHEMA IF NOT EXISTS BANK_DB.CUSTOMERS
    COMMENT = 'Customer information (PII protected)';

CREATE SCHEMA IF NOT EXISTS BANK_DB.RISK
    COMMENT = 'Risk assessment and credit scores';

-- Insurance Database
CREATE DATABASE IF NOT EXISTS INSURANCE_DB
    COMMENT = 'SafeGuard Insurance - Private claims and policy data';

CREATE SCHEMA IF NOT EXISTS INSURANCE_DB.CLAIMS
    COMMENT = 'Insurance claims data';

CREATE SCHEMA IF NOT EXISTS INSURANCE_DB.POLICIES
    COMMENT = 'Policy information';

CREATE SCHEMA IF NOT EXISTS INSURANCE_DB.RISK
    COMMENT = 'Risk assessment data';

-- Retail Database
CREATE DATABASE IF NOT EXISTS RETAIL_DB
    COMMENT = 'RetailCorp - Private purchase and return data';

CREATE SCHEMA IF NOT EXISTS RETAIL_DB.TRANSACTIONS
    COMMENT = 'Retail transactions';

CREATE SCHEMA IF NOT EXISTS RETAIL_DB.CUSTOMERS
    COMMENT = 'Customer purchase history';

CREATE SCHEMA IF NOT EXISTS RETAIL_DB.RETURNS
    COMMENT = 'Product returns data';

-- ============================================================================
-- PART 3: Create Clean Room Database (Shared Analytics Zone)
-- ============================================================================

CREATE DATABASE IF NOT EXISTS CLEANROOM_DB
    COMMENT = 'Data Clean Room - Privacy-safe shared analytics';

CREATE SCHEMA IF NOT EXISTS CLEANROOM_DB.AGGREGATED_VIEWS
    COMMENT = 'Aggregated views for cross-organization analysis';

CREATE SCHEMA IF NOT EXISTS CLEANROOM_DB.FRAUD_DETECTION
    COMMENT = 'Fraud pattern detection and alerts';

CREATE SCHEMA IF NOT EXISTS CLEANROOM_DB.APPROVED_FUNCTIONS
    COMMENT = 'Pre-approved analytical functions';

CREATE SCHEMA IF NOT EXISTS CLEANROOM_DB.AUDIT
    COMMENT = 'Query audit logs';

-- ============================================================================
-- PART 4: Create Main Application Database
-- ============================================================================

CREATE DATABASE IF NOT EXISTS SECURE_INSIGHTS_DB
    COMMENT = 'SecureInsights application database';

CREATE SCHEMA IF NOT EXISTS SECURE_INSIGHTS_DB.CONFIG
    COMMENT = 'Application configuration';

CREATE SCHEMA IF NOT EXISTS SECURE_INSIGHTS_DB.AUDIT
    COMMENT = 'Application audit logs';

CREATE SCHEMA IF NOT EXISTS SECURE_INSIGHTS_DB.USERS
    COMMENT = 'User management and permissions';

-- ============================================================================
-- PART 5: Create Roles and Grant Permissions
-- ============================================================================

-- Create roles for different user types
CREATE ROLE IF NOT EXISTS BANK_ANALYST
    COMMENT = 'Analyst role for Metro Bank';

CREATE ROLE IF NOT EXISTS INSURANCE_ANALYST
    COMMENT = 'Analyst role for SafeGuard Insurance';

CREATE ROLE IF NOT EXISTS RETAIL_ANALYST
    COMMENT = 'Analyst role for RetailCorp';

CREATE ROLE IF NOT EXISTS CLEANROOM_ANALYST
    COMMENT = 'Role with access to clean room aggregated data only';

-- Grant warehouse usage
GRANT USAGE ON WAREHOUSE SECURE_INSIGHTS_WH TO ROLE CLEANROOM_ANALYST;
GRANT USAGE ON WAREHOUSE SECURE_INSIGHTS_WH TO ROLE BANK_ANALYST;
GRANT USAGE ON WAREHOUSE SECURE_INSIGHTS_WH TO ROLE INSURANCE_ANALYST;
GRANT USAGE ON WAREHOUSE SECURE_INSIGHTS_WH TO ROLE RETAIL_ANALYST;

-- Grant database access (organizations can only see their own data + clean room)
GRANT USAGE ON DATABASE BANK_DB TO ROLE BANK_ANALYST;
GRANT USAGE ON DATABASE CLEANROOM_DB TO ROLE BANK_ANALYST;

GRANT USAGE ON DATABASE INSURANCE_DB TO ROLE INSURANCE_ANALYST;
GRANT USAGE ON DATABASE CLEANROOM_DB TO ROLE INSURANCE_ANALYST;

GRANT USAGE ON DATABASE RETAIL_DB TO ROLE RETAIL_ANALYST;
GRANT USAGE ON DATABASE CLEANROOM_DB TO ROLE RETAIL_ANALYST;

GRANT USAGE ON DATABASE CLEANROOM_DB TO ROLE CLEANROOM_ANALYST;
GRANT USAGE ON DATABASE SECURE_INSIGHTS_DB TO ROLE CLEANROOM_ANALYST;

-- ============================================================================
-- PART 6: Enable Snowflake Features
-- ============================================================================

-- Enable Cortex AI functions for the account
-- Note: Cortex functions are available in specific regions and require appropriate account setup

-- Verify Cortex availability (commented out - may not be available in all regions yet)
-- SELECT SYSTEM$CORTEX_IS_AVAILABLE('COMPLETE') as cortex_available;

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- List all created databases
SHOW DATABASES LIKE '%DB';

-- List all warehouses
SHOW WAREHOUSES;

-- List all roles
SHOW ROLES LIKE '%ANALYST';

-- Display summary
SELECT 
    'Setup Complete!' as status,
    '✅ Databases created: BANK_DB, INSURANCE_DB, RETAIL_DB, CLEANROOM_DB, SECURE_INSIGHTS_DB' as databases,
    '✅ Roles created: BANK_ANALYST, INSURANCE_ANALYST, RETAIL_ANALYST, CLEANROOM_ANALYST' as roles,
    '✅ Warehouses created: SECURE_INSIGHTS_WH, DATA_LOADING_WH' as warehouses;

-- ============================================================================
-- Next Steps
-- ============================================================================

/*
NEXT STEPS:
1. Run 02_create_clean_room.sql to set up Data Clean Room tables and views
2. Run 03_security_policies.sql to implement row access and masking policies
3. Run 04_streams_tasks.sql to set up automated fraud detection
4. Load sample data using the data generation scripts

For production deployment:
- Configure network policies
- Set up SSO/OAuth authentication
- Enable multi-factor authentication
- Configure audit logging to external storage
- Set up monitoring and alerting
- Review and adjust warehouse sizes based on workload
*/
