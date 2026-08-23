# Ratha Chakram - Insurance for Indian Expats in USA
## Customer Migration & Market Penetration Analysis POC

## 🎯 Problem Statement

**Ratha Chakram** just launched insurance products specifically designed for Indian expats on business visas (H1B, L1, B1) in the USA. The company wants to understand:

1. **Market Penetration**: How many Indian expats are switching from competitors?
2. **Competitive Analysis**: Which competitors are we winning from? (Allianz, AIG, ICICI Lombard, HDFC ERGO)
3. **ROI Metrics**: Average premium savings? Onboarding speed? India coverage adoption?
4. **Win-back Strategy**: Why are expats choosing Ratha over established competitors?

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│        RATHA CHAKRAM EXECUTIVE DASHBOARD                         │
│     (Monitor Expat Acquisition & Competitive Position)           │
└─────────────────────────┬────────────────────────────────────────┘
                          │
         "How many expats switched to Ratha?"
         "What's our average premium vs Allianz?"
         "Onboarding speed vs AIG?"
                          │
┌─────────────────────────▼────────────────────────────────────────┐
│                   CREWAI ORCHESTRATION                            │
├──────────────────────────────────────────────────────────────────┤
│  1. Query Router Agent                                            │
│     - Understands expat-focused questions                         │
│     - Routes to market capture, competitive, or ROI analysis      │
│                                                                   │
│  2. Data Retrieval Agent                                          │
│     - Fetches from: competitor plans, Ratha customers, tracking   │
│     - Calculates: savings, speed, adoption rates                  │
│                                                                   │
│  3. Insights Agent                                                │
│     - Frames results for business (market share, ROI)             │
│     - Identifies competitive advantages                           │
│     - Highlights growth opportunities                             │
└─────────────────────────┬────────────────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────────────────┐
│                    MCP SERVER LAYER                               │
├──────────────────────────────────────────────────────────────────┤
│  8 Expat-Focused Tools:                                           │
│  ▪ get_expats_switched_to_ratha()        - Market capture       │
│  ▪ get_competitors_losing_to_ratha()     - Win from which?      │
│  ▪ get_premium_savings_analysis()        - Cost advantage       │
│  ▪ get_onboarding_speed_improvement()    - Speed advantage      │
│  ▪ get_india_coverage_adoption()         - Our differentiator   │
│  ▪ get_satisfaction_by_visa_type()       - H1B, L1, B1 NPS      │
│  ▪ get_competitive_positioning()         - vs Allianz, AIG      │
│  ▪ get_market_share_forecast()           - Growth projection    │
└─────────────────────────┬────────────────────────────────────────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
┌────────▼──────┐ ┌───────▼────────┐ ┌───┴─────────────┐
│  EXCEL        │ │  REDSHIFT      │ │   REDSHIFT      │
│ (Competitors) │ │  (Ratha Chak.) │ │  (Competitor    │
│               │ │  Customers     │ │   Tracking)     │
│ 5K expats on  │ │  1.5K expats   │ │  5K records     │
│ Allianz, AIG, │ │  switched to   │ │  (detailed why) │
│ ICICI, HDFC   │ │  Ratha Chakram │ │                 │
└───────────────┘ └────────────────┘ └─────────────────┘
```

---

## 📊 Data Models

### 1. Competitor Expat Plans (Excel - Mock)
**File**: `competitor_expat_plans.xlsx` — 5,000 expats currently on competitor plans

| Column | Type | Description |
|--------|------|-------------|
| expat_id | VARCHAR(50) | Unique identifier |
| origin_country | VARCHAR(50) | "India" |
| visa_type | VARCHAR(20) | H1B, L1, B1, E2, F1, etc. |
| us_state | VARCHAR(2) | CA, TX, NY, WA, etc. |
| current_provider | VARCHAR(50) | Allianz, AIG, ICICI Lombard, HDFC ERGO |
| monthly_premium | DECIMAL(10,2) | What they pay now (baseline) |
| coverage_types | VARCHAR(100) | Auto, Health, Renter, combinations |
| includes_india_coverage | BOOLEAN | Can use in India? |
| claims_processing_days | INT | Avg claim processing time |
| customer_since | DATE | When they started with provider |
| plan_status | VARCHAR(20) | ACTIVE, EXPIRED, CANCELLED |

---

### 2. Ratha Chakram Customers (Redshift - Mock)
**Table**: `ratha_chakram_customers` — 1,500 expats switched to Ratha (30% market capture)

| Column | Type | Description |
|--------|------|-------------|
| expat_id | VARCHAR(50) | Unique identifier |
| origin_country | VARCHAR(50) | "India" |
| visa_type | VARCHAR(20) | H1B, L1, B1, etc. |
| us_state | VARCHAR(2) | Current US state |
| switched_from | VARCHAR(50) | Previous provider (Allianz, AIG, etc.) |
| previous_monthly_premium | DECIMAL(10,2) | What they paid before |
| ratha_monthly_premium | DECIMAL(10,2) | Our price (typically 20-35% lower) |
| premium_savings_percent | DECIMAL(5,2) | Calculated: (prev - ratha) / prev * 100 |
| coverage_types | VARCHAR(100) | What they bought |
| india_coverage_enabled | BOOLEAN | Opted into India-USA coordination |
| onboarding_days | INT | Days from signup to active (typically 1-3) |
| competitor_onboarding_days | INT | What they experienced before (typically 7-14) |
| switched_date | DATE | When they became Ratha customers |
| satisfaction_score | INT | 1-10 NPS-like score |
| monthly_retention_rate | DECIMAL(3,1) | % staying active |

---

### 3. Competitor Exit Analysis (Redshift - Mock)
**Table**: `expat_competitive_tracking` — 5,000 records of why expats switched

| Column | Type | Description |
|--------|------|-------------|
| expat_id | VARCHAR(50) | Customer identifier |
| previous_company | VARCHAR(50) | Allianz, AIG, ICICI Lombard, HDFC ERGO |
| plan_end_date | DATE | When they left competitor |
| reason_left_previous | VARCHAR(100) | Why they left (high cost, slow claims, etc.) |
| reason_chose_ratha | VARCHAR(100) | Why Ratha won them (price, speed, India coverage) |
| had_ratha_before | BOOLEAN | Did they ever have Ratha? (win-back scenario) |
| premium_savings_percent | DECIMAL(5,2) | How much cheaper is Ratha? |
| onboarding_speed_advantage_days | INT | How much faster was Ratha? |
| india_coverage_interest | BOOLEAN | Did they care about India coordination? |
| acquisition_cost_estimated | DECIMAL(10,2) | Est. cost to acquire this customer |
| lifetime_value_projected | DECIMAL(10,2) | Projected 3-year value |

---

## 🎯 Query Templates

### Template 1: "Expats Switched to Ratha"
Answers: "How many Indian expats have switched to Ratha?"

```
Input: "How many expats switched to Ratha?"
Output: 
  1,500 Indian expats have switched to Ratha Chakram
  - From Allianz: 450 (30%)
  - From AIG: 380 (25%)
  - From ICICI Lombard: 340 (23%)
  - From HDFC ERGO: 200 (13%)
  - From others: 130 (9%)
  
  Average premium savings: 27%
  Average onboarding time: 1.5 days (vs 9 days competitors)
