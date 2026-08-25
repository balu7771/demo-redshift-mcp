"""Data access layer for Ratha Chakram expat insurance data."""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# ============================================================================
# Data Loader
# ============================================================================

class DataLayer:
    """Unified data access layer for competitor pool, Ratha customers, and switch tracking."""

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.competitor_pool_df = None
        self.ratha_df = None
        self.tracking_df = None
        self._load_all_data()

    def _load_all_data(self):
        """Load all datasets from disk."""
        competitor_pool_path = self.data_dir / "competitor_expat_plans.xlsx"
        ratha_path = self.data_dir / "ratha_chakram_customers.csv"
        tracking_path = self.data_dir / "expat_competitive_tracking.csv"

        if competitor_pool_path.exists():
            self.competitor_pool_df = pd.read_excel(competitor_pool_path)
            print(f"Loaded competitor pool data: {len(self.competitor_pool_df)} expats")
        else:
            raise FileNotFoundError(f"Competitor pool data not found at {competitor_pool_path}")

        if ratha_path.exists():
            self.ratha_df = pd.read_csv(ratha_path)
            print(f"Loaded Ratha Chakram customer data: {len(self.ratha_df)} customers")
        else:
            raise FileNotFoundError(f"Ratha Chakram customer data not found at {ratha_path}")

        if tracking_path.exists():
            self.tracking_df = pd.read_csv(tracking_path)
            print(f"Loaded competitive tracking data: {len(self.tracking_df)} records")
        else:
            raise FileNotFoundError(f"Competitive tracking data not found at {tracking_path}")

    # ========================================================================
    # Query Methods (MCP Tools)
    # ========================================================================

    def query_competitor_pool(self, filters: Optional[Dict] = None) -> pd.DataFrame:
        """Query expats currently on competitor plans."""
        result = self.competitor_pool_df.copy()

        if filters:
            if "us_state" in filters:
                result = result[result["us_state"] == filters["us_state"]]
            if "plan_status" in filters:
                result = result[result["plan_status"] == filters["plan_status"]]
            if "current_provider" in filters:
                result = result[result["current_provider"] == filters["current_provider"]]

        return result

    def query_ratha_customers(self, filters: Optional[Dict] = None) -> pd.DataFrame:
        """Query Ratha Chakram customers."""
        result = self.ratha_df.copy()

        if filters:
            if "us_state" in filters:
                result = result[result["us_state"] == filters["us_state"]]
            if "coverage_types" in filters:
                result = result[result["coverage_types"] == filters["coverage_types"]]

        return result

    def query_tracking(self, filters: Optional[Dict] = None) -> pd.DataFrame:
        """Query competitive switch-tracking history."""
        result = self.tracking_df.copy()

        if filters:
            if "previous_company" in filters:
                result = result[result["previous_company"] == filters["previous_company"]]

        return result

    def customers_switched(self) -> Dict:
        """
        Find expats who switched from a competitor to Ratha Chakram.

        Returns:
            Dict with count and sample data
        """
        return {
            "count": len(self.ratha_df),
            "percentage": round((len(self.ratha_df) / len(self.competitor_pool_df)) * 100, 2),
            "sample_records": self.ratha_df.head(5).to_dict("records"),
        }

    def customers_retained_by_competitors(self) -> Dict:
        """
        Find expats who remained on competitor plans (did not switch to Ratha).

        Returns:
            Dict with count and status breakdown
        """
        switched_ids = set(self.ratha_df["expat_id"])
        retained = self.competitor_pool_df[~self.competitor_pool_df["expat_id"].isin(switched_ids)]

        return {
            "count": len(retained),
            "percentage": round((len(retained) / len(self.competitor_pool_df)) * 100, 2),
            "by_status": retained["plan_status"].value_counts().to_dict(),
        }

    def switches_by_competitor(self) -> Dict:
        """
        Breakdown of Ratha switches by which competitor the expat came from.

        Returns:
            Dict with count and per-competitor breakdown
        """
        return {
            "count": len(self.ratha_df),
            "percentage": round((len(self.ratha_df) / len(self.competitor_pool_df)) * 100, 2),
            "by_competitor": self.ratha_df["switched_from"].value_counts().to_dict(),
            "sample_records": self.ratha_df.head(5).to_dict("records"),
        }

    def get_switch_reasons(self) -> Dict:
        """
        Reasons expats left their previous competitor and chose Ratha Chakram.

        Returns:
            Dict with reason breakdowns
        """
        return {
            "total_switched": len(self.tracking_df),
            "reason_left_previous": self.tracking_df["reason_left_previous"].value_counts().to_dict(),
            "reason_chose_ratha": self.tracking_df["reason_chose_ratha"].value_counts().to_dict(),
            "details": self.tracking_df.head(10).to_dict("records"),
        }

    def cross_join_analysis(self) -> Dict:
        """
        Cross-store analysis of competitive migration patterns.

        Returns:
            Comprehensive summary
        """
        switched = self.customers_switched()
        retained = self.customers_retained_by_competitors()
        by_competitor = self.switches_by_competitor()
        reasons = self.get_switch_reasons()

        total = len(self.competitor_pool_df)

        return {
            "total_competitor_pool": total,
            "switched": {
                "count": switched["count"],
                "percentage": switched["percentage"],
            },
            "retained_by_competitors": {
                "count": retained["count"],
                "percentage": retained["percentage"],
            },
            "by_competitor": by_competitor["by_competitor"],
            "switch_reasons": reasons["reason_chose_ratha"],
            "summary": f"Out of {total} expats on competitor plans: {switched['count']} switched to Ratha Chakram "
                      f"({switched['percentage']}%), and {retained['count']} remain with competitors "
                      f"({retained['percentage']}%).",
        }
