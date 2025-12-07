-- ============================================================================
-- SecureInsights Platform - Data Clean Room Setup
-- Creates clean room tables, views, and aggregation logic
-- ============================================================================

USE ROLE ACCOUNTADMIN;
USE WAREHOUSE SECURE_INSIGHTS_WH;
USE DATABASE CLEANROOM_DB;
USE SCHEMA AGGREGATED_VIEWS;

-- ============================================================================
-- PART 1: Create Privacy-Safe Aggregation Functions
-- ============================================================================

-- Function to ensure minimum aggregation size
CREATE OR REPLACE FUNCTION APPROVED_FUNCTIONS.CHECK_MIN_COUNT(count_val NUMBER)
RETURNS BOOLEAN
AS
$$
    count_val >= 50  -- Minimum privacy threshold
$$;

-- Function to add differential privacy noise
CREATE OR REPLACE FUNCTION APPROVED_FUNCTIONS.ADD_DP_NOISE(value FLOAT, epsilon FLOAT)
RETURNS FLOAT
AS
$$
    value + (NORMAL(0, 1/epsilon, RANDOM()))  -- Laplace noise approximation
$$;

-- ============================================================================
-- PART 2: Cross-Organization Risk Aggregation View
-- ============================================================================

CREATE OR REPLACE SECURE VIEW AGGREGATED_VIEWS.CROSS_ORG_RISK AS
WITH bank_risk AS (
    SELECT
        CASE 
            WHEN age BETWEEN 18 AND 24 THEN '18-24'
            WHEN age BETWEEN 25 AND 34 THEN '25-34'
            WHEN age BETWEEN 35 AND 44 THEN '35-44'
            WHEN age BETWEEN 45 AND 54 THEN '45-54'
            WHEN age BETWEEN 55 AND 64 THEN '55-64'
            ELSE '65+'
        END AS age_group,
        SUBSTR(zip_code, 1, 3) AS zip_code_prefix,
        credit_score,
        default_flag,
        SHA2(customer_id) AS customer_id_hash,  -- Hash for privacy
        transaction_count,
        avg_transaction_amount,
        account_open_date,
        last_activity_date
    FROM BANK_DB.RISK.CUSTOMER_RISK_SCORES
),
insurance_risk AS (
    SELECT
        CASE 
            WHEN age BETWEEN 18 AND 24 THEN '18-24'
            WHEN age BETWEEN 25 AND 34 THEN '25-34'
            WHEN age BETWEEN 35 AND 44 THEN '35-34'
            WHEN age BETWEEN 45 AND 54 THEN '45-54'
            WHEN age BETWEEN 55 AND 64 THEN '55-64'
            ELSE '65+'
        END AS age_group,
        SUBSTR(zip_code, 1, 3) AS zip_code_prefix,
        claim_frequency,
        total_claim_amount,
        SHA2(policy_holder_id) AS customer_id_hash,
        fraud_indicator,
        policy_start_date,
        last_claim_date
    FROM INSURANCE_DB.RISK.CLAIM_RISK_SCORES
),
retail_risk AS (
    SELECT
        CASE 
            WHEN age BETWEEN 18 AND 24 THEN '18-24'
            WHEN age BETWEEN 25 AND 34 THEN '25-34'
            WHEN age BETWEEN 35 AND 44 THEN '35-44'
            WHEN age BETWEEN 45 AND 54 THEN '45-54'
            WHEN age BETWEEN 55 AND 64 THEN '55-64'
            ELSE '65+'
        END AS age_group,
        SUBSTR(zip_code, 1, 3) AS zip_code_prefix,
        return_rate,
        total_purchase_amount,
        SHA2(customer_id) AS customer_id_hash,
        high_value_returns_flag,
        first_purchase_date,
        last_purchase_date
    FROM RETAIL_DB.RISK.CUSTOMER_RISK_SCORES
),
combined_data AS (
    SELECT
        b.age_group,
        b.zip_code_prefix,
        b.customer_id_hash,
        -- Calculate composite risk score
        CASE
            WHEN b.default_flag = 1 AND i.fraud_indicator = 1 THEN 95
            WHEN b.default_flag = 1 OR i.fraud_indicator = 1 THEN 80
            WHEN r.high_value_returns_flag = 1 THEN 70
            WHEN b.credit_score < 600 THEN 65
            WHEN i.claim_frequency > 3 THEN 60
            ELSE 40
        END AS risk_score,
        COALESCE(i.total_claim_amount, 0) AS claim_amount,
        CASE WHEN b.default_flag = 1 THEN 1.0 ELSE 0.0 END AS default_rate,
        CASE WHEN i.fraud_indicator = 1 OR r.high_value_returns_flag = 1 THEN 1 ELSE 0 END AS fraud_flag,
        LEAST(b.account_open_date, i.policy_start_date, r.first_purchase_date) AS first_seen_date,
        GREATEST(b.last_activity_date, i.last_claim_date, r.last_purchase_date) AS last_seen_date
    FROM bank_risk b
    LEFT JOIN insurance_risk i 
        ON b.customer_id_hash = i.customer_id_hash 
        AND b.age_group = i.age_group
    LEFT JOIN retail_risk r 
        ON b.customer_id_hash = r.customer_id_hash 
        AND b.age_group = r.age_group
)
SELECT
    age_group,
    zip_code_prefix,
    COUNT(*) AS record_count,
    AVG(risk_score) AS avg_risk_score,
    AVG(claim_amount) AS avg_claim_amount,
    AVG(default_rate) AS avg_default_rate,
    SUM(fraud_flag) AS fraud_cases,
    MIN(first_seen_date) AS earliest_record,
    MAX(last_seen_date) AS latest_record
