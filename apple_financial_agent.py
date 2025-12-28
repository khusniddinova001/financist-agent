"""
Apple Financial Analysis AI Agent
Performs automated financial statement analysis including profitability bridges,
cash flow bridges, and working capital analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import yfinance as yf
import requests
from typing import Dict, List, Tuple
import json

class AppleFinancialAgent:
    """
    AI Agent for analyzing Apple's financial statements
    """
    
    def __init__(self):
        self.ticker = "AAPL"
        self.company_name = "Apple Inc."
        self.financial_data = {}
        self.analysis_results = {}
        
    def fetch_financial_statements(self) -> Dict:
        """
        Fetch Apple's financial statements using yfinance
        Returns: Dictionary containing income statement, balance sheet, cash flow
        """
        print("📊 Fetching Apple financial data...")
        
        apple = yf.Ticker(self.ticker)
        
        # Get financial statements
        self.financial_data = {
            'income_statement': apple.financials,  # Annual income statement
            'quarterly_income': apple.quarterly_financials,
            'balance_sheet': apple.balance_sheet,  # Annual balance sheet
            'quarterly_balance': apple.quarterly_balance_sheet,
            'cash_flow': apple.cashflow,  # Annual cash flow
            'quarterly_cashflow': apple.quarterly_cashflow,
            'info': apple.info
        }
        
        print(f"✅ Successfully fetched {len(self.financial_data['income_statement'].columns)} years of data")
        return self.financial_data
    
    def calculate_profitability_bridge(self) -> pd.DataFrame:
        """
        Calculate profitability bridge showing drivers of EBIT/EBITDA changes
        """
        print("\n🔍 Analyzing Profitability Bridge...")
        
        income_stmt = self.financial_data['income_statement']
        
        # Get the two most recent years
        years = income_stmt.columns[:2]
        current_year = years[0]
        prior_year = years[1]
        
        # Extract key metrics
        revenue_current = income_stmt.loc['Total Revenue', current_year]
        revenue_prior = income_stmt.loc['Total Revenue', prior_year]
        
        cogs_current = income_stmt.loc['Cost Of Revenue', current_year] if 'Cost Of Revenue' in income_stmt.index else 0
        cogs_prior = income_stmt.loc['Cost Of Revenue', prior_year] if 'Cost Of Revenue' in income_stmt.index else 0
        
        operating_income_current = income_stmt.loc['Operating Income', current_year]
        operating_income_prior = income_stmt.loc['Operating Income', prior_year]
        
        # Calculate gross profit
        gross_profit_current = revenue_current - cogs_current
        gross_profit_prior = revenue_prior - cogs_prior
        
        # Operating expenses
        opex_current = gross_profit_current - operating_income_current
        opex_prior = gross_profit_prior - operating_income_prior
        
        # Build the bridge
        bridge_data = {
            'Component': [
                'Prior Year EBIT',
                'Revenue Growth Impact',
                'Gross Margin Change',
                'Operating Expense Change',
                'Current Year EBIT',
                '',
                'EBIT Margin (Prior)',
                'EBIT Margin (Current)',
                'Margin Change'
            ],
            'Amount ($M)': [
                operating_income_prior / 1e6,
                (revenue_current - revenue_prior) * (gross_profit_prior / revenue_prior) / 1e6,
                ((gross_profit_current / revenue_current) - (gross_profit_prior / revenue_prior)) * revenue_current / 1e6,
                -(opex_current - opex_prior) / 1e6,
                operating_income_current / 1e6,
                np.nan,
                (operating_income_prior / revenue_prior) * 100,
                (operating_income_current / revenue_current) * 100,
                ((operating_income_current / revenue_current) - (operating_income_prior / revenue_prior)) * 100
            ]
        }
        
        bridge_df = pd.DataFrame(bridge_data)
        self.analysis_results['profitability_bridge'] = bridge_df
        
        print("✅ Profitability bridge calculated")
        return bridge_df
    
    def calculate_cash_flow_bridge(self) -> pd.DataFrame:
        """
        Calculate cash flow bridge: Net Income → Operating Cash Flow → Free Cash Flow
        """
        print("\n💰 Analyzing Cash Flow Bridge...")
        
        income_stmt = self.financial_data['income_statement']
        cash_flow = self.financial_data['cash_flow']
        
        current_year = cash_flow.columns[0]
        
        # Key metrics
        net_income = income_stmt.loc['Net Income', current_year]
        
        # Operating cash flow components
        depreciation = cash_flow.loc['Depreciation And Amortization', current_year] if 'Depreciation And Amortization' in cash_flow.index else 0
        
        stock_based_comp = 0
        if 'Stock Based Compensation' in cash_flow.index:
            stock_based_comp = cash_flow.loc['Stock Based Compensation', current_year]
        
        change_in_wc = cash_flow.loc['Change In Working Capital', current_year] if 'Change In Working Capital' in cash_flow.index else 0
        
        other_operating = 0
        if 'Other Operating Cash Flows Items' in cash_flow.index:
            other_operating = cash_flow.loc['Other Operating Cash Flows Items', current_year]
        
        operating_cf = cash_flow.loc['Operating Cash Flow', current_year]
        
        # Capex
        capex = cash_flow.loc['Capital Expenditure', current_year] if 'Capital Expenditure' in cash_flow.index else 0
        
        # Free cash flow
        free_cash_flow = operating_cf + capex  # Capex is negative
        
        # Build the bridge
        bridge_data = {
            'Component': [
                'Net Income',
                'Add: Depreciation & Amortization',
                'Add: Stock-Based Compensation',
                'Change in Working Capital',
                'Other Operating Adjustments',
                'Operating Cash Flow',
                '',
                'Less: Capital Expenditure',
                'Free Cash Flow',
                '',
                'Cash Conversion Rate (%)'
            ],
            'Amount ($M)': [
                net_income / 1e6,
                depreciation / 1e6,
                stock_based_comp / 1e6,
                change_in_wc / 1e6,
                other_operating / 1e6,
                operating_cf / 1e6,
                np.nan,
                capex / 1e6,
                free_cash_flow / 1e6,
                np.nan,
                (operating_cf / net_income) * 100
            ]
        }
        
        bridge_df = pd.DataFrame(bridge_data)
        self.analysis_results['cash_flow_bridge'] = bridge_df
        
        print("✅ Cash flow bridge calculated")
        return bridge_df
    
    def analyze_working_capital(self) -> pd.DataFrame:
        """
        Analyze working capital drivers (AR, Inventory, AP, etc.)
        """
        print("\n📦 Analyzing Working Capital Drivers...")
        
        balance_sheet = self.financial_data['balance_sheet']
        income_stmt = self.financial_data['income_statement']
        
        years = balance_sheet.columns[:2]
        current_year = years[0]
        prior_year = years[1]
        
        # Extract working capital components
        def get_value(metric, year, default=0):
            return balance_sheet.loc[metric, year] if metric in balance_sheet.index else default
        
        ar_current = get_value('Accounts Receivable', current_year)
        ar_prior = get_value('Accounts Receivable', prior_year)
        
        inventory_current = get_value('Inventory', current_year)
        inventory_prior = get_value('Inventory', prior_year)
        
        ap_current = get_value('Accounts Payable', current_year)
        ap_prior = get_value('Accounts Payable', prior_year)
        
        # Get revenue and COGS for ratio analysis
        revenue = income_stmt.loc['Total Revenue', current_year]
        cogs = income_stmt.loc['Cost Of Revenue', current_year] if 'Cost Of Revenue' in income_stmt.index else 0
        
        # Calculate days metrics
        dso_current = (ar_current / revenue) * 365 if revenue != 0 else 0
        dso_prior = (ar_prior / income_stmt.loc['Total Revenue', prior_year]) * 365
        
        dio_current = (inventory_current / cogs) * 365 if cogs != 0 else 0
        dio_prior = (inventory_prior / (income_stmt.loc['Cost Of Revenue', prior_year] if 'Cost Of Revenue' in income_stmt.index else 1)) * 365
        
        dpo_current = (ap_current / cogs) * 365 if cogs != 0 else 0
        dpo_prior = (ap_prior / (income_stmt.loc['Cost Of Revenue', prior_year] if 'Cost Of Revenue' in income_stmt.index else 1)) * 365
        
        # Cash conversion cycle
        ccc_current = dso_current + dio_current - dpo_current
        ccc_prior = dso_prior + dio_prior - dpo_prior
        
        wc_data = {
            'Metric': [
                'Accounts Receivable',
                'Inventory',
                'Accounts Payable',
                'Net Working Capital',
                '',
                'Days Sales Outstanding (DSO)',
                'Days Inventory Outstanding (DIO)',
                'Days Payable Outstanding (DPO)',
                'Cash Conversion Cycle (Days)',
                '',
                'YoY Change in WC',
                'Change in DSO',
                'Change in DIO',
                'Change in DPO',
                'Change in CCC'
            ],
            'Current Year': [
                ar_current / 1e6,
                inventory_current / 1e6,
                ap_current / 1e6,
                (ar_current + inventory_current - ap_current) / 1e6,
                np.nan,
                dso_current,
                dio_current,
                dpo_current,
                ccc_current,
                np.nan,
                ((ar_current + inventory_current - ap_current) - (ar_prior + inventory_prior - ap_prior)) / 1e6,
                dso_current - dso_prior,
                dio_current - dio_prior,
                dpo_current - dpo_prior,
                ccc_current - ccc_prior
            ],
            'Prior Year': [
                ar_prior / 1e6,
                inventory_prior / 1e6,
                ap_prior / 1e6,
                (ar_prior + inventory_prior - ap_prior) / 1e6,
                np.nan,
                dso_prior,
                dio_prior,
                dpo_prior,
                ccc_prior,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan,
                np.nan
            ]
        }
        
        wc_df = pd.DataFrame(wc_data)
        self.analysis_results['working_capital'] = wc_df
        
        print("✅ Working capital analysis completed")
        return wc_df
    
    def generate_management_summary(self) -> str:
        """
        Generate AI-powered management summary of financial performance
        """
        print("\n📝 Generating Management Summary...")
        
        # Extract key insights
        prof_bridge = self.analysis_results['profitability_bridge']
        cf_bridge = self.analysis_results['cash_flow_bridge']
        wc_analysis = self.analysis_results['working_capital']
        
        # Get key numbers
        ebit_change = prof_bridge.loc[prof_bridge['Component'] == 'Current Year EBIT', 'Amount ($M)'].values[0] - \
                      prof_bridge.loc[prof_bridge['Component'] == 'Prior Year EBIT', 'Amount ($M)'].values[0]
        
        margin_change = prof_bridge.loc[prof_bridge['Component'] == 'Margin Change', 'Amount ($M)'].values[0]
        
        fcf = cf_bridge.loc[cf_bridge['Component'] == 'Free Cash Flow', 'Amount ($M)'].values[0]
        cash_conversion = cf_bridge.loc[cf_bridge['Component'] == 'Cash Conversion Rate (%)', 'Amount ($M)'].values[0]
        
        ccc_change = wc_analysis.loc[wc_analysis['Metric'] == 'Change in CCC', 'Current Year'].values[0]
        
        summary = f"""
