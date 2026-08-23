# 📂 Project Files Guide

## Directory Structure

```
demo-redshift-mcp/
│
├── 📖 DOCUMENTATION (Start Here)
│   ├── QUICK_START.md                  ← 5-min setup guide
│   ├── README.md                       ← Full user guide
│   ├── INSURANCE_POC_ARCHITECTURE.md   ← Design decisions
│   ├── IMPLEMENTATION_COMPLETE.md      ← Technical deep dive
│   ├── DELIVERY_SUMMARY.md             ← What was built
│   └── FILES_GUIDE.md                  ← This file
│
├── 🚀 EXECUTABLE
│   ├── test_data_layer.py              ← Run data tests (no API key)
│   ├── test_poc.py                     ← Run full tests (needs API)
│   └── src/demo_redshift_mcp/
│       └── app.py                      ← Gradio UI (python -m demo_redshift_mcp)
│
├── 💾 SOURCE CODE
│   └── src/demo_redshift_mcp/
│       ├── __init__.py                 ← Main entry point
│       ├── app.py                      ← Gradio UI interface
│       ├── crew_agents.py              ← CrewAI orchestration
│       ├── mcp_server.py               ← 8 MCP tools
│       ├── data_layer.py               ← Query logic & analysis
│       └── data_generator.py           ← Mock data creation
│
├── 📊 DATA (Auto-Generated)
│   ├── legacy_product.xlsx             ← 900 customers
│   ├── new_product_customers.csv       ← 211 customers (100 renewed + 121 returned)
│   └── competitor_coverage.csv         ← 810 competitor records
│
├── ⚙️ CONFIGURATION
│   ├── pyproject.toml                  ← Dependencies & metadata
│   ├── .env.example                    ← API key template
│   └── .gitignore                      ← Git settings
│
└── 📚 REFERENCE
    └── .git/                           ← Version control
```

---

## Quick Navigation by Task

### "I want to understand the architecture"
→ Read: `INSURANCE_POC_ARCHITECTURE.md` (10 min)

### "I want to get running in 5 minutes"
→ Follow: `QUICK_START.md`
```bash
python test_data_layer.py
```

### "I want to try the Gradio UI"
→ Follow: `QUICK_START.md`, "Full Application Setup"
```bash
python -m demo_redshift_mpc
# Opens http://localhost:7860
```

### "I want to see what was built"
→ Read: `DELIVERY_SUMMARY.md`

### "I want to understand the code"
→ Read: `IMPLEMENTATION_COMPLETE.md`
→ Then explore: `src/demo_redshift_mcp/`

### "I want to extend the system"
→ See: `IMPLEMENTATION_COMPLETE.md` → "Customization Points"
→ Or: `QUICK_START.md` → "Extending the System"

---

## File Purposes

### Documentation Files

| File | Purpose | Read Time |
|------|---------|-----------|
| `QUICK_START.md` | Fast setup, troubleshooting, extensions | 5 min |
| `README.md` | Full user guide, examples, features | 10 min |
| `INSURANCE_POC_ARCHITECTURE.md` | Design rationale, decision docs | 15 min |
| `IMPLEMENTATION_COMPLETE.md` | Technical details, customization | 20 min |
| `DELIVERY_SUMMARY.md` | What was built, next steps | 10 min |
| `FILES_GUIDE.md` | This file | 2 min |

### Test Files

| File | Purpose | Requires |
|------|---------|----------|
| `test_data_layer.py` | Data generation, queries, MCP tools | None |
| `test_poc.py` | Full integration test | API key |

### Source Code Files

| File | Purpose | Lines | Key Classes |
|------|---------|-------|-------------|
| `app.py` | Gradio UI interface | ~80 | create_interface() |
| `crew_agents.py` | CrewAI agents & tools | ~200 | query_router, analysis_supervisor |
| `mcp_server.py` | MCP tool definitions | ~60 | InsuranceMCPTools |
| `data_layer.py` | Query logic & analysis | ~200 | DataLayer |
| `data_generator.py` | Mock data generation | ~150 | generate_all_data() |
| `__init__.py` | Module entry point | ~5 | main() |

### Data Files

| File | Type | Rows | Created By |
|------|------|------|-----------|
| `legacy_product.xlsx` | Excel | 900 | data_generator.py |
| `new_product_customers.csv` | CSV | 211 | data_generator.py |
| `competitor_coverage.csv` | CSV | 810 | data_generator.py |

---

## Execution Flows

### Flow 1: Test Data Layer
```
You: python test_data_layer.py
     ↓
test_data_layer.py
     ├─ imports data_generator.py
     ├─ imports data_layer.py
     ├─ imports mcp_server.py
     ↓
Output: Analysis results (no CrewAI)
```