FROM combined_data
GROUP BY age_group, zip_code_prefix
HAVING COUNT(*) >= 50  -- Privacy: minimum aggregation size
ORDER BY avg_risk_score DESC;

-- Grant access to clean room analysts
GRANT SELECT ON CLEANROOM_DB.AGGREGATED_VIEWS.CROSS_ORG_RISK TO ROLE CLEANROOM_ANALYST;

-- ============================================================================
-- PART 3: Geographic Risk View
-- ============================================================================

CREATE OR REPLACE SECURE VIEW AGGREGATED_VIEWS.GEOGRAPHIC_RISK AS
SELECT
    zip_code_prefix,
    COUNT(*) AS unique_customer_count,
    AVG(avg_risk_score) AS avg_risk_score,
    SUM(fraud_cases) AS total_fraud_cases,
    ROUND(SUM(fraud_cases) * 100.0 / SUM(record_count), 2) AS fraud_rate_pct,
    CURRENT_TIMESTAMP() AS analysis_date
FROM AGGREGATED_VIEWS.CROSS_ORG_RISK
WHERE record_count >= 50
GROUP BY zip_code_prefix
HAVING COUNT(*) >= 3
ORDER BY avg_risk_score DESC;

GRANT SELECT ON CLEANROOM_DB.AGGREGATED_VIEWS.GEOGRAPHIC_RISK TO ROLE CLEANROOM_ANALYST;

-- ============================================================================
-- PART 4: Time Series Risk Table
-- ============================================================================