MANAGEMENT SUMMARY - {self.company_name}
{'='*60}

EXECUTIVE OVERVIEW
------------------
Apple's financial performance shows {"strong" if ebit_change > 0 else "declining"} operational 
momentum with EBIT {"increasing" if ebit_change > 0 else "decreasing"} by ${abs(ebit_change):,.0f}M 
year-over-year. Operating margins {"expanded" if margin_change > 0 else "contracted"} by 
{abs(margin_change):.2f} percentage points, reflecting {"improved operational efficiency" if margin_change > 0 else "margin pressure"}.

KEY FINANCIAL HIGHLIGHTS
------------------------
1. PROFITABILITY
   • EBIT Change: ${ebit_change:+,.0f}M ({'+' if ebit_change > 0 else ''}{(ebit_change/prof_bridge.loc[0, 'Amount ($M)']*100):.1f}%)
   • Margin Movement: {margin_change:+.2f}pp
   • Primary Driver: {"Revenue growth" if prof_bridge.loc[1, 'Amount ($M)'] > abs(prof_bridge.loc[2, 'Amount ($M)']) else "Margin expansion"}

2. CASH GENERATION
   • Free Cash Flow: ${fcf:,.0f}M
   • Cash Conversion Rate: {cash_conversion:.1f}%
   • Quality of Earnings: {"High - strong cash conversion" if cash_conversion > 90 else "Moderate - watch working capital"}

