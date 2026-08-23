"""Generate mock insurance data for POC."""

import random
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path

# ============================================================================
# Configuration - RATHA CHAKRAM: Insurance for Indian Expats in USA
# ============================================================================

# Competitor Expat Plans: 5,000 expats on competitor insurance
COMPETITOR_CUSTOMER_COUNT = 5000
# Ratha Chakram Customers: 1,500 switched to Ratha (30% market capture)
RATHA_CUSTOMER_COUNT = 1500

US_STATES = ["CA", "TX", "NY", "WA", "IL", "PA", "MA", "CO", "GA", "NC", "MI", "FL"]
VISA_TYPES = ["H1B", "L1", "B1", "E2", "F1"]
COVERAGE_TYPES = ["Auto", "Health", "Renter", "Auto+Health"]
VEHICLE_MODELS = ["Toyota Camry", "Honda Civic", "Ford F-150", "Chevy Silverado",
                   "BMW 3 Series", "Tesla Model 3", "Mazda CX-5", "Jeep Wrangler"]

# Competitors targeting expat market
COMPETITOR_NAMES = ["Allianz", "AIG", "ICICI Lombard", "HDFC ERGO", "CHUBB", "IMG Global"]

# Why expats choose (or leave) insurance
REASONS_LEFT_COMPETITOR = [
    "High premium",
    "Slow claims processing",
    "Complex onboarding",
    "No India coverage",
    "Poor customer service",
    "Limited coverage options"
]

REASONS_CHOSE_RATHA = [
    "Better affordability",
    "Faster onboarding",
    "India-USA coordination",
    "Simpler process",
    "Better customer support",
    "Comprehensive expat coverage"
]

FEATURES = ["BASIC", "STANDARD", "PREMIUM"]

# ============================================================================
# Helper Functions
# ============================================================================

def generate_expat_id():
    """Generate expat identifier."""
    return f"EXP{random.randint(100000, 999999)}"

def generate_policy_number():
    """Generate policy number for Ratha."""
    return f"RATHA{random.randint(100000, 999999)}"

def generate_competitor_expat() -> dict:
    """Generate expat on competitor insurance plan."""
    monthly_premium = round(random.uniform(75, 150), 2)  # Expat insurance tier

    return {
        "expat_id": generate_expat_id(),
        "origin_country": "India",
        "visa_type": random.choice(VISA_TYPES),
        "us_state": random.choice(US_STATES),
        "current_provider": random.choice(COMPETITOR_NAMES),
        "monthly_premium": monthly_premium,
        "coverage_types": random.choice(COVERAGE_TYPES),
        "includes_india_coverage": random.choice([True, False]),
        "claims_processing_days": random.randint(7, 21),
        "customer_since": datetime.now() - timedelta(days=random.randint(90, 1095)),
        "plan_status": random.choice(["ACTIVE", "EXPIRED", "CANCELLED"]),
    }

def generate_ratha_customer(competitor_expat: dict) -> dict:
    """Generate Ratha Chakram customer (converted from competitor)."""
    # Ratha is typically 20-35% cheaper
    previous_monthly = competitor_expat["monthly_premium"]
    discount_rate = random.uniform(0.20, 0.35)
    ratha_monthly = round(previous_monthly * (1 - discount_rate), 2)

    # Ratha is fast: 1-3 days typically vs 7-14 for competitors
    ratha_onboarding = random.randint(1, 3)
    competitor_onboarding = random.randint(7, 14)

    return {
        "expat_id": competitor_expat["expat_id"],
        "origin_country": "India",
        "visa_type": competitor_expat["visa_type"],
        "us_state": competitor_expat["us_state"],
        "switched_from": competitor_expat["current_provider"],
        "previous_monthly_premium": previous_monthly,
        "ratha_monthly_premium": ratha_monthly,
        "premium_savings_percent": round(discount_rate * 100, 1),
        "coverage_types": competitor_expat["coverage_types"],
        "india_coverage_enabled": random.choice([True, True, True, False]),  # 75% adoption
        "onboarding_days": ratha_onboarding,
        "competitor_onboarding_days": competitor_onboarding,
        "switched_date": datetime.now() - timedelta(days=random.randint(0, 90)),
        "satisfaction_score": random.randint(7, 10),  # Happy customers
        "monthly_retention_rate": round(random.uniform(97, 99.5), 1),
    }

