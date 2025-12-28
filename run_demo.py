"""
MAIN DEMO SCRIPT
Run this to execute complete Apple Financial Analysis
"""

from apple_financial_agent import AppleFinancialAgent, quick_test
from report_generator import generate_all_reports
import sys


def main():
    """
    Main execution function
    """
    print("\n" + "="*70)
    print(" "*15 + "🍎 APPLE FINANCIAL ANALYSIS AI AGENT")
    print("="*70)
    print("\nThis demo will:")
    print("  1. Fetch Apple's latest financial statements")
    print("  2. Calculate profitability bridges (EBIT drivers)")
    print("  3. Analyze cash flow (Net Income → FCF)")
    print("  4. Examine working capital efficiency")
    print("  5. Generate management summary")
    print("  6. Export reports to Excel, charts, and text")
    print("\n" + "="*70)
    
    input("\nPress ENTER to begin analysis...")
    
    try:
        # Step 1: Run financial analysis
        print("\n🚀 STEP 1: Running Financial Analysis...")
        agent = AppleFinancialAgent()
        results = agent.run_complete_analysis()
        
        # Display results in console
        print("\n" + "="*70)
        print("📊 ANALYSIS RESULTS")
        print("="*70)
        
        print("\n1️⃣ PROFITABILITY BRIDGE")
        print("-" * 70)
        print(results['profitability_bridge'].to_string(index=False))
        
        print("\n\n2️⃣ CASH FLOW BRIDGE")
        print("-" * 70)
        print(results['cash_flow_bridge'].to_string(index=False))
        
        print("\n\n3️⃣ WORKING CAPITAL ANALYSIS")
        print("-" * 70)
        print(results['working_capital'].to_string(index=False))
        
        print("\n\n4️⃣ MANAGEMENT SUMMARY")
        print("-" * 70)
        print(results['management_summary'])
        
        # Step 2: Generate reports
        print("\n\n🚀 STEP 2: Generating Reports...")
        reports = generate_all_reports(agent)
        
        print("\n" + "="*70)
        print("✅ ANALYSIS COMPLETE!")
        print("="*70)
        print("\nYour reports are ready:")
        print(f"\n📊 Excel Workbook: {reports['excel']}")
        print(f"📄 Text Summary: {reports['summary']}")
        print(f"\n📈 Charts Generated:")
        for chart in reports['charts']:
            print(f"    • {chart}")
        
        print("\n" + "="*70)
        print("💡 Next Steps:")
        print("="*70)
        print("1. Open the Excel file for detailed analysis")
        print("2. Review the PNG charts for visual insights")
        print("3. Share the text summary with stakeholders")
        print("\n" + "="*70)
        
        return agent, reports
        
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        print("\nPlease ensure:")
        print("  • You have internet connection (to fetch financial data)")
        print("  • All dependencies are installed: pip install -r requirements.txt")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    agent, reports = main()
    
    print("\n🎉 Demo completed successfully!")
    print("\nThe agent object contains all analysis results.")
    print("Access them via: agent.analysis_results")
