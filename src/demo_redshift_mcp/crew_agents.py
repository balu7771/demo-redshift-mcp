"""CrewAI agents for customer migration analysis."""

from crewai import Agent, Task, Crew
from .mcp_server import create_mcp_tools
import json

# ============================================================================
# Setup MCP Tools
# ============================================================================

mcp = create_mcp_tools()

# ============================================================================
# Define CrewAI Tools (Wrapper)
# ============================================================================

from crewai.tools import tool

@tool("GetRenewedCount")
def get_renewed_count():
    """Get count of customers who renewed into the new product"""
    return mcp.get_renewed_customers_count()

@tool("GetLeftCount")
def get_left_count():
    """Get count of customers who left for competitors"""
    return mcp.get_customers_left_count()

@tool("GetReturnedCount")
def get_returned_count():
    """Get count of customers who came back from competitors"""
    return mcp.get_returned_customers_count()

@tool("GetReturnReasons")
def get_return_reasons():
    """Get reasons why customers came back (price, features, etc)"""
    return mcp.get_return_reasons()

@tool("GetComprehensiveAnalysis")
def get_comprehensive_analysis():
    """Get full cross-store migration analysis"""
    return mcp.get_comprehensive_analysis()

@tool("QueryByState")
def query_by_state(state: str):
    """Get customer stats for a specific state"""
    return mcp.query_legacy_by_state(state)

@tool("QueryByFeature")
def query_by_feature(feature: str):
    """Get customers by feature adoption (SIMPLE, CONNECTED, PREMIUM)"""
    return mcp.query_new_product_by_feature(feature)

@tool("CompetitorAnalysis")
def competitor_analysis(competitor: str):
    """Get stats for a specific competitor (Allstate, Progressive, Geico, StateFarm)"""
    return mcp.get_competitor_analysis(competitor)

# ============================================================================
# Agents
# ============================================================================

query_router = Agent(
    role="Query Router",
    goal="Understand customer migration questions and select the right data tool to answer them",
    backstory="Expert at interpreting business questions about customer migration. "
              "Must call appropriate tools: GetRenewedCount, GetLeftCount, GetReturnedCount, "
              "GetReturnReasons, or GetComprehensiveAnalysis based on what the executive asks.",
    verbose=True,
    tools=[
        get_renewed_count,
        get_left_count,
        get_returned_count,
        get_return_reasons,
        get_comprehensive_analysis,
        query_by_state,
        query_by_feature,
        competitor_analysis,
    ],
)

analysis_supervisor = Agent(
    role="Analysis Supervisor",
    goal="Review router's findings and produce clear, executive-ready insights",
    backstory="Senior business analyst with deep insurance industry knowledge. "
              "Formats data into actionable insights for executives. "
              "Always explains WHAT the number means and WHY it matters.",
    verbose=True,
    tools=[],
)

# ============================================================================
# Main Workflow
# ============================================================================

def run_customer_migration_analysis(user_question: str) -> str:
    """
    Main entry point: execute the crew to answer a customer migration question.

    Args:
        user_question: Executive's natural language question

    Returns:
        Final formatted response
    """

    if not user_question or len(user_question.strip()) == 0:
        return "Please ask a question about customer migration (e.g., 'How many customers renewed?')"

    # ========================================================================
    # Task 1: Route the Question
    # ========================================================================
    routing_task = Task(
        description=f"Analyze this customer migration question and use the appropriate tools "
                   f"to fetch data:\n\nQuestion: {user_question}\n\n"
                   f"Decide which tool to call based on keywords:\n"
                   f"- 'renewed', 'moved', 'upgraded' → GetRenewedCount\n"
                   f"- 'left', 'cancelled', 'competitor' → GetLeftCount\n"
                   f"- 'returned', 'came back', 'win-back' → GetReturnedCount\n"
                   f"- 'why' + 'came back', 'reasons' → GetReturnReasons\n"
                   f"- 'overall', 'summary', 'total' → GetComprehensiveAnalysis\n"
                   f"- State-specific → QueryByState\n"
                   f"- Feature-specific → QueryByFeature",
        expected_output="Tool results with raw data and metrics",
        agent=query_router,
    )

    # ========================================================================
    # Task 2: Analyze & Format
    # ========================================================================
    analysis_task = Task(
        description=f"Based on the router's tool results, provide an executive summary that:\n"
                   f"1. States the key metric clearly\n"
                   f"2. Explains what it means in business terms\n"
                   f"3. Provides actionable insights\n"
                   f"4. Suggests next steps if relevant\n\n"
                   f"Original question: {user_question}",
        expected_output="Clear, actionable business insights formatted for executives",
        agent=analysis_supervisor,
        context=[routing_task],
    )

    # ========================================================================
    # Execute Crew
    # ========================================================================
    crew = Crew(
        agents=[query_router, analysis_supervisor],
        tasks=[routing_task, analysis_task],
        verbose=True,
    )

    try:
        result = crew.kickoff()
        return str(result)
    except Exception as e:
        return f"Analysis failed: {str(e)}"