def generate_competitor_exit_tracking(expat_id: str, previous_provider: str) -> dict:
    """Generate tracking of why expat switched (competitive analysis)."""
    return {
        "expat_id": expat_id,
        "previous_company": previous_provider,
        "plan_end_date": datetime.now() - timedelta(days=random.randint(0, 60)),
        "reason_left_previous": random.choice(REASONS_LEFT_COMPETITOR),
        "reason_chose_ratha": random.choice(REASONS_CHOSE_RATHA),
        "had_ratha_before": False,
        "premium_savings_percent": round(random.uniform(15, 35), 1),
        "onboarding_speed_advantage_days": random.randint(4, 10),
        "india_coverage_interest": random.choice([True, True, False]),
        "acquisition_cost_estimated": round(random.uniform(50, 200), 2),
        "lifetime_value_projected": round(random.uniform(1500, 5000), 2),
    }

# ============================================================================
# Main Data Generation
# ============================================================================

def generate_all_data(output_dir: str = "./data") -> tuple:
    """Generate Ratha Chakram expat migration data."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    print("Generating Ratha Chakram expat insurance data...")

    # 1. Generate competitor customers: 5,000 expats on competitor plans
    print(f"  • Generating {COMPETITOR_CUSTOMER_COUNT} expats on competitor plans...")
    competitor_customers = [generate_competitor_expat() for _ in range(COMPETITOR_CUSTOMER_COUNT)]
    competitor_df = pd.DataFrame(competitor_customers)

    # 2. Generate Ratha Chakram customers: 1,500 switched (30% market capture)
    print(f"  • Generating {RATHA_CUSTOMER_COUNT} Ratha Chakram customers...")
    selected_expats = competitor_df.sample(n=RATHA_CUSTOMER_COUNT)

    ratha_customers = [
        generate_ratha_customer(row.to_dict())
        for _, row in selected_expats.iterrows()
    ]
    ratha_df = pd.DataFrame(ratha_customers)

    # 3. Generate competitive exit tracking (why they switched)
    print("  • Generating competitive tracking data...")
    exit_tracking = [
        generate_competitor_exit_tracking(row["expat_id"], row["switched_from"])
        for _, row in ratha_df.iterrows()
    ]
    tracking_df = pd.DataFrame(exit_tracking)

    # 4. Save to Excel and CSV
    competitor_path = output_path / "competitor_expat_plans.xlsx"
    competitor_df.to_excel(competitor_path, index=False, engine="openpyxl")
    print(f"  ✓ Saved competitor plans: {competitor_path}")

    ratha_path = output_path / "ratha_chakram_customers.csv"
    ratha_df.to_csv(ratha_path, index=False)
    print(f"  ✓ Saved Ratha customers: {ratha_path}")

    tracking_path = output_path / "expat_competitive_tracking.csv"
    tracking_df.to_csv(tracking_path, index=False)
    print(f"  ✓ Saved competitive tracking: {tracking_path}")

    print("\n✅ Ratha Chakram Data Generation Complete!")
    print(f"  • Expats on competitor plans: {len(competitor_df)}")
    print(f"  • Switched to Ratha Chakram: {len(ratha_df)} ({round(len(ratha_df)/len(competitor_df)*100, 1)}% market capture)")
    print(f"  • Competitive tracking records: {len(tracking_df)}")

    # Show sample breakdown
    print(f"\n  Market breakdown by competitor:")
    for provider, count in ratha_df["switched_from"].value_counts().items():
        pct = round(count / len(ratha_df) * 100, 1)
        print(f"    • From {provider}: {count} ({pct}%)")

    print(f"\n  Visa type breakdown:")
    for visa, count in ratha_df["visa_type"].value_counts().items():
        pct = round(count / len(ratha_df) * 100, 1)
        print(f"    • {visa}: {count} ({pct}%)")

    print(f"\n  Key metrics:")
    print(f"    • Avg premium savings: {ratha_df['premium_savings_percent'].mean():.1f}%")
    print(f"    • Avg Ratha onboarding: {ratha_df['onboarding_days'].mean():.1f} days")
    print(f"    • Avg competitor onboarding: {ratha_df['competitor_onboarding_days'].mean():.1f} days")
    print(f"    • India coverage adoption: {ratha_df['india_coverage_enabled'].sum()} ({round(ratha_df['india_coverage_enabled'].mean()*100, 1)}%)")
    print(f"    • Avg satisfaction: {ratha_df['satisfaction_score'].mean():.1f}/10")

    return competitor_df, ratha_df, tracking_df

if __name__ == "__main__":
    generate_all_data()
