# Quick Start Guide

## 30-Second Setup

### Test the Data Analysis (No API Key Required)
```bash
cd /Users/Balu/Documents/Projects/MyCode/demo-redshift-mcp
python test_data_layer.py
```

**Output**: Shows analysis of 900 legacy customers, 211 renewals, 121 returned, with breakdown by return reasons.

---

## Full Application Setup (with Gradio UI)

### Prerequisites
- **API Key**: Get from https://console.anthropic.com
- **Python**: 3.13 or lower (CrewAI compatibility issue with 3.14)

### Step 1: Set Environment
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY=sk-ant-...
```

### Step 2: Install Dependencies
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### Step 3: Generate Mock Data
```bash
python -m demo_redshift_mcp.data_generator
# Creates: data/legacy_product.xlsx, new_product_customers.csv, competitor_coverage.csv
```

### Step 4: Launch UI
```bash
python -m demo_redshift_mpc
# Opens at http://localhost:7860
```

### Step 5: Ask Questions
Try these in the Gradio interface:
- "How many customers renewed?"
- "How many customers left for competitors?"
- "How many came back and why?"
- "Tell me the migration summary"
- "Show me customers in California"
- "Who adopted the CONNECTED feature?"

---

## System Output Example

**Input**: "How many customers came back from competitors and why?"

**Output**:
```
Returned Customers Analysis:
- Total returned: 121 (13.44% of legacy customers)
- From Geico: 41 customers
- From Progressive: 36 customers  
- From Allstate: 23 customers
- From State Farm: 21 customers

Why They Came Back:
- Price-Sensitive: 15 customers (lower premiums)
- Innovation: 15 customers (new connected features)
- Simplicity: 16 customers (simplified products)
- Value + Features: 75 customers (combination of benefits)

Key Insight: 62% came back primarily for value + features 
combination, while 25% were price-sensitive.
```

---

## Architecture at a Glance

```
Your Question 
    ↓
Gradio UI
    ↓
CrewAI Agent (understands intent)
    ↓
MCP Tools (calls data layer)
    ↓
Data Layer (Excel + CSV queries + joins)
    ↓
Executive Insights + Numbers
```

---

## Key Files

| File | Purpose |
|------|---------|
| `src/demo_redshift_mcp/app.py` | Gradio interface |
| `src/demo_redshift_mcp/crew_agents.py` | CrewAI agents |
| `src/demo_redshift_mcp/mcp_server.py` | 8 analysis tools |
| `src/demo_redshift_mcp/data_layer.py` | Query logic |
| `src/demo_redshift_mcp/data_generator.py` | Mock data generator |
| `data/` | Generated datasets |

---

## Troubleshooting

### "Python 3.14 - chromadb error"
CrewAI doesn't support Python 3.14 yet. Use Python 3.13:
```bash
# Using pyenv
pyenv install 3.13.0
pyenv local 3.13.0
uv sync
python -m demo_redshift_mcp
```

### "Data not found" 
Generate mock data:
```bash
python -c "from src.demo_redshift_mcp.data_generator import generate_all_data; generate_all_data()"
```

### "ANTHROPIC_API_KEY not set"
Edit `.env`:
```bash
cp .env.example .env
# Add your key: ANTHROPIC_API_KEY=sk-ant-...
```

### "Module not found"
Reinstall:
```bash
uv sync
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

---

## Extending the System

### Add a New Question Type

**Example**: "How many customers are in ACTIVE status?"

**Step 1**: Add to data layer (`data_layer.py`):
```python
def customers_in_active_status(self) -> Dict:
    active = self.legacy_df[self.legacy_df["status"] == "ACTIVE"]
    return {
        "count": len(active),
        "percentage": round((len(active) / len(self.legacy_df)) * 100, 2),
    }
```

**Step 2**: Expose in MCP (`mcp_server.py`):
```python
def get_active_customers(self) -> str:
    result = self.data.customers_in_active_status()
    return f"Active Customers: {result['count']} ({result['percentage']}%)"
```

**Step 3**: Add CrewAI tool (`crew_agents.py`):
```python
@tool("GetActiveCount")
def get_active_count():
    """Get count of customers still in active status"""
    return mcp.get_active_customers()

# Add to query_router.tools = [..., get_active_count]
```

**Done!** Now ask: "How many customers are still active?"

---

## Real-World Deployment

When moving to production:

### 1. Replace Mock Data with Redshift
```python
# data_layer.py
def query_new_product_customers(self):
    query = "SELECT * FROM redshift_schema.new_product_customers"
    return pd.read_sql(query, self.redshift_connection)
```

### 2. Add Real Competitor Data
```python
# Use LexisNexis / Verisk API instead of mock
# Same interface, different backend
```

### 3. Scale to Millions
- Add caching for queries
- Use Redshift for joins (not pandas)
- Add pagination for large result sets

---

## Testing

### Data Layer Tests (No API Key)
```bash
python test_data_layer.py
```

### Full Integration Tests (Requires API Key)
```bash
python test_poc.py
```

---

## Next Steps

1. **Get Started**: Run `python test_data_layer.py` (2 minutes)
2. **Try UI**: Set API key, run `python -m demo_redshift_mcp`
3. **Customize**: Extend with your own questions
4. **Deploy**: Switch to Redshift + real data

---

**Questions?** Check `IMPLEMENTATION_COMPLETE.md` or `INSURANCE_POC_ARCHITECTURE.md` for details.
