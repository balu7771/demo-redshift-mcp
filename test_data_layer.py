#!/usr/bin/env python3
"""
Test the data layer and MCP tools directly (no CrewAI dependency).
This tests the core analysis logic without Python version issues.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from demo_redshift_mcp.data_generator import generate_all_data
from demo_redshift_mcp.data_layer import DataLayer
from demo_redshift_mcp.mcp_server import create_mcp_tools

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

        # Show sample data
        print("\n   Sample Legacy Customer:")
        print(f"      {legacy.iloc[0].to_dict()}")
        return True
    except Exception as e:
        print(f"❌ Data generation failed: {e}")
        import traceback
        traceback.print_exc()
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
        print(f"   By status: {left['by_status']}")

        # Test 3: Returned customers
        returned = data.customers_returned()
        print(f"✅ Returned customers: {returned['count']} ({returned['percentage']}%)")
        print(f"   By competitor: {returned['by_competitor']}")

        # Test 4: Return reasons
        reasons = data.infer_return_reasons()
        print(f"✅ Return reasons analyzed:")
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
        print(f"   • {mcp.get_renewed_customers_count()}")
        print(f"   • {mcp.get_customers_left_count()}")
        print(f"   • {mcp.get_returned_customers_count()}")
        print(f"   • {mcp.get_return_reasons()}")
        print(f"   • {mcp.get_comprehensive_analysis()}")

        return True
    except Exception as e:
        print(f"❌ MCP tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("\n" + "🧪 " * 20)
    print("Insurance Customer Migration POC - Data Layer Tests")
    print("🧪 " * 20)

    results = {}

    # Test 1: Data generation
    results["Data Generation"] = test_data_generation()

    # Test 2: Data layer
    results["Data Layer"] = test_data_layer()

    # Test 3: MCP tools
    results["MCP Tools"] = test_mcp_tools()

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)

    for test_name, result in results.items():
        status = "✅ PASS" if result is True else "❌ FAIL"
        print(f"{status:10} {test_name}")

    print("\n" + "=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)

    if failed > 0:
        print("\n❌ Some tests failed. Check errors above.")
        sys.exit(1)
    else:
        print("\n✅ All data layer tests passed!")
        print("\nThe core analysis engine is working correctly.")
        print("Data is ready in: ./data/")
        print("\nNote: Full Gradio UI requires Python < 3.14 due to CrewAI compatibility.")
        print("When running on Python 3.13 or lower:")
        print("  1. pip install -r requirements.txt")
        print("  2. python -m demo_redshift_mcp")
        print("  3. Open http://localhost:7860")
        sys.exit(0)

if __name__ == "__main__":
    main()
