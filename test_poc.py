#!/usr/bin/env python3
"""
Quick test script to verify the POC works end-to-end.
Run this to test data generation, MCP tools, and CrewAI agents.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from demo_redshift_mcp.data_generator import generate_all_data
from demo_redshift_mcp.data_layer import DataLayer
from demo_redshift_mcp.mcp_server import create_mcp_tools

# Note: CrewAI import is lazy-loaded due to Python 3.14 compatibility issues

def test_data_generation():
    """Test: Generate mock data."""
    print("\n" + "=" * 70)
    print("TEST 1: Data Generation")
    print("=" * 70)

    try:
        legacy, new_product, competitor = generate_all_data()
        print("✅ Data generation successful")
        print(f"   • Legacy: {len(legacy)} customers")
        print(f"   • New Product: {len(new_product)} customers")
        print(f"   • Competitor Records: {len(competitor)} records")
        return True
    except Exception as e:
        print(f"❌ Data generation failed: {e}")
        return False

def test_data_layer():
    """Test: Data layer queries."""
    print("\n" + "=" * 70)
    print("TEST 2: Data Layer Queries")
    print("=" * 70)

    try:
        data = DataLayer()

        # Test 1: Renewed customers
        renewed = data.customers_renewed()
        print(f"✅ Renewed customers: {renewed['count']} ({renewed['percentage']}%)")

        # Test 2: Customers left
        left = data.customers_left()
        print(f"✅ Customers left: {left['count']} ({left['percentage']}%)")

        # Test 3: Returned customers
        returned = data.customers_returned()
        print(f"✅ Returned customers: {returned['count']} ({returned['percentage']}%)")

        # Test 4: Return reasons
        reasons = data.infer_return_reasons()
        print(f"✅ Return reasons analyzed: {reasons['total_came_back']} customers")
        for reason, count in reasons['reason_breakdown'].items():
            print(f"   • {reason}: {count}")

        # Test 5: Cross-store analysis
        analysis = data.cross_join_analysis()
        print(f"✅ Cross-store analysis:")
        print(f"   {analysis['summary']}")

        return True
    except Exception as e:
        print(f"❌ Data layer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mcp_tools():
    """Test: MCP tools."""
    print("\n" + "=" * 70)
    print("TEST 3: MCP Tools")
    print("=" * 70)

    try:
        mcp = create_mcp_tools()

        print("✅ Testing MCP tools:")
        print(f"   • Renewed: {mcp.get_renewed_customers_count()}")
        print(f"   • Left: {mcp.get_customers_left_count()}")
        print(f"   • Returned: {mcp.get_returned_customers_count()}")
        print(f"   • Reasons: {mcp.get_return_reasons()}")

        return True
    except Exception as e:
        print(f"❌ MCP tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_crew_agents():
    """Test: CrewAI agents (optional - requires API key)."""
    print("\n" + "=" * 70)
    print("TEST 4: CrewAI Agents")
    print("=" * 70)

    try:
        # Check if API key is available
        import os
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("⚠️  ANTHROPIC_API_KEY not set. Skipping CrewAI test.")
            print("   Set it in .env file to test the full workflow.")
            return None

        from demo_redshift_mcp.crew_agents import run_customer_migration_analysis

        print("Testing CrewAI with sample question...")
        result = run_customer_migration_analysis("How many customers renewed?")
        print("✅ CrewAI agents working")
        print(f"   Response (first 200 chars): {str(result)[:200]}...")

        return True
    except Exception as e:
        print(f"❌ CrewAI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("\n" + "🧪 " * 20)
    print("Insurance Customer Migration POC - Test Suite")
    print("🧪 " * 20)

    results = {}

    # Test 1: Data generation
    results["Data Generation"] = test_data_generation()

    # Test 2: Data layer
    results["Data Layer"] = test_data_layer()

    # Test 3: MCP tools
    results["MCP Tools"] = test_mcp_tools()

    # Test 4: CrewAI (optional)
    results["CrewAI Agents"] = test_crew_agents()

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v is True)
    skipped = sum(1 for v in results.values() if v is None)
    failed = sum(1 for v in results.values() if v is False)

    for test_name, result in results.items():
        status = "✅ PASS" if result is True else ("⏭️ SKIP" if result is None else "❌ FAIL")
        print(f"{status:10} {test_name}")

    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {skipped} skipped, {failed} failed")
    print("=" * 70)

    if failed > 0:
        print("\n❌ Some tests failed. Check errors above.")
        sys.exit(1)
    else:
        print("\n✅ All required tests passed!")
        print("\nNext steps:")
        print("1. Set ANTHROPIC_API_KEY in .env to enable CrewAI tests")
        print("2. Run: python -m demo_redshift_mcp")
        print("3. Open http://localhost:7860 in your browser")
        sys.exit(0)

if __name__ == "__main__":
    main()
