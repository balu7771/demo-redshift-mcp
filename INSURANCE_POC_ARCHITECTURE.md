# Insurance Customer Migration Analysis - POC Architecture

## Problem Statement
Analyze customer migration patterns for an insurance company's new product launch:
- How many customers renewed (stayed with company)?
- How many left to competitors?
- How many came back from competitors and why?

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     EXECUTIVE (NL Question)                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    "Tell me how many..."
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    CREWAI ORCHESTRATION                          │
├──────────────────────────────────────────────────────────────────┤
│  1. Query Analyzer Agent                                         │
│     - Parse NL question                                          │
│     - Check template registry                                    │
│     - If match → use template logic                              │
│     - If no match → create dynamic query logic                   │
│                                                                  │
│  2. Data Retrieval Agent                                         │
│     - Call MCP tools to fetch data                               │
│     - Execute joins & cross-store logic                          │
│                                                                  │
│  3. Insights Agent                                               │
│     - Analyze results                                            │
│     - Format response with business context                      │
│     - Add "why came back" inference                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                      MCP SERVER LAYER                            │
├──────────────────────────────────────────────────────────────────┤
│  ▪ query_redshift_new_product()   - Query new product data       │
│  ▪ query_redshift_competitors()   - Query competitor mock data   │
│  ▪ read_legacy_excel()            - Read Excel file              │
│  ▪ cross_join_by_driver_license() - Join legacy + new via DL     │
│  ▪ analyze_migration_cohorts()    - Segment customers            │
│  ▪ infer_return_reason()          - Why came back logic          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼────────┐ ┌──────▼──────┐  ┌────────▼────────┐
│  EXCEL (Mock)  │ │  REDSHIFT   │  │   REDSHIFT      │
│                │ │  (New Prod) │  │  (Competitors)  │
│ Legacy Product │ │  100 custs  │  │   Mock data     │
│  900 customers │ │             │  │   (Big 4)       │
└────────────────┘ └─────────────┘  └─────────────────┘
```

---

## Data Models

### 1. Legacy Product Data (Excel - Mock)
**File**: `legacy_product_mock.xlsx`

| Column | Type | Description |
|--------|------|-------------|
| driver_license | VARCHAR(50) | PRIMARY KEY - unique identifier |
| state | VARCHAR(2) | Insured state |
| naic_code | VARCHAR(10) | NAIC company code |
| policy_number | VARCHAR(50) | Policy ID |
| coverage_type | VARCHAR(50) | e.g., "Auto", "Home" |
| vehicle_vin | VARCHAR(17) | Vehicle VIN (if auto) |
| vehicle_model | VARCHAR(100) | Vehicle model (if auto) |
| premium_6month | DECIMAL(10,2) | 6-month premium amount |
| last_renewal_date | DATE | Last renewal date |
| status | VARCHAR(20) | "ACTIVE", "EXPIRED", "CANCELLED" |

**Row Count**: 900 customers

---

### 2. New Product Data (Redshift - Mock)
**Table**: `new_product_customers`

| Column | Type | Description |
|--------|------|-------------|
| driver_license | VARCHAR(50) | PRIMARY KEY - matches legacy DL |
| state | VARCHAR(2) | Insured state |
| naic_code | VARCHAR(10) | New product NAIC |
| policy_number | VARCHAR(50) | New policy ID |
| coverage_type | VARCHAR(50) | Coverage in new product |
| vehicle_vin | VARCHAR(17) | (if auto) |
| vehicle_model | VARCHAR(100) | (if auto) |
| premium_6month | DECIMAL(10,2) | New premium (typically lower) |
| effective_date | DATE | Renewal date to new product |
| feature_adoption | VARCHAR(20) | "SIMPLE", "CONNECTED", "PREMIUM" |
| created_at | TIMESTAMP | Record created |

**Row Count**: 100 customers

---

### 3. Competitor Data (Redshift - Mock)
**Table**: `competitor_coverage_history`

| Column | Type | Description |
|--------|------|-------------|
| driver_license | VARCHAR(50) | Customer identifier |
| competitor_name | VARCHAR(50) | "Allstate", "Progressive", "Geico", "State Farm" |
| coverage_start | DATE | When customer started with competitor |
| coverage_end | DATE | When customer left competitor (NULL if still there) |
| was_customer_with_us_before | BOOLEAN | Did they come back to us? |
| reason_left_us | VARCHAR(100) | Mock: "Price", "Coverage Gap", "Service" |

**Row Count**: Mock entries for competitors

---

## Query Template Registry

Pre-defined templates for common questions:

### Template 1: "Customers Renewed"
**Pattern**: `"renewed into new product" OR "moved to new product" OR "upgraded"`

```python
{
    "template_name": "customers_renewed",
    "description": "Count customers who moved from legacy to new product",
    "query_logic": """
    SELECT COUNT(DISTINCT dl.driver_license) as renewed_count
    FROM legacy_customers dl
    INNER JOIN new_product_customers np ON dl.driver_license = np.driver_license
    WHERE dl.status IN ('ACTIVE', 'EXPIRED')
      AND np.effective_date >= dl.last_renewal_date
    """
}
```

### Template 2: "Customers Left"
**Pattern**: `"left" OR "moved out" OR "cancelled" OR "went to competitor"`

```python
{
    "template_name": "customers_left",
    "description": "Count customers who left and didn't renew in new product",
    "query_logic": """
    SELECT COUNT(DISTINCT dl.driver_license) as left_count
    FROM legacy_customers dl
    WHERE dl.driver_license NOT IN (SELECT driver_license FROM new_product_customers)
      AND dl.status IN ('ACTIVE', 'EXPIRED')
    """
}
```

### Template 3: "Customers Returned"
**Pattern**: `"came back" OR "returned" OR "win back" OR "re-acquired"`

```python
{
    "template_name": "customers_returned",
    "description": "Count customers who went to competitor then came back",
    "query_logic": """
    SELECT COUNT(DISTINCT cc.driver_license) as returned_count
    FROM competitor_coverage_history cc
    INNER JOIN new_product_customers np ON cc.driver_license = np.driver_license
    WHERE cc.was_customer_with_us_before = TRUE
      AND cc.coverage_end IS NOT NULL
      AND np.effective_date > cc.coverage_end
    """
}
```

---

## Implementation Roadmap

### Phase 1: Data Setup (Week 1)
- [ ] Create mock legacy product data (900 customers) → Excel
- [ ] Create mock new product data (100 customers) → Redshift table
- [ ] Create mock competitor data → Redshift table
- [ ] Set up Redshift connection in Python

### Phase 2: MCP Server (Week 1-2)
- [ ] Build MCP server with 6 tools (see above)
- [ ] Test individual data fetches
- [ ] Test cross-store joins

### Phase 3: CrewAI Integration (Week 2)
- [ ] Query Analyzer Agent
- [ ] Data Retrieval Agent
- [ ] Insights Agent
- [ ] Integrate with MCP

### Phase 4: Testing & Refinement (Week 2)
- [ ] Test all 3 key questions
- [ ] Test edge cases
- [ ] Verify "why came back" inference logic

### Phase 5: Natural Language Interface (Week 3)
- [ ] Build CLI for executive questions
- [ ] Add response formatting
- [ ] Document for business users

---

## Key Design Decisions

### 1. Why Keep Excel Separate?
- Simulates real scenario where legacy data may be in different systems
- Tests cross-store join logic early
- Simple to mock and iterate

### 2. Why MCP for Data Access?
- Clean abstraction between data layer and business logic
- Production-ready: MCP tools can be scaled/replaced
- Enables CrewAI agents to remain focused on reasoning, not data plumbing

### 3. Why Template + Dynamic Fallback?
- Fast path for common questions (templates)
- Flexible path for edge cases (CrewAI reasoning)
- Balances performance with adaptability

### 4. Why Infer "Why Came Back"?
- No explicit reason data in mock
- Pattern: compare new product features/pricing vs. legacy
  - New premium < old premium → "Price"
  - New has "CONNECTED" feature → "Innovation"
  - New has "SIMPLE" → "Simplicity"

---

## Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Data: Legacy | Python + openpyxl | Easy mock data creation |
| Data: New | AWS Redshift + psycopg2 | Production-grade OLAP |
| MCP | Claude MCP SDK | Clean, typed tool definitions |
| Orchestration | CrewAI 0.x | Multi-agent reasoning |
| Environment | Python 3.10+ | Modern async support |

---

## Success Criteria

✅ Executive can ask: "How many customers renewed?"
✅ Executive can ask: "How many left for competitors?"
✅ Executive can ask: "How many came back and why?"
✅ Response includes business context (e.g., "X% came back due to pricing")
✅ System handles 900 legacy + 100 new in <5 seconds

---

## Next Steps

1. **Approval**: Review this architecture. Any changes needed?
2. **Implementation**: Start with Phase 1 (data setup)
3. **Iteration**: Build incrementally, test each phase

---

## Questions for Clarification

Before implementation:
1. Do you want Redshift columns for mock competitor reasons (e.g., `reason_left_us`)?
2. Should "why came back" be based on hard rules (premium diff) or softer inference?
3. For Phase 5, do you want a CLI, HTTP endpoint, or both?

