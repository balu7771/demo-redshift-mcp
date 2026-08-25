"""CrewAI agents for Ratha Chakram expat competitive migration analysis."""

from dotenv import load_dotenv
load_dotenv()

import os

from crewai import Agent, Task, Crew
from .mcp_server import create_mcp_tools
import json

# ============================================================================
# Setup MCP Tools
# ============================================================================

mcp = create_mcp_tools()

# CrewAI defaults to "gpt-4.1-mini" when no llm is set on an Agent, which
# fails with a 403 for OpenAI projects lacking access to that model.
# Override via CREWAI_MODEL; defaults to Claude since ANTHROPIC_API_KEY
# is already required for this project.
LLM_MODEL = os.getenv("CREWAI_MODEL", "anthropic/claude-sonnet-5")

# ============================================================================
# Define CrewAI Tools (Wrapper)
# ============================================================================

from crewai.tools import tool

@tool("GetSwitchedCount")
def get_switched_count():
    """Get count of expats who switched from a competitor to Ratha Chakram"""
    return mcp.get_switched_customers_count()

@tool("GetRetainedCount")
def get_retained_count():
    """Get count of expats who remain on competitor plans"""
    return mcp.get_retained_by_competitors_count()

@tool("GetSwitchesByCompetitor")
def get_switches_by_competitor():
    """Get breakdown of switches to Ratha Chakram by originating competitor"""
    return mcp.get_switches_by_competitor()

@tool("GetSwitchReasons")
def get_switch_reasons():
    """Get reasons why expats left competitors and chose Ratha Chakram"""
    return mcp.get_switch_reasons()

@tool("GetComprehensiveAnalysis")
def get_comprehensive_analysis():
    """Get full cross-store competitive migration analysis"""
    return mcp.get_comprehensive_analysis()

@tool("QueryByState")
def query_by_state(state: str):
    """Get competitor-pool expat stats for a specific US state"""
    return mcp.query_competitor_pool_by_state(state)

@tool("QueryByCoverageType")
def query_by_coverage_type(coverage_type: str):
    """Get Ratha Chakram customers by coverage type (Auto, Health, Renter, Auto+Health)"""
    return mcp.query_ratha_by_coverage_type(coverage_type)

@tool("CompetitorAnalysis")
def competitor_analysis(competitor: str):
    """Get stats for a specific competitor (Allianz, AIG, ICICI Lombard, HDFC ERGO, CHUBB, IMG Global)"""
    return mcp.get_competitor_analysis(competitor)

# ============================================================================
# Agents
# ============================================================================

query_router = Agent(
    role="Query Router",
    goal="Understand expat competitive migration questions and select the right data tool to answer them",
    backstory="Expert at interpreting business questions about expats switching from competitor "
              "insurance plans to Ratha Chakram. Must call appropriate tools: GetSwitchedCount, "
              "GetRetainedCount, GetSwitchesByCompetitor, GetSwitchReasons, or GetComprehensiveAnalysis "
              "based on what the executive asks.",
    verbose=True,
    llm=LLM_MODEL,
    tools=[
        get_switched_count,
        get_retained_count,
        get_switches_by_competitor,
        get_switch_reasons,
        get_comprehensive_analysis,
        query_by_state,
        query_by_coverage_type,
        competitor_analysis,
    ],
)

analysis_supervisor = Agent(
    role="Analysis Supervisor",
    goal="Review router's findings and produce clear, executive-ready insights",
    backstory="Senior business analyst with deep expat insurance industry knowledge. "
              "Formats data into actionable insights for executives. "
              "Always explains WHAT the number means and WHY it matters.",
    verbose=True,
    llm=LLM_MODEL,
    tools=[],
)

# ============================================================================
# Main Workflow
# ============================================================================

def run_customer_migration_analysis(user_question: str) -> str:
    """
    Main entry point: execute the crew to answer an expat competitive migration question.

    Args:
        user_question: Executive's natural language question

    Returns:
        Final formatted response
    """

    if not user_question or len(user_question.strip()) == 0:
        return "Please ask a question about expat customer migration (e.g., 'How many expats switched to Ratha Chakram?')"

    # ========================================================================
    # Task 1: Route the Question
    # ========================================================================
    routing_task = Task(
        description=f"Analyze this expat competitive migration question and use the appropriate tools "
                   f"to fetch data:\n\nQuestion: {user_question}\n\n"
                   f"Decide which tool to call based on keywords:\n"
                   f"- 'switched', 'moved', 'converted' → GetSwitchedCount\n"
                   f"- 'retained', 'stayed', 'remain with competitor' → GetRetainedCount\n"
                   f"- 'by competitor', 'which competitor', 'from which provider' → GetSwitchesByCompetitor\n"
                   f"- 'why' + 'switched', 'reasons' → GetSwitchReasons\n"
                   f"- 'overall', 'summary', 'total' → GetComprehensiveAnalysis\n"
                   f"- State-specific → QueryByState\n"
                   f"- Coverage-type-specific → QueryByCoverageType\n"
                   f"- Named competitor (e.g. Allianz, AIG) → CompetitorAnalysis",
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
