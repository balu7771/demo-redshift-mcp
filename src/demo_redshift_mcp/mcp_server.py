"""MCP Server exposing insurance data tools."""

from .data_layer import DataLayer

# ============================================================================
# MCP Tools (For CrewAI Agents)
# ============================================================================

class InsuranceMCPTools:
    """MCP tools for querying insurance customer data."""

    def __init__(self, data_layer: DataLayer):
        self.data = data_layer

    # ========================================================================
    # Individual Query Tools
    # ========================================================================

    def get_renewed_customers_count(self) -> str:
        """Get count of customers who renewed from legacy to new product."""
        result = self.data.customers_renewed()
        return f"Renewed Customers: {result['count']} ({result['percentage']}% of legacy)"

    def get_customers_left_count(self) -> str:
        """Get count of customers who left and didn't renew."""
        result = self.data.customers_left()
        breakdown = ", ".join([f"{k}: {v}" for k, v in result["by_status"].items()])
        return f"Customers Left: {result['count']} ({result['percentage']}% of legacy). By Status: {breakdown}"

    def get_returned_customers_count(self) -> str:
        """Get count of customers who came back from competitors."""
        result = self.data.customers_returned()
        by_competitor = ", ".join([f"{k}: {v}" for k, v in result["by_competitor"].items()])
        return f"Returned Customers: {result['count']} ({result['percentage']}% of legacy). From: {by_competitor}"

    def get_return_reasons(self) -> str:
        """Get inferred reasons why customers came back."""
        result = self.data.infer_return_reasons()
        breakdown = ", ".join([f"{k}: {v}" for k, v in result["reason_breakdown"].items()])
        return f"Return Reasons: {breakdown}. (Based on pricing & feature analysis)"

    def get_comprehensive_analysis(self) -> str:
        """Get comprehensive cross-store migration analysis."""
        result = self.data.cross_join_analysis()
        return result["summary"] + f"\n\nReturn Reasons Breakdown:\n" + \
               "\n".join([f"  • {k}: {v}" for k, v in result["return_reasons"].items()])

    # ========================================================================
    # Supporting Query Tools
    # ========================================================================

    def query_legacy_by_state(self, state: str) -> str:
        """Get legacy customers for a specific state."""
        result = self.data.query_legacy_customers({"state": state})
        return f"Legacy customers in {state}: {len(result)} customers. Avg premium: ${result['premium_6month'].mean():.2f}"

    def query_new_product_by_feature(self, feature: str) -> str:
        """Get new product customers by feature adoption."""
        result = self.data.query_new_product_customers({"feature_adoption": feature})
        return f"New product customers with {feature} feature: {len(result)} customers. Avg premium: ${result['premium_6month'].mean():.2f}"

    def get_competitor_analysis(self, competitor: str) -> str:
        """Get customers who went to a specific competitor."""
        result = self.data.query_competitor_coverage({"competitor_name": competitor})
        active_coverage = result[result["coverage_end"].isna()]
        returned = result[result["coverage_end"].notna()]
        return f"{competitor}: {len(active_coverage)} still there, {len(returned)} came back"


# ============================================================================
# Factory Function
# ============================================================================

def create_mcp_tools(data_dir: str = "./data") -> InsuranceMCPTools:
    """Create MCP tools instance with data layer."""
    data_layer = DataLayer(data_dir=data_dir)
    return InsuranceMCPTools(data_layer)
