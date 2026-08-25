"""MCP Server exposing Ratha Chakram expat insurance data tools."""

from .data_layer import DataLayer

# ============================================================================
# MCP Tools (For CrewAI Agents)
# ============================================================================

class InsuranceMCPTools:
    """MCP tools for querying Ratha Chakram expat insurance data."""

    def __init__(self, data_layer: DataLayer):
        self.data = data_layer

    # ========================================================================
    # Individual Query Tools
    # ========================================================================

    def get_switched_customers_count(self) -> str:
        """Get count of expats who switched from a competitor to Ratha Chakram."""
        result = self.data.customers_switched()
        return f"Switched to Ratha Chakram: {result['count']} ({result['percentage']}% of competitor pool)"

    def get_retained_by_competitors_count(self) -> str:
        """Get count of expats who remain on competitor plans."""
        result = self.data.customers_retained_by_competitors()
        breakdown = ", ".join([f"{k}: {v}" for k, v in result["by_status"].items()])
        return f"Retained by Competitors: {result['count']} ({result['percentage']}% of competitor pool). By Status: {breakdown}"

    def get_switches_by_competitor(self) -> str:
        """Get breakdown of Ratha switches by which competitor the expat came from."""
        result = self.data.switches_by_competitor()
        by_competitor = ", ".join([f"{k}: {v}" for k, v in result["by_competitor"].items()])
        return f"Switched Customers: {result['count']} ({result['percentage']}% of competitor pool). From: {by_competitor}"

    def get_switch_reasons(self) -> str:
        """Get reasons why expats left competitors and chose Ratha Chakram."""
        result = self.data.get_switch_reasons()
        left = ", ".join([f"{k}: {v}" for k, v in result["reason_left_previous"].items()])
        chose = ", ".join([f"{k}: {v}" for k, v in result["reason_chose_ratha"].items()])
        return f"Reasons left previous provider: {left}. Reasons chose Ratha Chakram: {chose}."

    def get_comprehensive_analysis(self) -> str:
        """Get comprehensive cross-store competitive migration analysis."""
        result = self.data.cross_join_analysis()
        return result["summary"] + f"\n\nSwitch Reasons Breakdown:\n" + \
               "\n".join([f"  • {k}: {v}" for k, v in result["switch_reasons"].items()])

    # ========================================================================
    # Supporting Query Tools
    # ========================================================================

    def query_competitor_pool_by_state(self, state: str) -> str:
        """Get competitor-pool expats for a specific US state."""
        result = self.data.query_competitor_pool({"us_state": state})
        return f"Expats on competitor plans in {state}: {len(result)}. Avg premium: ${result['monthly_premium'].mean():.2f}"

    def query_ratha_by_coverage_type(self, coverage_type: str) -> str:
        """Get Ratha Chakram customers by coverage type (Auto, Health, Renter, Auto+Health)."""
        result = self.data.query_ratha_customers({"coverage_types": coverage_type})
        return f"Ratha customers with {coverage_type} coverage: {len(result)}. Avg premium: ${result['ratha_monthly_premium'].mean():.2f}"

    def get_competitor_analysis(self, competitor: str) -> str:
        """Get stats for a specific competitor: how many expats remain vs switched away."""
        pool = self.data.query_competitor_pool({"current_provider": competitor})
        switched_away = self.data.query_ratha_customers()
        switched_away = switched_away[switched_away["switched_from"] == competitor]
        switched_ids = set(switched_away["expat_id"])
        remaining = pool[~pool["expat_id"].isin(switched_ids)]
        return f"{competitor}: {len(remaining)} still with them, {len(switched_away)} switched to Ratha Chakram"


# ============================================================================
# Factory Function
# ============================================================================

def create_mcp_tools(data_dir: str = "./data") -> InsuranceMCPTools:
    """Create MCP tools instance with data layer."""
    data_layer = DataLayer(data_dir=data_dir)
    return InsuranceMCPTools(data_layer)