```

### Template 2: "Competitive Positioning"
Answers: "How are we doing vs each competitor?"

```
Input: "Compare Ratha to Allianz for expats"
Output:
  RATHA vs ALLIANZ (Indian Expats):
  - Ratha customers: 450
  - Avg Ratha premium: $89/month
  - Avg Allianz premium: $119/month
  - Savings: 25%
  
  - Ratha onboarding: 1.2 days
  - Allianz onboarding: 11 days
  - Speed advantage: 9.8 days faster
  
  - Ratha India coverage: 78% adoption
  - Allianz India coverage: 12% adoption
```

### Template 3: "ROI Metrics"
Answers: "What's the business impact?"

```
Input: "Show ROI of switching to Ratha"
Output:
  RATHA CHAKRAM ROI FOR EXPATS:
  
  Market Capture:
  - Total expats on competitor plans: 5,000
  - Switched to Ratha: 1,500 (30%)
  - Potential remaining: 3,500 (70%)
  
  Premium Economics:
  - Average monthly premium (Ratha): $89
  - Average lifetime value (3 years): $3,204
  - Total revenue from switched: $4.8M/year
  
  Satisfaction:
  - Avg satisfaction score: 8.2/10
  - Retention rate (monthly): 98.5%
  - India coverage adoption: 78%
