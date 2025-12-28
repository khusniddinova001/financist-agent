"""
Report Generator for Apple Financial Analysis
Exports analysis to Excel, PDF, and PowerPoint formats
"""

import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


class ReportGenerator:
    """
    Generates professional reports from financial analysis
    """
    
    def __init__(self, agent):
        self.agent = agent
        self.results = agent.analysis_results
        
    def create_excel_report(self, filename="Apple_Financial_Analysis.xlsx"):
        """
        Create comprehensive Excel workbook with all analyses
        """
        print(f"\n📑 Creating Excel report: {filename}")
        
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        workbook = writer.book
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })
        
        currency_format = workbook.add_format({
            'num_format': '$#,##0',
            'border': 1
        })
        
        percent_format = workbook.add_format({
            'num_format': '0.0%',
            'border': 1
        })
        
        number_format = workbook.add_format({
            'num_format': '#,##0.0',
            'border': 1
        })
        
        # Sheet 1: Executive Summary
        summary_df = pd.DataFrame({
            'Section': ['Report Information', '', 'Company', 'Analysis Date', 'Fiscal Year', 'Report Type'],
            'Details': ['Apple Inc. Financial Analysis', '', 'Apple Inc. (AAPL)', 
                       datetime.now().strftime('%Y-%m-%d'), 
                       self.agent.financial_data['income_statement'].columns[0].strftime('%Y'),
                       'Automated AI Analysis']
        })
        
        summary_df.to_excel(writer, sheet_name='Executive Summary', index=False)
        worksheet = writer.sheets['Executive Summary']
        
        # Add management summary
        row_offset = 8
        worksheet.write(row_offset, 0, 'MANAGEMENT SUMMARY', header_format)
        
        summary_text = self.results['management_summary'].split('\n')
        for i, line in enumerate(summary_text):
            worksheet.write(row_offset + i + 1, 0, line)
        
        # Sheet 2: Profitability Bridge
        prof_bridge = self.results['profitability_bridge']
        prof_bridge.to_excel(writer, sheet_name='Profitability Bridge', index=False)
        
        worksheet = writer.sheets['Profitability Bridge']
        for col_num, value in enumerate(prof_bridge.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Format currency columns
        for row in range(1, len(prof_bridge) + 1):
            worksheet.write(row, 1, prof_bridge.iloc[row-1, 1], currency_format)
        
        # Sheet 3: Cash Flow Bridge
        cf_bridge = self.results['cash_flow_bridge']
        cf_bridge.to_excel(writer, sheet_name='Cash Flow Bridge', index=False)
        
        worksheet = writer.sheets['Cash Flow Bridge']
        for col_num, value in enumerate(cf_bridge.columns.values):
            worksheet.write(0, col_num, value, header_format)
            
        for row in range(1, len(cf_bridge) + 1):
            worksheet.write(row, 1, cf_bridge.iloc[row-1, 1], currency_format)
        
        # Sheet 4: Working Capital
        wc_analysis = self.results['working_capital']
        wc_analysis.to_excel(writer, sheet_name='Working Capital', index=False)
        
        worksheet = writer.sheets['Working Capital']
        for col_num, value in enumerate(wc_analysis.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Sheet 5: Raw Data
        income_stmt = self.agent.financial_data['income_statement']
        income_stmt.to_excel(writer, sheet_name='Income Statement')
        
        balance_sheet = self.agent.financial_data['balance_sheet']
        balance_sheet.to_excel(writer, sheet_name='Balance Sheet')
        
        cash_flow = self.agent.financial_data['cash_flow']
        cash_flow.to_excel(writer, sheet_name='Cash Flow Statement')
        
        writer.close()
        print(f"✅ Excel report saved: {filename}")
        
        return filename
    
    def create_visualizations(self):
        """
        Create charts for the analysis
        """
        print("\n📊 Creating visualizations...")
        
        charts = {}
        
        # Chart 1: Profitability Bridge Waterfall
        prof_bridge = self.results['profitability_bridge']
        bridge_components = prof_bridge[prof_bridge['Component'].str.len() > 0].head(5)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        components = bridge_components['Component'].values
        amounts = bridge_components['Amount ($M)'].values
        
        # Create waterfall chart
        x = range(len(components))
        colors = ['green' if i in [0, 4] else 'blue' if amt > 0 else 'red' 
                 for i, amt in enumerate(amounts)]
        
        ax.bar(x, amounts, color=colors, alpha=0.7, edgecolor='black')
        ax.set_xticks(x)
        ax.set_xticklabels(components, rotation=45, ha='right')
        ax.set_ylabel('Amount ($M)', fontsize=12, fontweight='bold')
        ax.set_title('Profitability Bridge Analysis', fontsize=14, fontweight='bold')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for i, (comp, amt) in enumerate(zip(components, amounts)):
            ax.text(i, amt, f'${amt:,.0f}M', ha='center', 
                   va='bottom' if amt > 0 else 'top', fontweight='bold')
        
        plt.tight_layout()
        charts['profitability_waterfall'] = fig
        
        # Chart 2: Cash Flow Bridge
        fig, ax = plt.subplots(figsize=(12, 6))
        
        cf_bridge = self.results['cash_flow_bridge']
        cf_components = cf_bridge[cf_bridge['Component'].str.len() > 0].head(9)
        
        components = cf_components['Component'].values
        amounts = cf_components['Amount ($M)'].values
        
        colors = ['green' if 'Net Income' in comp or 'Free Cash Flow' in comp or 'Operating' in comp
                 else 'blue' if amt > 0 else 'red' 
                 for comp, amt in zip(components, amounts)]
        
        ax.barh(components, amounts, color=colors, alpha=0.7, edgecolor='black')
        ax.set_xlabel('Amount ($M)', fontsize=12, fontweight='bold')
        ax.set_title('Cash Flow Bridge: Net Income → Free Cash Flow', fontsize=14, fontweight='bold')
        ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        ax.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, (comp, amt) in enumerate(zip(components, amounts)):
            ax.text(amt, i, f' ${amt:,.0f}M', ha='left' if amt > 0 else 'right', 
                   va='center', fontweight='bold')
        
        plt.tight_layout()
        charts['cashflow_bridge'] = fig
        
        # Chart 3: Working Capital Trends
        fig, ax = plt.subplots(figsize=(12, 6))
        
        wc_analysis = self.results['working_capital']
        wc_metrics = wc_analysis[wc_analysis['Metric'].isin(['Days Sales Outstanding (DSO)',
                                                               'Days Inventory Outstanding (DIO)',
                                                               'Days Payable Outstanding (DPO)'])]
        
        metrics = wc_metrics['Metric'].values
        current = wc_metrics['Current Year'].values
        prior = wc_metrics['Prior Year'].values
        
        x = range(len(metrics))
        width = 0.35
        
        ax.bar([i - width/2 for i in x], prior, width, label='Prior Year', 
               color='lightblue', edgecolor='black')
        ax.bar([i + width/2 for i in x], current, width, label='Current Year', 
               color='darkblue', edgecolor='black')
        
        ax.set_ylabel('Days', fontsize=12, fontweight='bold')
        ax.set_title('Working Capital Efficiency Metrics', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(['DSO', 'DIO', 'DPO'], fontsize=11)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for i in x:
            ax.text(i - width/2, prior[i], f'{prior[i]:.0f}', ha='center', 
                   va='bottom', fontweight='bold', fontsize=9)
            ax.text(i + width/2, current[i], f'{current[i]:.0f}', ha='center', 
                   va='bottom', fontweight='bold', fontsize=9)
        
        plt.tight_layout()
        charts['working_capital'] = fig
        
        print("✅ Visualizations created")
        return charts
    
    def save_charts(self, charts, prefix="Apple"):
        """
        Save all charts as PNG files
        """
        print("\n💾 Saving charts...")
        
        saved_files = []
        for name, fig in charts.items():
            filename = f"{prefix}_{name}.png"
            fig.savefig(filename, dpi=300, bbox_inches='tight')
            saved_files.append(filename)
            print(f"   Saved: {filename}")
        
        return saved_files
    
    def create_summary_report(self, filename="Apple_Analysis_Summary.txt"):
        """
        Create a text summary report
        """
        print(f"\n📄 Creating summary report: {filename}")
        
        with open(filename, 'w') as f:
            f.write(self.results['management_summary'])
            
            f.write("\n\n" + "="*60 + "\n")
            f.write("DETAILED ANALYSIS TABLES\n")
            f.write("="*60 + "\n\n")
            
            f.write("PROFITABILITY BRIDGE\n")
            f.write("-"*60 + "\n")
            f.write(self.results['profitability_bridge'].to_string(index=False))
            
            f.write("\n\n")
            f.write("CASH FLOW BRIDGE\n")
            f.write("-"*60 + "\n")
            f.write(self.results['cash_flow_bridge'].to_string(index=False))
            
            f.write("\n\n")
            f.write("WORKING CAPITAL ANALYSIS\n")
            f.write("-"*60 + "\n")
            f.write(self.results['working_capital'].to_string(index=False))
        
        print(f"✅ Summary report saved: {filename}")
        return filename


def generate_all_reports(agent):
    """
    Generate all report formats
    """
    print("\n" + "="*60)
    print("📑 GENERATING REPORTS")
    print("="*60)
    
    generator = ReportGenerator(agent)
    
    # Create Excel report
    excel_file = generator.create_excel_report()
    
    # Create visualizations
    charts = generator.create_visualizations()
    chart_files = generator.save_charts(charts)
    
    # Create text summary
    summary_file = generator.create_summary_report()
    
    print("\n" + "="*60)
    print("✅ ALL REPORTS GENERATED SUCCESSFULLY")
    print("="*60)
    print(f"\nGenerated files:")
    print(f"  📊 {excel_file}")
    print(f"  📄 {summary_file}")
    for chart in chart_files:
        print(f"  📈 {chart}")
    
    return {
        'excel': excel_file,
        'summary': summary_file,
        'charts': chart_files
    }


if __name__ == "__main__":
    from apple_financial_agent import AppleFinancialAgent
    
    # Run analysis
    agent = AppleFinancialAgent()
    agent.run_complete_analysis()
    
    # Generate reports
    reports = generate_all_reports(agent)
