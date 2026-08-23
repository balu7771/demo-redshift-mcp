"""Data access layer for insurance customer data."""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# ============================================================================
# Data Loader
# ============================================================================

class DataLayer:
    """Unified data access layer for legacy, new product, and competitor data."""

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.legacy_df = None
        self.new_product_df = None
        self.competitor_df = None
        self._load_all_data()

    def _load_all_data(self):
        """Load all datasets from disk."""
        legacy_path = self.data_dir / "legacy_product.xlsx"
        new_product_path = self.data_dir / "new_product_customers.csv"
        competitor_path = self.data_dir / "competitor_coverage.csv"

        if legacy_path.exists():
            self.legacy_df = pd.read_excel(legacy_path)
            print(f"Loaded legacy data: {len(self.legacy_df)} customers")
        else:
            raise FileNotFoundError(f"Legacy data not found at {legacy_path}")

        if new_product_path.exists():
            self.new_product_df = pd.read_csv(new_product_path)
            print(f"Loaded new product data: {len(self.new_product_df)} customers")
        else:
            raise FileNotFoundError(f"New product data not found at {new_product_path}")

        if competitor_path.exists():
            self.competitor_df = pd.read_csv(competitor_path)
            print(f"Loaded competitor data: {len(self.competitor_df)} records")
        else:
            raise FileNotFoundError(f"Competitor data not found at {competitor_path}")

    # ========================================================================
    # Query Methods (MCP Tools)
    # ========================================================================

    def query_legacy_customers(self, filters: Optional[Dict] = None) -> pd.DataFrame:
        """Query legacy product customers."""
        result = self.legacy_df.copy()

        if filters:
            if "state" in filters:
                result = result[result["state"] == filters["state"]]
            if "status" in filters:
                result = result[result["status"] == filters["status"]]
            if "coverage_type" in filters:
                result = result[result["coverage_type"] == filters["coverage_type"]]

        return result

    def query_new_product_customers(self, filters: Optional[Dict] = None) -> pd.DataFrame:
        """Query new product customers."""
        result = self.new_product_df.copy()

        if filters:
            if "state" in filters:
                result = result[result["state"] == filters["state"]]
            if "feature_adoption" in filters:
                result = result[result["feature_adoption"] == filters["feature_adoption"]]

        return result

    def query_competitor_coverage(self, filters: Optional[Dict] = None) -> pd.DataFrame:
        """Query competitor coverage history."""
        result = self.competitor_df.copy()

        if filters:
            if "competitor_name" in filters:
                result = result[result["competitor_name"] == filters["competitor_name"]]
            if "was_customer_with_us_before" in filters:
                result = result[result["was_customer_with_us_before"] == filters["was_customer_with_us_before"]]

        return result

    def customers_renewed(self) -> Dict:
        """
        Find customers who renewed from legacy to new product.

        Returns:
            Dict with count and sample data
        """
        renewed_dls = set(self.new_product_df["driver_license"])
        legacy_active = self.legacy_df[self.legacy_df["driver_license"].isin(renewed_dls)]

        return {
            "count": len(renewed_dls),
            "percentage": round((len(renewed_dls) / len(self.legacy_df)) * 100, 2),
            "sample_records": legacy_active.head(5).to_dict("records"),
        }

    def customers_left(self) -> Dict:
        """
        Find customers who left (not in new product).

        Returns:
            Dict with count and details
        """
        renewed_dls = set(self.new_product_df["driver_license"])
        left = self.legacy_df[~self.legacy_df["driver_license"].isin(renewed_dls)]

        return {
            "count": len(left),
            "percentage": round((len(left) / len(self.legacy_df)) * 100, 2),
            "by_status": left["status"].value_counts().to_dict(),
        }

    def customers_returned(self) -> Dict:
        """
        Find customers who went to competitor then came back to new product.

        Returns:
            Dict with count and analysis
        """
        # Customers with competitor history who ended coverage
        competitor_history = self.competitor_df[
            (self.competitor_df["coverage_end"].notna()) &
            (self.competitor_df["was_customer_with_us_before"] == True)
        ]

        # Check if they're in new product
        came_back_dls = set(self.new_product_df["driver_license"])
        returned = competitor_history[competitor_history["driver_license"].isin(came_back_dls)]

        return {
            "count": len(returned),
            "percentage": round((len(returned) / len(self.legacy_df)) * 100, 2),
            "by_competitor": returned["competitor_name"].value_counts().to_dict(),
            "sample_records": returned.head(5).to_dict("records"),
        }

    def infer_return_reasons(self) -> Dict:
        """
        Infer why customers came back based on feature/pricing differences.

        Uses soft inference:
        - Premium drop > 15% → "Price-Sensitive"
        - Feature adoption "CONNECTED" → "Innovation"
        - Feature adoption "SIMPLE" → "Simplicity"
        - Combination → "Value + Features"

        Returns:
            Dict with reason breakdown
        """
        came_back_dls = set(
            self.competitor_df[
                (self.competitor_df["coverage_end"].notna()) &
                (self.competitor_df["was_customer_with_us_before"] == True)
            ]["driver_license"]
        )

        # Get matching customers in both legacy and new product
        came_back_customers = []
        for dl in came_back_dls:
            legacy = self.legacy_df[self.legacy_df["driver_license"] == dl]
            new = self.new_product_df[self.new_product_df["driver_license"] == dl]

            if not legacy.empty and not new.empty:
                came_back_customers.append({
                    "driver_license": dl,
                    "legacy_premium": legacy.iloc[0]["premium_6month"],
                    "new_premium": new.iloc[0]["premium_6month"],
                    "feature_adoption": new.iloc[0]["feature_adoption"],
                })

        reasons_count = {
            "Price-Sensitive": 0,
            "Innovation": 0,
            "Simplicity": 0,
            "Value + Features": 0,
        }

        for customer in came_back_customers:
            premium_drop = (
                (customer["legacy_premium"] - customer["new_premium"]) /
                customer["legacy_premium"] * 100
            )

            reasons = []
            if premium_drop > 15:
                reasons.append("Price")

            if customer["feature_adoption"] == "CONNECTED":
                reasons.append("Innovation")
            elif customer["feature_adoption"] == "SIMPLE":
                reasons.append("Simplicity")

            if len(reasons) == 0:
                final_reason = "Value + Features"
            elif len(reasons) == 1:
                final_reason = reasons[0] + ("-Sensitive" if reasons[0] == "Price" else "")
            else:
                final_reason = "Value + Features"

            reasons_count[final_reason] += 1

        return {
            "total_came_back": len(came_back_customers),
            "reason_breakdown": reasons_count,
            "details": came_back_customers[:10],  # Sample
        }

    def cross_join_analysis(self) -> Dict:
        """
        Cross-store analysis of all migration patterns.

        Returns:
            Comprehensive summary
        """
        renewed = self.customers_renewed()
        left = self.customers_left()
        returned = self.customers_returned()
        reasons = self.infer_return_reasons()

        total = len(self.legacy_df)

        return {
            "total_legacy_customers": total,
            "renewed": {
                "count": renewed["count"],
                "percentage": renewed["percentage"],
            },
            "left": {
                "count": left["count"],
                "percentage": left["percentage"],
            },
            "returned": {
                "count": returned["count"],
                "percentage": returned["percentage"],
            },
            "return_reasons": reasons["reason_breakdown"],
            "summary": f"Out of {total} legacy customers: {renewed['count']} renewed "
                      f"({renewed['percentage']}%), {left['count']} left ({left['percentage']}%), "
                      f"and {returned['count']} came back ({returned['percentage']}%)",
        }
