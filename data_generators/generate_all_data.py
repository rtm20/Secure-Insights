"""
Generate synthetic data for all organizations
Quick demo data generation for hackathon
"""

import os
from dotenv import load_dotenv
import snowflake.connector
from datetime import datetime, timedelta
import random
from pathlib import Path

# Load .env from project root
env_path = Path(__file__).parent.parent / '.env'
print(f"Loading .env from: {env_path}")
print(f".env exists: {env_path.exists()}")
loaded = load_dotenv(env_path)
print(f"load_dotenv result: {loaded}")

# Debug: print all env vars starting with SNOWFLAKE_
print("\nEnvironment variables loaded:")
for key, value in os.environ.items():
    if key.startswith('SNOWFLAKE_'):
        print(f"  {key}: {value[:20] if value else 'None'}...")

def get_connection():
    """Create Snowflake connection"""
    account = "UXIEUCT-STC92106"
    user = os.getenv('SNOWFLAKE_USER')
    token = os.getenv('SNOWFLAKE_TOKEN')
    password = os.getenv('SNOWFLAKE_PASSWORD')
    
    print(f"Debug - Account: {account}")
    print(f"Debug - User: {user}")
    print(f"Debug - Auth method: {'PAT' if token else 'Password'}")
    
    if token:
        # Use PAT authentication
        return snowflake.connector.connect(
            account=account,
            user=user,
            authenticator='oauth',
            token=token,
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
            role=os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN')
        )
    else:
        # Fall back to password authentication
        return snowflake.connector.connect(
            account=account,
            user=user,
            password=password,
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
            role=os.getenv('SNOWFLAKE_ROLE', 'ACCOUNTADMIN')
        )

def generate_bank_data(conn, num_records=10000):
    """Generate synthetic bank customer data"""
    print(f"Generating {num_records} bank customer records...")
    
    cursor = conn.cursor()
    
    # Create table
    cursor.execute("""
        CREATE OR REPLACE TABLE BANK_DB.RISK.CUSTOMER_RISK_SCORES (
            customer_id NUMBER,
            age NUMBER,
            zip_code STRING,
            credit_score NUMBER,
            default_flag NUMBER,
            transaction_count NUMBER,
            avg_transaction_amount FLOAT,
            account_open_date DATE,
            last_activity_date DATE
        )
    """)
    
    # Generate data using Snowflake's GENERATOR function
    cursor.execute(f"""
        INSERT INTO BANK_DB.RISK.CUSTOMER_RISK_SCORES
        SELECT
            SEQ4() AS customer_id,
            UNIFORM(18, 75, RANDOM()) AS age,
            LPAD(TO_VARCHAR(UNIFORM(100, 999, RANDOM())), 3, '0') AS zip_code,
            UNIFORM(300, 850, RANDOM()) AS credit_score,
            CASE WHEN UNIFORM(0, 100, RANDOM()) < 8 THEN 1 ELSE 0 END AS default_flag,
            UNIFORM(5, 100, RANDOM()) AS transaction_count,
            UNIFORM(100, 5000, RANDOM()) AS avg_transaction_amount,
            DATEADD(DAY, -UNIFORM(1, 730, RANDOM()), CURRENT_DATE()) AS account_open_date,
            DATEADD(DAY, -UNIFORM(1, 30, RANDOM()), CURRENT_DATE()) AS last_activity_date
        FROM TABLE(GENERATOR(ROWCOUNT => {num_records}))
    """)
    
    count = cursor.execute("SELECT COUNT(*) FROM BANK_DB.RISK.CUSTOMER_RISK_SCORES").fetchone()[0]
    print(f"✅ Created {count} bank records")
    
    cursor.close()

def generate_insurance_data(conn, num_records=8000):
    """Generate synthetic insurance claims data"""
    print(f"Generating {num_records} insurance records...")
    
    cursor = conn.cursor()
    
    # Create table
    cursor.execute("""
        CREATE OR REPLACE TABLE INSURANCE_DB.RISK.CLAIM_RISK_SCORES (
            policy_holder_id NUMBER,
            age NUMBER,
            zip_code STRING,
            claim_frequency NUMBER,
            total_claim_amount FLOAT,
            fraud_indicator NUMBER,
            policy_start_date DATE,
            last_claim_date DATE
        )
    """)
    
    # Generate data
    cursor.execute(f"""
        INSERT INTO INSURANCE_DB.RISK.CLAIM_RISK_SCORES
        SELECT
            SEQ4() AS policy_holder_id,
            UNIFORM(18, 75, RANDOM()) AS age,
            LPAD(TO_VARCHAR(UNIFORM(100, 999, RANDOM())), 3, '0') AS zip_code,
            UNIFORM(0, 5, RANDOM()) AS claim_frequency,
            UNIFORM(500, 50000, RANDOM()) AS total_claim_amount,
            CASE WHEN UNIFORM(0, 100, RANDOM()) < 6 THEN 1 ELSE 0 END AS fraud_indicator,
            DATEADD(DAY, -UNIFORM(30, 1460, RANDOM()), CURRENT_DATE()) AS policy_start_date,
            DATEADD(DAY, -UNIFORM(1, 180, RANDOM()), CURRENT_DATE()) AS last_claim_date
        FROM TABLE(GENERATOR(ROWCOUNT => {num_records}))
    """)
    
    count = cursor.execute("SELECT COUNT(*) FROM INSURANCE_DB.RISK.CLAIM_RISK_SCORES").fetchone()[0]
    print(f"✅ Created {count} insurance records")
    
    cursor.close()