### Flow 2: Run Gradio UI
```
You: python -m demo_redshift_mpc
     ↓
__init__.py → main()
     ↓
app.py → create_interface()
     ↓
Gradio launches at http://localhost:7860
     ↓
Executive: "How many customers renewed?"
     ↓
crew_agents.py → run_customer_migration_analysis()
     ├─ query_router agent calls GetRenewedCount tool
     └─ analysis_supervisor formats response
     ↓
mcp_server.py → get_renewed_customers_count()
     ↓
data_layer.py → customers_renewed()
     ├─ Load legacy_df
     ├─ Load new_product_df
     └─ Join on driver_license
     ↓
Response: "211 customers (23.44%)"
```

### Flow 3: Extend with New Question

You want executives to ask: "How many customers by state?"

```
1. Edit data_layer.py → add customers_by_state()
2. Edit mcp_server.py → add get_customers_by_state()
3. Edit crew_agents.py → add @tool("CustomersByState")
4. Add to query_router.tools list
5. Done! Now works: "Tell me customers in California"
```

---

## Code Organization

### data_layer.py - The Brain
```
DataLayer class
├── query_legacy_customers()          # Filter legacy data
├── query_new_product_customers()     # Filter new product
├── query_competitor_coverage()       # Filter competitors
│
├── customers_renewed()               # 211 out of 900
├── customers_left()                  # 689 out of 900
├── customers_returned()              # 121 out of 900
├── infer_return_reasons()            # Why they came back
└── cross_join_analysis()             # Full summary
```

### mcp_server.py - The Tools
```
InsuranceMCPTools class
├── get_renewed_customers_count()
├── get_customers_left_count()
├── get_returned_customers_count()
├── get_return_reasons()
├── get_comprehensive_analysis()
├── query_by_state()
├── query_by_feature()
└── competitor_analysis()
```

### crew_agents.py - The Orchestration
```
Tools (wrapped with @tool decorator)
├── get_renewed_count()
├── get_left_count()
├── get_returned_count()
├── get_return_reasons()
├── get_comprehensive_analysis()
└── ... (8 total)

Agents
├── query_router → understands intent, picks tools
└── analysis_supervisor → formats results

run_customer_migration_analysis() → Main entry point
```

### app.py - The Interface
```
create_interface() → Gradio Blocks
├── Title & description
├── Input: Textbox for question
├── Output: Textbox for response
├── Button: Submit
└── Examples: Pre-built questions
```

---

## Key Statistics

### Code Metrics
- **Total lines of code**: ~1000
- **Python files**: 6 (app, crew_agents, mcp_server, data_layer, data_generator, __init__)
- **Test files**: 2 (test_data_layer, test_poc)
- **Documentation**: 6 markdown files

### Data Metrics
- **Mock customers created**: 900 (legacy) + 211 (new) = 1,111
- **Competitor records**: 810
- **Returned customers**: 121 (13.44%)
- **Renewal rate**: 23.44%

### Features
- **MCP tools**: 8
- **CrewAI agents**: 2
- **Sample questions**: 6
- **Analysis dimensions**: Renewed, Left, Returned, Return Reasons, By State, By Feature, By Competitor

---

## Starting Points by Role

### Executive / Business User
→ `QUICK_START.md` → `DELIVERY_SUMMARY.md`
→ Run: `python -m demo_redshift_mpc`

### Data Scientist / Analyst
→ `IMPLEMENTATION_COMPLETE.md`
→ Run: `python test_data_layer.py`
→ Explore: `src/demo_redshift_mcp/data_layer.py`

### Software Engineer
→ `INSURANCE_POC_ARCHITECTURE.md`
→ Read: All source code in `src/`
→ Run: `python test_poc.py`

### Project Manager
→ `DELIVERY_SUMMARY.md`
→ Check: Metrics section
→ Read: Next Steps section

---

## Common Commands

```bash
# List all files in project
find . -type f ! -path "./.git/*" ! -path "*venv*" | head -20

# Run data layer tests
python test_data_layer.py

# Generate fresh mock data
python -c "from src.demo_redshift_mcp.data_generator import generate_all_data; generate_all_data()"

# Launch Gradio UI
python -m demo_redshift_mpc

# Check dependencies installed
uv sync

# View generated data
head -5 data/legacy_product.xlsx
cat data/new_product_customers.csv | head -5
```

---

## File Dependencies

```
app.py
  ├─ crew_agents.py
  │   ├─ mcp_server.py
  │   │   └─ data_layer.py
  │   │       └─ data_generator.py
  │   └─ data_generator.py
  └─ data_generator.py
```

---

## Next Steps

1. **Start Here**: `QUICK_START.md` (5 min)
2. **Try Tests**: `python test_data_layer.py` (2 min)
3. **Understand**: `DELIVERY_SUMMARY.md` (10 min)
4. **Go Deep**: `IMPLEMENTATION_COMPLETE.md` (20 min)
5. **Extend**: Add your own analysis questions (30 min)

---

**Status**: ✅ All files created and tested
**Last Updated**: 2026-08-23
**Ready for**: Executive demo, developer extension, production deployment
