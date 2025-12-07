# SecureInsights Platform - Complete Setup Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Snowflake Account Setup](#snowflake-account-setup)
3. [Local Development Setup](#local-development-setup)
4. [Snowflake Database Configuration](#snowflake-database-configuration)
5. [Loading Sample Data](#loading-sample-data)
6. [Running the Application](#running-the-application)
7. [Testing the Features](#testing-the-features)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Prerequisites

### Required Accounts & Software
- ✅ **Snowflake Account** (30-day free trial available)
  - Sign up at: https://signup.snowflake.com
  - Select region: AWS US-EAST-1 (recommended for Cortex AI availability)
  - Edition: Enterprise or Business Critical (for Data Clean Rooms)

- ✅ **Python 3.9 or higher**
  - Download from: https://www.python.org/downloads/
  - Verify: `python --version`

- ✅ **Git** (optional but recommended)
  - Download from: https://git-scm.com/

- ✅ **Code Editor** (VS Code recommended)
  - Download from: https://code.visualstudio.com/

### System Requirements
- Operating System: Windows 10+, macOS 10.14+, or Linux
- RAM: 4GB minimum (8GB recommended)
- Disk Space: 500MB for application + data
- Internet Connection: Required for Snowflake access

---

## 🏔️ Snowflake Account Setup

### Step 1: Create Snowflake Trial Account

1. Go to https://signup.snowflake.com
2. Fill in your information:
   - Email: Your work or personal email
   - First Name, Last Name
   - Company: Your company or "Personal Project"
   - Role: Select "Data Analyst" or "Developer"
   
3. **Important Cloud Selection:**
   - Cloud Provider: **AWS** (recommended)
   - Region: **US East (N. Virginia)** or **US West (Oregon)**
   - These regions support Snowflake Cortex AI
   
4. **Edition:** Select **Enterprise** (available in trial)

5. Click "CONTINUE" and wait for account creation email

6. Check your email and click activation link

7. Set your password (remember this!)

### Step 2: Get Your Account Identifier

After logging into Snowflake:

1. Look at your browser URL: `https://[account_identifier].snowflakecomputing.com/...`
2. Copy everything before `.snowflakecomputing.com`
3. Example: `abc12345.us-east-1` or `orgname-accountname`
4. Save this for later configuration

### Step 3: Verify Cortex AI Availability

In Snowflake web UI:

1. Click on **Worksheets** (left sidebar)
2. Click **+ Worksheet** (top right)
3. Run this query:
   ```sql
   SELECT SYSTEM$CORTEX_IS_AVAILABLE('COMPLETE') as cortex_available;
   ```
4. Result should be `true`
5. If `false`, you may need to select a different region

---

## 💻 Local Development Setup

### Step 1: Download/Clone the Project

**Option A: If you have Git:**
```bash
git clone <repository-url>
cd SecureInsights
```

**Option B: Download ZIP:**
1. Download the project ZIP file
2. Extract to a folder (e.g., `C:\Projects\SecureInsights`)
3. Open terminal in that folder

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt.

### Step 3: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- Streamlit (web framework)
- Snowflake connector
- Pandas, Plotly (data/visualization)
- Other required libraries

**Expected output:** Installation of ~20 packages, takes 2-3 minutes

### Step 4: Configure Environment Variables

1. Copy the example environment file:
   ```bash
   # Windows
   copy .env.example .env
   
   # macOS/Linux
   cp .env.example .env
   ```

2. Open `.env` file in a text editor

3. Fill in your Snowflake credentials:
   ```ini
   SNOWFLAKE_ACCOUNT=your_account_identifier
   SNOWFLAKE_USER=your_username
   SNOWFLAKE_PASSWORD=your_password
   SNOWFLAKE_WAREHOUSE=COMPUTE_WH
   SNOWFLAKE_ROLE=ACCOUNTADMIN
   ```

4. **Example:**
   ```ini
   SNOWFLAKE_ACCOUNT=abc12345.us-east-1
   SNOWFLAKE_USER=john.doe@email.com
   SNOWFLAKE_PASSWORD=MySecurePass123!
   SNOWFLAKE_WAREHOUSE=COMPUTE_WH
   SNOWFLAKE_ROLE=ACCOUNTADMIN
   ```

5. Save the file

⚠️ **Security Note:** Never commit `.env` to version control (it's in `.gitignore`)

---

## 🗄️ Snowflake Database Configuration

### Step 1: Open Snowflake Web UI

1. Go to https://app.snowflake.com
2. Login with your credentials
3. Click **Worksheets** in left sidebar
4. Click **+ Worksheet** to create new worksheet

### Step 2: Run Database Setup Scripts

#### Script 1: Create Databases

1. In Snowflake worksheet, open the file:
   - `snowflake/setup/01_create_databases.sql`
   
2. Copy ALL the contents

3. Paste into Snowflake worksheet

4. Click **▶ Run All** (or press Ctrl+Enter / Cmd+Enter repeatedly)

5. **Expected Output:**
   ```
   Databases created: BANK_DB, INSURANCE_DB, RETAIL_DB, CLEANROOM_DB, SECURE_INSIGHTS_DB
   Roles created successfully
   Warehouses created successfully
   ```

6. **Verify:** In left sidebar, you should see your new databases

#### Script 2: Create Data Clean Room

1. Open file: `snowflake/setup/02_create_clean_room.sql`

2. Copy all contents to Snowflake worksheet

3. Run all statements

4. **Expected Output:**
   ```
   Data Clean Room setup complete!
   Views created: CROSS_ORG_RISK, GEOGRAPHIC_RISK, SEGMENT_ANALYSIS
   Tables created: DETECTED_PATTERNS, PATTERN_DETAILS, ALERT_HISTORY
   ```

#### Script 3: Security Policies (Optional for Demo)

For full production setup, run:
- `snowflake/setup/03_security_policies.sql`
- `snowflake/setup/04_streams_tasks.sql`

For hackathon demo, the first two scripts are sufficient.

### Step 3: Verify Setup

Run this verification query in Snowflake:

```sql
-- Check databases
SHOW DATABASES LIKE '%_DB';

-- Check clean room views
SHOW VIEWS IN CLEANROOM_DB.AGGREGATED_VIEWS;

-- Check fraud detection tables
SHOW TABLES IN CLEANROOM_DB.FRAUD_DETECTION;
```

**Expected Results:**
- 5 databases listed
- 3+ views in AGGREGATED_VIEWS schema
- 3 tables in FRAUD_DETECTION schema

---

## 📊 Loading Sample Data

### Option 1: Use Python Data Generators (Recommended)

```bash
# Make sure your virtual environment is activated
# and you're in the project root directory

python data_generators/generate_all_data.py
```

This will:
1. Generate synthetic customer data for all organizations
2. Load data into Snowflake
3. Take 5-10 minutes depending on data size

**Output:**
```
Generating bank customer data... ✓
Generating insurance claims data... ✓
Generating retail transaction data... ✓
Loading data to Snowflake... ✓
Verifying data... ✓

Summary:
- Bank records: 10,000
- Insurance records: 8,000
- Retail records: 12,000
Total: 30,000 records
```

### Option 2: Manual Sample Data (Quick Test)

For quick testing, run this in Snowflake worksheet:

```sql
-- Insert sample data into BANK_DB
USE DATABASE BANK_DB;
USE SCHEMA RISK;

CREATE OR REPLACE TABLE CUSTOMER_RISK_SCORES AS
SELECT
    SEQ4() AS customer_id,
    UNIFORM(18, 75, RANDOM()) AS age,
    TO_VARCHAR(UNIFORM(10001, 10500, RANDOM())) AS zip_code,
    UNIFORM(300, 850, RANDOM()) AS credit_score,
    CASE WHEN UNIFORM(0, 100, RANDOM()) < 8 THEN 1 ELSE 0 END AS default_flag,
    UNIFORM(5, 100, RANDOM()) AS transaction_count,
    UNIFORM(100, 5000, RANDOM()) AS avg_transaction_amount,
    DATEADD(DAY, -UNIFORM(1, 730, RANDOM()), CURRENT_DATE()) AS account_open_date,
    DATEADD(DAY, -UNIFORM(1, 30, RANDOM()), CURRENT_DATE()) AS last_activity_date
FROM TABLE(GENERATOR(ROWCOUNT => 10000));

-- Similar for INSURANCE_DB and RETAIL_DB
-- (Full scripts in snowflake/data/ directory)
```

### Verify Data Loading

```sql
-- Check record counts
SELECT 'Bank' AS source, COUNT(*) AS records FROM BANK_DB.RISK.CUSTOMER_RISK_SCORES
UNION ALL
SELECT 'Insurance', COUNT(*) FROM INSURANCE_DB.RISK.CLAIM_RISK_SCORES
UNION ALL
SELECT 'Retail', COUNT(*) FROM RETAIL_DB.RISK.CUSTOMER_RISK_SCORES;

-- Check clean room view
SELECT * FROM CLEANROOM_DB.AGGREGATED_VIEWS.CROSS_ORG_RISK
LIMIT 10;
```

---

## 🚀 Running the Application

### Step 1: Verify Configuration

```bash
# Check that .env file has correct values
cat .env  # macOS/Linux
type .env  # Windows
```

### Step 2: Start Streamlit Application

```bash
# Make sure you're in project root directory
# and virtual environment is activated

streamlit run app/Home.py
```

**Expected Output:**
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.1.x:8501
```

### Step 3: Open Application

1. Browser should automatically open to `http://localhost:8501`
2. If not, manually navigate to `http://localhost:8501`
3. You should see the **SecureInsights Platform** home page

### Common Startup Issues

**Issue:** "ModuleNotFoundError: No module named 'streamlit'"
- **Solution:** Make sure virtual environment is activated and dependencies are installed

**Issue:** "Cannot connect to Snowflake"
- **Solution:** Check `.env` file has correct credentials
- Test connection in Snowflake web UI first

**Issue:** "Port 8501 already in use"
- **Solution:** Kill existing Streamlit process or use different port:
  ```bash
  streamlit run app/Home.py --server.port 8502
  ```

---

## 🧪 Testing the Features

### Test 1: Home Page

✅ **What to Check:**
- Page loads without errors
- Organization cards display correctly
- Feature descriptions are visible
- Use case tabs work

### Test 2: Cross-Company Insights

1. Click **"Explore Insights"** or navigate to **"Cross-Company Insights"** page

2. **Test Natural Language Query:**
   - Enter: "Which age groups have the highest fraud risk?"
   - Click **"Analyze"**
   - ✅ Should show bar chart and data table
   - ✅ Results should have 6 age groups
   - ✅ AI insight should appear below

3. **Test Geographic Query:**
   - Enter: "Show me high-risk geographic areas"
   - Click **"Analyze"**
   - ✅ Should show scatter plot and bar chart
   - ✅ ZIP codes should be displayed

### Test 3: Fraud Detection

1. Navigate to **"Fraud Detection"** page

2. **Check Alert Dashboard:**
   - ✅ Metrics should show: 12 High, 28 Medium, 45 Low, 156 Resolved
   - ✅ Alert cards display with pattern names
   - ✅ Risk scores visible

3. **Test Alert Interaction:**
   - Click **"View Details"** on any alert
   - ✅ Should show info message
   - Click **"Mark Resolved"**
   - ✅ Should show success message

4. **Check Pattern Analysis Tab:**
   - ✅ Time series chart displays
   - ✅ Pattern distribution chart shows
   - ✅ Pie chart with org involvement displays

### Test 4: Reports

1. Navigate to **"Reports"** page

2. **Test Report Generation:**
   - Select report type: **"Executive Summary"**
   - Select period: **"Last 30 Days"**
   - Check options: Include charts and AI insights
   - Click **"Generate Report"**
   - ✅ Preview should display
   - ✅ Download buttons should appear

3. **Test Download:**
   - Click **"Download CSV"**
   - ✅ File should download
   - Open in Excel/spreadsheet
   - ✅ Should contain sample data

### Test 5: Snowflake Connection (Advanced)

If you want to test with real Snowflake data:

```python
# Create test_connection.py in project root
from app.utils.snowflake_connector import get_connection

conn = get_connection()
if conn.connect():
    print("✅ Connected to Snowflake successfully!")
    
    # Test query
    result = conn.execute_query("""
        SELECT COUNT(*) as total_records
        FROM CLEANROOM_DB.AGGREGATED_VIEWS.CROSS_ORG_RISK
    """)
    
    print(f"Total aggregated records: {result.iloc[0]['TOTAL_RECORDS']}")
else:
    print("❌ Connection failed")
```

Run: `python test_connection.py`

---

## 🔧 Troubleshooting

### Connection Issues

**Problem:** "Could not connect to Snowflake"

**Solutions:**
1. Verify credentials in `.env` file
2. Test login in Snowflake web UI
3. Check if account identifier is correct format
4. Ensure warehouse `COMPUTE_WH` exists
5. Verify network/firewall allows Snowflake connections

**Check with:**
```sql
-- In Snowflake web UI
SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE();
```

### Data Not Showing

**Problem:** Queries return empty results

**Solutions:**
1. Verify data was loaded:
   ```sql
   SELECT COUNT(*) FROM CLEANROOM_DB.AGGREGATED_VIEWS.CROSS_ORG_RISK;
   ```
2. Check if minimum aggregation size met (50 records)
3. Reload sample data if needed

### Streamlit Errors

**Problem:** "This app has encountered an error"

**Solutions:**
1. Check terminal for error messages
2. Verify all Python dependencies installed
3. Restart Streamlit:
   ```bash
   # Press Ctrl+C to stop
   streamlit run app/Home.py
   ```

### Cortex AI Not Working

**Problem:** AI explanations not generating

**Solutions:**
1. Verify Cortex is available in your region:
   ```sql
   SELECT SYSTEM$CORTEX_IS_AVAILABLE('COMPLETE');
   ```
2. If unavailable, use predefined text responses (already in code as fallback)
3. Consider changing Snowflake region

### Performance Issues

**Problem:** Queries are slow

**Solutions:**
1. Increase warehouse size in Snowflake:
   ```sql
   ALTER WAREHOUSE SECURE_INSIGHTS_WH SET WAREHOUSE_SIZE = 'MEDIUM';
   ```
2. Check if warehouse is running:
   ```sql
   SHOW WAREHOUSES;
   ```
3. Resume warehouse if suspended:
   ```sql
   ALTER WAREHOUSE SECURE_INSIGHTS_WH RESUME;
   ```

---

## 🎓 Next Steps

### For Development
1. ✅ Customize the UI/branding in `app/Home.py`
2. ✅ Add more query templates in `Cross_Company_Insights.py`
3. ✅ Extend fraud detection patterns in Snowflake
4. ✅ Add real data connectors for production

### For Demo/Pitch
1. ✅ Review `docs/DEMO_SCRIPT.md` for presentation flow
2. ✅ Practice the 5-minute pitch
3. ✅ Prepare for Q&A scenarios
4. ✅ Record a backup demo video

### For Production
1. ⚠️ Implement proper authentication (OAuth/SSO)
2. ⚠️ Set up row-level security policies
3. ⚠️ Configure audit logging to external storage
4. ⚠️ Set up monitoring and alerting
5. ⚠️ Load real organizational data (with consent)

---

## 📞 Support

### Resources
- **Snowflake Documentation:** https://docs.snowflake.com
- **Streamlit Documentation:** https://docs.streamlit.io
- **Project README:** See `README.md` in root directory

### Contact
- **Project Lead:** [Your Name]
- **Email:** [Your Email]
- **Hackathon:** Snowflake AI for Good 2026

---

**🎉 Congratulations! Your SecureInsights Platform is now ready!**

Proceed to `docs/DEMO_SCRIPT.md` for presentation preparation.