```

### Template 4: "Visa Type Breakdown"
Answers: "How are we doing with H1B vs L1 vs B1?"

```
Input: "Show adoption by visa type"
Output:
  RATHA ADOPTION BY VISA TYPE:
  
  H1B: 920 customers (61%)
  - Avg satisfaction: 8.4/10
  - Avg premium: $85/month
  - India coverage: 82%
  
  L1: 380 customers (25%)
  - Avg satisfaction: 8.1/10
  - Avg premium: $92/month
  - India coverage: 75%
  
  B1: 180 customers (12%)
  - Avg satisfaction: 7.9/10
  - Avg premium: $98/month
  - India coverage: 68%
```

---

## 📈 Key Business Metrics

### Market Penetration
- **Total target market**: 5,000 expats on competitors
- **Ratha customers**: 1,500 (30% market share)
- **Addressable remaining**: 3,500 (70% growth potential)

### Financial Impact
- **Avg monthly premium**: $89/month × 1,500 = $133.5K/month
- **Annual revenue**: $1.6M from switched customers
- **3-year customer lifetime value**: $4.8M total

### Competitive Advantages
1. **Price**: 27% cheaper on average ($30/month savings)
2. **Speed**: 7.8 days faster onboarding (1.5 vs 9 days)
3. **Coverage**: 78% adoption of India-USA coordination (competitors: <20%)
4. **Satisfaction**: 8.2/10 NPS score

### Growth Potential
- Current win rate: 30% of competitor customers
- Target win rate: 50% (3,500 more customers)
- Potential additional revenue: $2.6M annually

---

## 🔧 Implementation Roadmap

### Phase 1: Expat Data Setup (Week 1)
- [ ] Generate mock competitor plans (5K expats) → Excel
- [ ] Generate Ratha customers (1.5K customers) → Redshift
- [ ] Generate competitor tracking (5K records) → Redshift
- [ ] Validate visa type distributions
- [ ] Validate premium savings percentages
- [ ] Validate onboarding speed improvements

### Phase 2: Expat-Specific MCP (Week 1-2)
- [ ] 8 MCP tools for expat analysis
- [ ] Premium savings calculator
- [ ] Onboarding speed analyzer
- [ ] India coverage adoption tracker
- [ ] Competitive position calculator
- [ ] ROI metrics engine

### Phase 3: CrewAI for Expat Insights (Week 2)
- [ ] Query Router: understands expat questions
- [ ] Data Agent: fetches competitive & adoption data
- [ ] Insights Agent: frames for business impact
- [ ] Test with business questions

### Phase 4: Executive Dashboard (Week 3)
- [ ] Gradio UI for expat metrics
- [ ] ROI visualizations
- [ ] Competitor comparison
- [ ] Retention & satisfaction tracking

---

## 🎓 What This POC Demonstrates

✅ **Market Capture Analysis**: How many expats switched from competitors
✅ **Competitive Positioning**: Where we're winning (price, speed, coverage)
✅ **ROI Quantification**: Premium savings, faster onboarding, adoption rates
✅ **Growth Potential**: 70% of market still on competitors
✅ **Customer Satisfaction**: Retention & NPS tracking by segment
✅ **Product Differentiation**: India-USA coverage as unique value prop

---

## 💡 Next Steps

1. **Confirm data model**: Does the expat persona align with reality?
2. **Validate metrics**: Are premium savings, onboarding times realistic?
3. **Build & test**: Implement Phase 1 & 2
4. **Executive preview**: Show market penetration & ROI
5. **Go live**: Use for actual market strategy decisions

---

**Status**: Ready to implement
**Target Audience**: Ratha Chakram leadership (CEO, CMO, CFO)
**Use Case**: Justify growth investment, guide competitive strategy, track acquisition ROI
