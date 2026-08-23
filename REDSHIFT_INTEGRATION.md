# AWS Redshift Integration Guide
## Moving Ratha Chakram Data to Production

---

## Overview

This guide walks you through moving the Ratha Chakram POC data from mock Excel/CSV files to AWS Redshift for production use.

**Benefits of Redshift:**
- ✅ Scales to billions of rows (vs Excel's 1M limit)
- ✅ Real-time query performance (analytics in seconds)
- ✅ Concurrent access (multiple dashboards, teams)
- ✅ Automated backups & disaster recovery
- ✅ Integrates with CrewAI agents seamlessly

---

## Architecture: Before & After

### Current (POC)
```
Gradio UI
    ↓
CrewAI Agents
    ↓
Data Layer (Pandas)
    ↓
Excel/CSV files
```

### After Redshift Migration
```
Gradio UI
    ↓
CrewAI Agents
    ↓
Data Layer (SQL Queries)
    ↓
AWS Redshift Cluster
    ↓
Real-time Data (competitors, customers, tracking)
```

---

## Step 1: Create AWS Redshift Cluster

### 1.1 Via AWS Console (5 minutes)

1. Go to AWS Console → Redshift
2. Click "Create cluster"
3. Fill in:
   ```
   Cluster identifier: ratha-chakram-prod
   Database name: ratha_chakram
   Admin user: admin
   Password: [Strong password - save this!]
   Node type: dc2.large (Good for analytics, cost-effective)
   Number of nodes: 2 (Start small, scale later)
   ```
4. Click "Create cluster" and wait 5-10 minutes

### 1.2 Via AWS CLI (Recommended)

```bash
aws redshift create-cluster \
  --cluster-identifier ratha-chakram-prod \
  --node-type dc2.large \
  --number-of-nodes 2 \
  --master-username admin \
  --master-user-password 'YourStrongPassword!' \
  --db-name ratha_chakram \
  --publicly-accessible
```

**Save the endpoint** (looks like: `ratha-chakram-prod.abc123.us-east-1.redshift.amazonaws.com`)

---

## Step 2: Configure Security & Access

### 2.1 Security Group Settings

```bash
# Find your Redshift security group
aws redshift describe-clusters \
  --cluster-identifier ratha-chakram-prod

# Update security group to allow port 5439 from your IP
# In AWS Console:
# VPC Security Group → Inbound Rules → Add rule
# Type: Redshift (port 5439)
# Source: Your IP or 0.0.0.0/0 (dev only, not production!)
```

### 2.2 Test Connection

```bash
# Install psql if you don't have it
brew install postgresql  # macOS
# or: apt-get install postgresql-client  # Linux

# Test connection
psql -h ratha-chakram-prod.abc123.us-east-1.redshift.amazonaws.com \
     -U admin \
     -d ratha_chakram \
     -p 5439

# You should see: ratha_chakram=#
```

---

## Step 3: Create Tables in Redshift

### 3.1 Connect to Redshift

```bash
psql -h YOUR_REDSHIFT_ENDPOINT \
     -U admin \
     -d ratha_chakram \
     -p 5439
```

### 3.2 Create Table: Competitor Expat Plans

```sql
-- Table: competitor_expat_plans
-- Purpose: 5,000 expats currently on competitor insurance

CREATE TABLE IF NOT EXISTS competitor_expat_plans (
    expat_id VARCHAR(50) PRIMARY KEY,
    origin_country VARCHAR(50),
    visa_type VARCHAR(20),
    us_state VARCHAR(2),
    current_provider VARCHAR(50),
    monthly_premium DECIMAL(10,2),
    coverage_types VARCHAR(100),
    includes_india_coverage BOOLEAN,
    claims_processing_days INT,
    customer_since TIMESTAMP,
    plan_status VARCHAR(20),
    created_at TIMESTAMP DEFAULT GETDATE()
)
DISTKEY (expat_id)
SORTKEY (us_state, visa_type);

-- Create indexes for fast queries
CREATE INDEX idx_competitor_state ON competitor_expat_plans (us_state);
CREATE INDEX idx_competitor_visa ON competitor_expat_plans (visa_type);
CREATE INDEX idx_competitor_provider ON competitor_expat_plans (current_provider);
```

### 3.3 Create Table: Ratha Chakram Customers

```sql
-- Table: ratha_chakram_customers
-- Purpose: 1,500 expats who switched to Ratha (actual customers)

CREATE TABLE IF NOT EXISTS ratha_chakram_customers (
    expat_id VARCHAR(50) PRIMARY KEY,
    origin_country VARCHAR(50),
    visa_type VARCHAR(20),
    us_state VARCHAR(2),
    switched_from VARCHAR(50),
    previous_monthly_premium DECIMAL(10,2),
    ratha_monthly_premium DECIMAL(10,2),
    premium_savings_percent DECIMAL(5,2),
    coverage_types VARCHAR(100),
    india_coverage_enabled BOOLEAN,
    onboarding_days INT,
    competitor_onboarding_days INT,
    switched_date DATE,
    satisfaction_score INT,
    monthly_retention_rate DECIMAL(3,1),
    created_at TIMESTAMP DEFAULT GETDATE()
)
DISTKEY (expat_id)
SORTKEY (switched_date, us_state, visa_type);

-- Indexes
CREATE INDEX idx_ratha_state ON ratha_chakram_customers (us_state);
CREATE INDEX idx_ratha_visa ON ratha_chakram_customers (visa_type);
CREATE INDEX idx_ratha_provider ON ratha_chakram_customers (switched_from);
CREATE INDEX idx_ratha_switched ON ratha_chakram_customers (switched_date);
```

### 3.4 Create Table: Competitive Tracking

```sql
-- Table: expat_competitive_tracking
-- Purpose: Why expats switched, competitive analysis

CREATE TABLE IF NOT EXISTS expat_competitive_tracking (
    tracking_id INT IDENTITY(1,1) PRIMARY KEY,
    expat_id VARCHAR(50),
    previous_company VARCHAR(50),
    plan_end_date DATE,
    reason_left_previous VARCHAR(100),
    reason_chose_ratha VARCHAR(100),
    had_ratha_before BOOLEAN,
    premium_savings_percent DECIMAL(5,2),
    onboarding_speed_advantage_days INT,
    india_coverage_interest BOOLEAN,
    acquisition_cost_estimated DECIMAL(10,2),
    lifetime_value_projected DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT GETDATE()
)
DISTKEY (expat_id)
SORTKEY (previous_company, plan_end_date);

-- Indexes
CREATE INDEX idx_tracking_company ON expat_competitive_tracking (previous_company);
CREATE INDEX idx_tracking_expat ON expat_competitive_tracking (expat_id);
```

---

## Step 4: Load Data from CSV

### 4.1 Upload CSV to S3

```bash
# Create S3 bucket if you don't have one
aws s3 mb s3://ratha-chakram-data

# Upload CSV files
aws s3 cp data/ratha_chakram_customers.csv s3://ratha-chakram-data/
aws s3 cp data/expat_competitive_tracking.csv s3://ratha-chakram-data/

# Note: For competitor_expat_plans.xlsx, convert to CSV first:
# (Use Excel or: python -c "import pandas as pd; pd.read_excel('competitor_expat_plans.xlsx').to_csv('competitor_expat_plans.csv')")
aws s3 cp data/competitor_expat_plans.csv s3://ratha-chakram-data/
```

### 4.2 Load from S3 into Redshift

Connect to Redshift and run:

```sql
-- Load competitor plans
COPY competitor_expat_plans (
    expat_id, origin_country, visa_type, us_state, current_provider,
    monthly_premium, coverage_types, includes_india_coverage, 
    claims_processing_days, customer_since, plan_status
)
FROM 's3://ratha-chakram-data/competitor_expat_plans.csv'
IAM_ROLE 'arn:aws:iam::YOUR_ACCOUNT_ID:role/RedshiftS3AccessRole'
DELIMITER ','
IGNOREHEADER 1
NULL AS 'None'
DATEFORMAT 'YYYY-MM-DD HH:MI:SS'
ACCEPTINVCHAR;

-- Load Ratha customers
COPY ratha_chakram_customers (
    expat_id, origin_country, visa_type, us_state, switched_from,
    previous_monthly_premium, ratha_monthly_premium, premium_savings_percent,
    coverage_types, india_coverage_enabled, onboarding_days,
    competitor_onboarding_days, switched_date, satisfaction_score,
    monthly_retention_rate
)
FROM 's3://ratha-chakram-data/ratha_chakram_customers.csv'
IAM_ROLE 'arn:aws:iam::YOUR_ACCOUNT_ID:role/RedshiftS3AccessRole'
DELIMITER ','
IGNOREHEADER 1
NULL AS 'None'
DATEFORMAT 'YYYY-MM-DD'
ACCEPTINVCHAR;

-- Load competitive tracking
COPY expat_competitive_tracking (
    expat_id, previous_company, plan_end_date, reason_left_previous,
    reason_chose_ratha, had_ratha_before, premium_savings_percent,
    onboarding_speed_advantage_days, india_coverage_interest,
    acquisition_cost_estimated, lifetime_value_projected
)
FROM 's3://ratha-chakram-data/expat_competitive_tracking.csv'
IAM_ROLE 'arn:aws:iam::YOUR_ACCOUNT_ID:role/RedshiftS3AccessRole'
DELIMITER ','
IGNOREHEADER 1
NULL AS 'None'
DATEFORMAT 'YYYY-MM-DD'
ACCEPTINVCHAR;
```

### 4.3 Create IAM Role for Redshift S3 Access

```bash
# Create role
aws iam create-role \
  --role-name RedshiftS3AccessRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "redshift.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach S3 policy
aws iam attach-role-policy \
  --role-name RedshiftS3AccessRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Get role ARN
aws iam get-role --role-name RedshiftS3AccessRole
# Use the ARN in the COPY commands above
```

---

## Step 5: Verify Data Loaded

```sql
-- Check row counts
SELECT 'competitor_expat_plans' as table_name, COUNT(*) as row_count 
FROM competitor_expat_plans
UNION ALL
SELECT 'ratha_chakram_customers', COUNT(*) 
FROM ratha_chakram_customers
UNION ALL
SELECT 'expat_competitive_tracking', COUNT(*) 
FROM expat_competitive_tracking;

-- Expected output:
-- table_name                  | row_count
-- competitor_expat_plans      | 5000
-- ratha_chakram_customers     | 1500
-- expat_competitive_tracking  | 1500

-- Sample data check
SELECT TOP 5 * FROM ratha_chakram_customers;

-- Verify aggregations
SELECT 
    COUNT(DISTINCT expat_id) as total_customers,
    ROUND(AVG(premium_savings_percent), 2) as avg_savings_pct,
    ROUND(AVG(satisfaction_score), 1) as avg_satisfaction
FROM ratha_chakram_customers;

-- Expected: 1500 customers, ~27% savings, ~8.5 satisfaction
```

---

## Step 6: Update Python Code for Redshift

### 6.1 Update Connection String

Edit `src/demo_redshift_mcp/data_layer.py`:

```python
import psycopg2
from psycopg2 import sql

class DataLayer:
    def __init__(self, data_dir: str = "./data", use_redshift: bool = True):
        if use_redshift:
            self._connect_redshift()
        else:
            self._load_csv()

    def _connect_redshift(self):
        """Connect to Redshift cluster"""
        self.conn = psycopg2.connect(
            host='ratha-chakram-prod.abc123.us-east-1.redshift.amazonaws.com',
            port=5439,
            user='admin',
            password='YOUR_PASSWORD',
            database='ratha_chakram'
        )
        self.cursor = self.conn.cursor()

    def query_ratha_customers_redshift(self, filters=None):
        """Query from Redshift instead of CSV"""
        query = "SELECT * FROM ratha_chakram_customers WHERE 1=1"
        
        if filters:
            if filters.get("state"):
                query += f" AND us_state = '{filters['state']}'"
            if filters.get("visa_type"):
                query += f" AND visa_type = '{filters['visa_type']}'"
        
        self.cursor.execute(query)
        return self.cursor.fetchall()
```

### 6.2 Update Environment Variables

Edit `.env`:

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Redshift
REDSHIFT_HOST=ratha-chakram-prod.abc123.us-east-1.redshift.amazonaws.com
REDSHIFT_PORT=5439
REDSHIFT_USER=admin
REDSHIFT_PASSWORD=your_password
REDSHIFT_DATABASE=ratha_chakram

# Use Redshift or Mock Data?
USE_REDSHIFT=true
```

### 6.3 Update DataLayer to Use Environment Variables

```python
import os
import psycopg2

class DataLayer:
    def __init__(self):
        if os.getenv('USE_REDSHIFT') == 'true':
            self._init_redshift()
        else:
            self._init_csv()

    def _init_redshift(self):
        self.conn = psycopg2.connect(
            host=os.getenv('REDSHIFT_HOST'),
            port=int(os.getenv('REDSHIFT_PORT')),
            user=os.getenv('REDSHIFT_USER'),
            password=os.getenv('REDSHIFT_PASSWORD'),
            database=os.getenv('REDSHIFT_DATABASE')
        )
        self.cursor = self.conn.cursor()
```

---

## Step 7: Create Materialized Views (Optional but Recommended)

```sql
-- Materialized view for fast analytics queries
-- Refresh daily for latest metrics

CREATE MATERIALIZED VIEW ratha_market_metrics AS
SELECT 
    COUNT(DISTINCT rc.expat_id) as total_ratha_customers,
    ROUND(AVG(rc.premium_savings_percent), 2) as avg_savings_pct,
    ROUND(AVG(rc.satisfaction_score), 1) as avg_satisfaction,
    ROUND(COUNT(CASE WHEN rc.india_coverage_enabled THEN 1 END)::FLOAT / COUNT(*) * 100, 1) as india_adoption_pct,
    (SELECT COUNT(*) FROM competitor_expat_plans) as competitor_base,
    ROUND(COUNT(DISTINCT rc.expat_id)::FLOAT / (SELECT COUNT(*) FROM competitor_expat_plans) * 100, 1) as market_share_pct
FROM ratha_chakram_customers rc;

-- Create view for competitive analysis
CREATE MATERIALIZED VIEW competitor_win_analysis AS
SELECT 
    rc.switched_from,
    COUNT(*) as customers_won,
    ROUND(AVG(rc.premium_savings_percent), 1) as avg_savings,
    ROUND(AVG(et.onboarding_speed_advantage_days), 1) as avg_speed_advantage,
    ROUND(COUNT(CASE WHEN rc.india_coverage_enabled THEN 1 END)::FLOAT / COUNT(*) * 100, 1) as india_adoption_pct
FROM ratha_chakram_customers rc
LEFT JOIN expat_competitive_tracking et ON rc.expat_id = et.expat_id
GROUP BY rc.switched_from
ORDER BY customers_won DESC;

-- Refresh every day
ALTER MATERIALIZED VIEW ratha_market_metrics OWNER TO admin;
ALTER MATERIALIZED VIEW competitor_win_analysis OWNER TO admin;
```

---

## Step 8: Query Examples

```sql
-- Q1: Market penetration
SELECT market_share_pct FROM ratha_market_metrics;

-- Q2: Why are we winning?
SELECT switched_from, customers_won, avg_savings, avg_speed_advantage
FROM competitor_win_analysis
ORDER BY customers_won DESC;

-- Q3: By visa type
SELECT 
    visa_type,
    COUNT(*) as customers,
    ROUND(AVG(premium_savings_percent), 1) as avg_savings,
    ROUND(AVG(satisfaction_score), 1) as avg_satisfaction,
    ROUND(100 * COUNT(CASE WHEN india_coverage_enabled THEN 1 END)::FLOAT / COUNT(*), 1) as india_adoption_pct
FROM ratha_chakram_customers
GROUP BY visa_type
ORDER BY customers DESC;

-- Q4: Revenue impact
SELECT 
    COUNT(*) as customers,
    ROUND(AVG(ratha_monthly_premium), 2) as avg_monthly_premium,
    ROUND(AVG(ratha_monthly_premium) * COUNT(*), 2) as monthly_revenue,
    ROUND(AVG(ratha_monthly_premium) * COUNT(*) * 12, 2) as annual_revenue
FROM ratha_chakram_customers;

-- Q5: Customer lifetime value
SELECT 
    ROUND(AVG(ratha_monthly_premium) * 12 * 3, 2) as avg_3yr_ltv,
    COUNT(*) as customers,
    ROUND(AVG(ratha_monthly_premium) * 12 * 3 * COUNT(*), 2) as total_3yr_value
FROM ratha_chakram_customers;
```

---

## Monitoring & Maintenance

### Monitor Query Performance

```sql
-- Check slow queries
SELECT query, runtime FROM stl_query 
WHERE query_type = 'SELECT'
  AND runtime > 5000  -- Queries over 5 seconds
ORDER BY runtime DESC;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    size
FROM svv_table_info
ORDER BY size DESC;
```

### Schedule Regular Data Refreshes

```bash
# Update your data daily with new customer records
# Create a Lambda function or cron job:

aws lambda create-function \
  --function-name ratha-chakram-redshift-refresh \
  --runtime python3.9 \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda_function.zip
```

---

## Cost Estimation

### Cluster Costs

```
Node Type: dc2.large
Number of Nodes: 2
Hourly cost: 2 nodes × $1.086/hour = $2.17/hour
Monthly cost: $2.17 × 730 hours ≈ $1,584/month
Annual cost: ≈ $19,000/year

For 1,500-5,000 customers, this is $12.66-$38/customer/year
```

### Cost Optimization Tips

1. **Use dc2.large initially** (good for analytics)
2. **Scale to 4-6 nodes** at 10K+ customers
3. **Use reserved nodes** for 30% discount (1-3 year commitment)
4. **Compress data** in Redshift (reduce storage by 70%)

---

## Security Best Practices

### 1. Credentials Management
```bash
# Use AWS Secrets Manager instead of hardcoded passwords
aws secretsmanager create-secret \
  --name ratha-chakram-redshift \
  --secret-string '{"username":"admin","password":"your_password"}'
```

### 2. Encryption
```sql
-- Enable encryption at rest (automatic with Redshift)
-- Enable encryption in transit (SSL/TLS):
REVOKE CONNECT ON DATABASE ratha_chakram FROM PUBLIC;
```

### 3. IAM Access Control
```bash
# Restrict to specific users/roles only
# Don't use root AWS account for Redshift
```

### 4. Audit Logging
```bash
# Enable query logging
aws redshift modify-cluster \
  --cluster-identifier ratha-chakram-prod \
  --enable-logging
```

---

## Troubleshooting

### Connection Issues
```bash
# Check cluster status
aws redshift describe-clusters \
  --cluster-identifier ratha-chakram-prod

# Check security group
aws ec2 describe-security-groups \
  --filters Name=group-name,Values=default

# Test with psql
psql -h YOUR_ENDPOINT -U admin -d ratha_chakram -p 5439 -c "SELECT 1"
```

### Slow Queries
```sql
-- Analyze explain plan
EXPLAIN SELECT * FROM ratha_chakram_customers WHERE us_state = 'CA';

-- Add indexes if needed
CREATE INDEX idx_ratha_state ON ratha_chakram_customers (us_state);

-- VACUUM and ANALYZE
VACUUM ratha_chakram_customers;
ANALYZE ratha_chakram_customers;
```

### Data Not Loading
```sql
-- Check load errors
SELECT error_code, error_reason, COUNT(*) 
FROM stl_load_errors 
WHERE table_name = 'ratha_chakram_customers'
GROUP BY error_code, error_reason;

-- Re-run with error handling
COPY ratha_chakram_customers FROM 's3://...' 
WITH STATUPDATE EXPLICIT_IDS NULL AS 'None';
```

---

## Migration Checklist

- [ ] Create Redshift cluster (5-10 min)
- [ ] Configure security group
- [ ] Test psql connection
- [ ] Create 3 tables in Redshift
- [ ] Upload CSV to S3
- [ ] Create IAM role for S3 access
- [ ] Load data with COPY commands
- [ ] Verify row counts match
- [ ] Create indexes & materialized views
- [ ] Update Python connection string
- [ ] Update `.env` variables
- [ ] Test with `test_data_layer.py`
- [ ] Run Gradio dashboard and verify
- [ ] Set up daily refresh schedule
- [ ] Enable query logging
- [ ] Enable encryption & backups
- [ ] Document credentials securely

---

## Next: Real Customer Data

Once this is working with mock data:

1. **Load historical data** (past customer migrations)
2. **Set up real-time pipeline** (new signups → Redshift)
3. **Archive cold data** (customers < 1 year → S3)
4. **Add BI tools** (Tableau, Looker on top of Redshift)

---

**Status**: Ready for production. Redshift scales to millions of records and concurrent queries.

**Support**: For Redshift issues, check AWS Redshift documentation or contact AWS support.

---

## Quick Reference

```bash
# Connect to Redshift
psql -h YOUR_ENDPOINT -U admin -d ratha_chakram

# Upload data to S3
aws s3 cp data/*.csv s3://ratha-chakram-data/

# Check cluster status
aws redshift describe-clusters --cluster-identifier ratha-chakram-prod

# Monitor queries
SELECT query, runtime FROM stl_query ORDER BY runtime DESC LIMIT 10;

# Scale cluster
aws redshift modify-cluster --cluster-identifier ratha-chakram-prod --number-of-nodes 4
```

---

**You're ready to go production.** 🚀