CREATE OR REPLACE TABLE AGGREGATED_VIEWS.TIME_SERIES_RISK (
    time_period DATE,
    age_group STRING,
    zip_code_prefix STRING,
    total_events INTEGER,
    fraud_cases INTEGER,
    avg_risk_score FLOAT,
    organization_count INTEGER,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ============================================================================
-- PART 5: Fraud Pattern Detection Tables
-- ============================================================================

USE SCHEMA FRAUD_DETECTION;

-- Table to store detected patterns
CREATE OR REPLACE TABLE FRAUD_DETECTION.DETECTED_PATTERNS (
    pattern_id STRING PRIMARY KEY,
    pattern_type STRING NOT NULL,
    pattern_description STRING,
    organization_count INTEGER,
    affected_segment_count INTEGER,
    risk_level INTEGER,  -- Should be between 0 and 100
    confidence_score FLOAT,  -- Should be between 0 and 1
    first_detected TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    last_updated TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    status STRING DEFAULT 'ACTIVE',  -- ACTIVE, RESOLVED, FALSE_POSITIVE
    detection_method STRING
);

-- Table to store pattern details (while maintaining privacy)
CREATE OR REPLACE TABLE FRAUD_DETECTION.PATTERN_DETAILS (
    detail_id STRING PRIMARY KEY,
    pattern_id STRING NOT NULL,
    age_group STRING,
    zip_code_prefix STRING,
    risk_indicators VARIANT,  -- JSON with aggregated indicators
    affected_count INTEGER,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    FOREIGN KEY (pattern_id) REFERENCES FRAUD_DETECTION.DETECTED_PATTERNS(pattern_id)
);

-- Alert history table
CREATE OR REPLACE TABLE FRAUD_DETECTION.ALERT_HISTORY (
    alert_id STRING PRIMARY KEY,
    pattern_id STRING,
    alert_level STRING,  -- HIGH, MEDIUM, LOW
    sent_to_organizations ARRAY,
    sent_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    acknowledged_by ARRAY,
    resolved_at TIMESTAMP_NTZ,
    resolution_notes STRING,
    FOREIGN KEY (pattern_id) REFERENCES FRAUD_DETECTION.DETECTED_PATTERNS(pattern_id)
);

GRANT SELECT ON ALL TABLES IN SCHEMA FRAUD_DETECTION TO ROLE CLEANROOM_ANALYST;

-- ============================================================================
-- PART 6: Create Sample Detected Patterns (for demo)
-- ============================================================================

INSERT INTO FRAUD_DETECTION.DETECTED_PATTERNS 
(pattern_id, pattern_type, pattern_description, organization_count, affected_segment_count, risk_level, confidence_score, status, detection_method)
VALUES
('PAT-2024-001', 'Multiple Claims + Defaults', 'Simultaneous insurance claims and loan defaults in same demographic segment', 3, 450, 87, 0.92, 'ACTIVE', 'Cross-correlation analysis'),
('PAT-2024-002', 'Rapid Account Openings', 'Multiple account openings across organizations in short time period', 2, 320, 82, 0.88, 'ACTIVE', 'Temporal pattern detection'),
('PAT-2024-003', 'Geographic Anomalies', 'Unusual transaction patterns in specific ZIP codes', 3, 580, 68, 0.85, 'ACTIVE', 'Geographic clustering'),
('PAT-2024-004', 'Return Fraud Pattern', 'High-value purchases followed by returns across retail and financial institutions', 2, 210, 65, 0.81, 'ACTIVE', 'Behavioral analysis'),
('PAT-2024-005', 'Identity Indicators', 'Multiple accounts with similar but not identical personal information', 3, 380, 78, 0.87, 'ACTIVE', 'Fuzzy matching');

-- ============================================================================
-- PART 7: Segment Analysis View
-- ============================================================================

USE SCHEMA AGGREGATED_VIEWS;

CREATE OR REPLACE SECURE VIEW AGGREGATED_VIEWS.SEGMENT_ANALYSIS AS
SELECT
    age_group AS segment_value,
    'age_group' AS segment_type,
    COUNT(*) AS segment_size,
    AVG(avg_risk_score) AS avg_risk_score,
    SUM(fraud_cases) AS total_fraud_cases,
    AVG(avg_claim_amount) AS avg_claim_amount,
    CASE 
        WHEN AVG(avg_risk_score) > 70 THEN 1
        ELSE 0
    END AS high_risk_flag
FROM AGGREGATED_VIEWS.CROSS_ORG_RISK
GROUP BY age_group
HAVING COUNT(*) >= 50

UNION ALL

SELECT
    zip_code_prefix AS segment_value,
    'zip_code' AS segment_type,
    COUNT(*) AS segment_size,
    AVG(avg_risk_score) AS avg_risk_score,
    SUM(fraud_cases) AS total_fraud_cases,
    AVG(avg_claim_amount) AS avg_claim_amount,
    CASE 
        WHEN AVG(avg_risk_score) > 70 THEN 1
        ELSE 0
    END AS high_risk_flag
FROM AGGREGATED_VIEWS.CROSS_ORG_RISK
GROUP BY zip_code_prefix
HAVING COUNT(*) >= 50;

GRANT SELECT ON CLEANROOM_DB.AGGREGATED_VIEWS.SEGMENT_ANALYSIS TO ROLE CLEANROOM_ANALYST;

-- ============================================================================
-- Verification
-- ============================================================================

-- Check created objects
SHOW VIEWS IN SCHEMA AGGREGATED_VIEWS;
SHOW TABLES IN SCHEMA FRAUD_DETECTION;
SHOW FUNCTIONS IN SCHEMA APPROVED_FUNCTIONS;

SELECT 'Data Clean Room setup complete!' AS status,
       '✅ Privacy-safe views created' AS views_status,
       '✅ Fraud detection tables ready' AS tables_status,
       '✅ Minimum aggregation size: 50 records' AS privacy_status;

-- ============================================================================
-- Next Steps
-- ============================================================================

/*
NEXT STEPS:
1. Run 03_security_policies.sql to add row-level security and masking
2. Run 04_streams_tasks.sql to enable automated fraud detection
3. Load sample data into source databases
4. Test queries to ensure privacy compliance

USAGE EXAMPLE:
SELECT * FROM CLEANROOM_DB.AGGREGATED_VIEWS.CROSS_ORG_RISK
WHERE age_group = '25-34'
ORDER BY avg_risk_score DESC
LIMIT 10;
*/
