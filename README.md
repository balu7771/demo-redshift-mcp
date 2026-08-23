# Insurance Customer Migration Analysis POC

A production-grade proof-of-concept demonstrating customer migration analysis using:
- **Data Layer**: Mock legacy (Excel) + new product (CSV) + competitor data
- **MCP Server**: Data access tools exposed to CrewAI agents
- **CrewAI**: Query router + analysis agents for multi-step reasoning
- **Gradio UI**: Executive-friendly natural language interface

## Architecture

```
Executive Question
    ↓
Gradio UI
    ↓
CrewAI Router Agent (query understanding)
    ↓
CrewAI Analysis Agent (data fetching + insights)
    ↓
MCP Tools (GetRenewedCount, GetLeftCount, etc.)
    ↓
Data Layer (pandas + Excel/CSV queries)
    ↓
Response formatted for executives
```

## Setup

### 1. Install Dependencies

```bash
# Install using uv (recommended)
uv sync

# OR using pip
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 3. Generate Mock Data

```bash
python -m demo_redshift_mcp.data_generator
```

This creates:
- `data/legacy_product.xlsx` - 900 legacy customers
- `data/new_product_customers.csv` - 100 new product customers
- `data/competitor_coverage.csv` - Competitor history

## Running the Application

### Web UI (Recommended)

```bash
# Launch Gradio interface
python -m demo_redshift_mcp

# Opens at http://localhost:7860
```

### Command Line (Testing)

```bash
python -c "
from src.demo_redshift_mcp.crew_agents import run_customer_migration_analysis
result = run_customer_migration_analysis('How many customers renewed?')
print(result)
"
```

## Sample Questions for Executives

1. **"How many customers renewed into the new product?"**
   - Returns: Count + percentage of migration success

2. **"How many customers left and went to competitors?"**
   - Returns: Count + breakdown by status (ACTIVE/EXPIRED/CANCELLED)

3. **"How many came back from competitors and why?"**
   - Returns: Return count + reasons (price, features, etc.)

4. **"What's the overall migration summary?"**
   - Returns: Comprehensive analysis of all segments

5. **"Tell me about customers in California"**
   - Returns: State-specific metrics

6. **"Who adopted the CONNECTED feature?"**
   - Returns: Feature adoption breakdown

## Project Structure

```
demo-redshift-mcp/
├── src/demo_redshift_mcp/
│   ├── app.py                 # Gradio UI entry point
│   ├── crew_agents.py         # CrewAI agents + workflow
│   ├── mcp_server.py          # MCP tools definition
│   ├── data_layer.py          # Data access logic
│   ├── data_generator.py      # Mock data generation
│   └── __init__.py
├── data/                      # Generated mock data
│   ├── legacy_product.xlsx
│   ├── new_product_customers.csv
│   └── competitor_coverage.csv
├── INSURANCE_POC_ARCHITECTURE.md
├── pyproject.toml
└── .env
```

## Key Design Decisions

### Data Separation (Excel vs CSV)
- Legacy: Excel (simulates existing systems)
- New: CSV in "Redshift" (simulates cloud OLAP)
- Reason: Tests cross-store join logic early

### MCP Over Direct Queries
- Clean abstraction between data and reasoning
- Production-ready: swap CSV with Redshift later
- Agents stay focused on reasoning, not plumbing

### Template + Dynamic Fallback
- Fast path: pre-defined queries for common questions
- Flexible path: CrewAI creates logic for edge cases
- Soft inference: combine pricing + feature signals to explain why customers returned

## Next Steps

### Phase 1: Data ✅
- Mock data generation (900 legacy, 100 new, competitor coverage)

### Phase 2: MCP ✅
- Data access tools (GetRenewedCount, GetLeftCount, etc.)

### Phase 3: CrewAI ✅
- Query router + analysis agents

### Phase 4: Testing
- Run sample questions and verify accuracy
- Test edge cases

### Phase 5: UI ✅
- Gradio interface for executives

### Future Enhancements
- [ ] Replace CSV with actual AWS Redshift
- [ ] Add state-level dashboards
- [ ] Export reports as PDF/Excel
- [ ] Add historical trend analysis
- [ ] Deploy as FastAPI endpoint

## Troubleshooting

### "Module not found" error
```bash
# Ensure you're in the right directory
cd /Users/Balu/Documents/Projects/MyCode/demo-redshift-mcp

# Reinstall dependencies
uv sync
```

### "Data not found" error
```bash
# Generate mock data
python -m demo_redshift_mcp.data_generator
```

### CrewAI errors
- Ensure ANTHROPIC_API_KEY is set in .env
- Check that you have Claude 3.5 Sonnet (or later) access

## Development

### Adding a New Query Tool

1. Add method to `DataLayer` (data_layer.py)
2. Wrap it in `InsuranceMCPTools` (mcp_server.py)
3. Create CrewAI @tool wrapper (crew_agents.py)
4. Update routing logic in analysis_task

### Testing Locally

```bash
from src.demo_redshift_mcp.data_layer import DataLayer

data = DataLayer()
result = data.customers_renewed()
print(result)
```

## License

Internal POC - Not for production use without proper data governance.