def generate_retail_data(conn, num_records=12000):
    """Generate synthetic retail transaction data"""
    print(f"Generating {num_records} retail records...")
    
    cursor = conn.cursor()
    
    # Create table
    cursor.execute("""
        CREATE OR REPLACE TABLE RETAIL_DB.RISK.CUSTOMER_RISK_SCORES (
            customer_id NUMBER,
            age NUMBER,
            zip_code STRING,
            return_rate FLOAT,
            total_purchase_amount FLOAT,
            high_value_returns_flag NUMBER,
            first_purchase_date DATE,
            last_purchase_date DATE
        )
    """)
    
    # Generate data
    cursor.execute(f"""
        INSERT INTO RETAIL_DB.RISK.CUSTOMER_RISK_SCORES
        SELECT
            SEQ4() AS customer_id,
            UNIFORM(18, 75, RANDOM()) AS age,
            LPAD(TO_VARCHAR(UNIFORM(100, 999, RANDOM())), 3, '0') AS zip_code,
            UNIFORM(0, 50, RANDOM()) / 100.0 AS return_rate,
            UNIFORM(200, 20000, RANDOM()) AS total_purchase_amount,
            CASE WHEN UNIFORM(0, 100, RANDOM()) < 5 THEN 1 ELSE 0 END AS high_value_returns_flag,
            DATEADD(DAY, -UNIFORM(30, 1095, RANDOM()), CURRENT_DATE()) AS first_purchase_date,
            DATEADD(DAY, -UNIFORM(1, 60, RANDOM()), CURRENT_DATE()) AS last_purchase_date
        FROM TABLE(GENERATOR(ROWCOUNT => {num_records}))
    """)
    
    count = cursor.execute("SELECT COUNT(*) FROM RETAIL_DB.RISK.CUSTOMER_RISK_SCORES").fetchone()[0]
    print(f"✅ Created {count} retail records")
    
    cursor.close()

def verify_data(conn):
    """Verify data was created successfully"""
    print("\nVerifying data...")
    
    cursor = conn.cursor()
    
    # Check all tables
    results = cursor.execute("""
        SELECT 'Bank' AS source, COUNT(*) AS records 
        FROM BANK_DB.RISK.CUSTOMER_RISK_SCORES
        UNION ALL
        SELECT 'Insurance', COUNT(*) 
        FROM INSURANCE_DB.RISK.CLAIM_RISK_SCORES
        UNION ALL
        SELECT 'Retail', COUNT(*) 
        FROM RETAIL_DB.RISK.CUSTOMER_RISK_SCORES
    """).fetchall()
    
    print("\n📊 Data Summary:")
    print("-" * 40)
    total = 0
    for row in results:
        print(f"  {row[0]}: {row[1]:,} records")
        total += row[1]
    print("-" * 40)
    print(f"  Total: {total:,} records")
    
    # Test clean room view
    print("\nTesting Clean Room aggregation...")
    try:
        result = cursor.execute("""
            SELECT COUNT(*) as agg_records
            FROM CLEANROOM_DB.AGGREGATED_VIEWS.CROSS_ORG_RISK
        """).fetchone()
        
        if result and result[0] > 0:
            print(f"✅ Clean Room view working: {result[0]} aggregated records")
        else:
            print("⚠️  Clean Room view exists but returned no data (may need > 50 records per group)")
    except Exception as e:
        print(f"⚠️  Clean Room view error: {e}")
        print("   Run 02_create_clean_room.sql if not already executed")
    
    cursor.close()

def main():
    """Main execution function"""
    print("=" * 60)
    print("SecureInsights Data Generator")
    print("=" * 60)
    print()
    
    try:
        # Connect to Snowflake
        print("Connecting to Snowflake...")
        conn = get_connection()
        print("✅ Connected successfully!\n")
        
        # Generate data for each organization
        generate_bank_data(conn, num_records=10000)
        generate_insurance_data(conn, num_records=8000)
        generate_retail_data(conn, num_records=12000)
        
        # Verify everything worked
        verify_data(conn)
        
        print("\n" + "=" * 60)
        print("✅ Data generation complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Run: streamlit run app/Home.py")
        print("2. Navigate to Cross-Company Insights")
        print("3. Try a query: 'Which age groups have the highest fraud risk?'")
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your .env file has correct Snowflake credentials")
        print("2. Ensure you've run 01_create_databases.sql")
        print("3. Ensure you've run 02_create_clean_room.sql")
        print("4. Verify warehouse COMPUTE_WH exists and is running")
        
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