3. WORKING CAPITAL EFFICIENCY
   • Cash Conversion Cycle: {"Improved" if ccc_change < 0 else "Deteriorated"} by {abs(ccc_change):.1f} days
   • Working Capital Management: {"Efficient capital deployment" if ccc_change < 0 else "Requires attention"}

STRATEGIC IMPLICATIONS
---------------------
{"Apple demonstrates robust operational execution with strong cash generation and improving margins. The business model continues to generate high-quality earnings with excellent cash conversion." if ebit_change > 0 and margin_change > 0 else "Mixed performance signals warrant careful monitoring of operational efficiency and margin management."}

ANALYST RECOMMENDATION
---------------------
The financial fundamentals {"support a positive outlook" if fcf > 80000 and cash_conversion > 90 else "suggest cautious optimism"}. 
Management's capital allocation and operational discipline remain {"key strengths" if margin_change > 0 else "areas requiring focus"}.

{'='*60}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        self.analysis_results['management_summary'] = summary
        print("✅ Management summary generated")
        return summary
    
    def run_complete_analysis(self):
        """
        Execute complete financial analysis workflow
        """
        print("\n" + "="*60)
        print("🤖 APPLE FINANCIAL ANALYSIS AI AGENT")
        print("="*60)
        
        # Step 1: Fetch data
        self.fetch_financial_statements()
        
        # Step 2: Perform analyses
        self.calculate_profitability_bridge()
        self.calculate_cash_flow_bridge()
        self.analyze_working_capital()
        
        # Step 3: Generate summary
        self.generate_management_summary()
        
        print("\n" + "="*60)
        print("✅ ANALYSIS COMPLETE")
        print("="*60)
        
        return self.analysis_results


# Quick test function
def quick_test():
    """
    Quick test to see if everything works
    """
    agent = AppleFinancialAgent()
    results = agent.run_complete_analysis()
    
    print("\n\n📊 PROFITABILITY BRIDGE")
    print(results['profitability_bridge'].to_string(index=False))
    
    print("\n\n💰 CASH FLOW BRIDGE")
    print(results['cash_flow_bridge'].to_string(index=False))
    
    print("\n\n📦 WORKING CAPITAL ANALYSIS")
    print(results['working_capital'].to_string(index=False))
    
    print("\n\n" + results['management_summary'])
    
    return agent


if __name__ == "__main__":
    agent = quick_test()
