import os
from fpdf import FPDF

def generate_test_pdf(output_path, size='small'):
    """
    Generate a test PDF with financial content.
    
    Args:
        output_path: Path to save the PDF
        size: Size of the PDF ('small' or 'large')
    """
    pdf = FPDF()
    
    # Set up the PDF
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add a title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Financial Analysis Report - Test Document", ln=True, align='C')
    pdf.ln(10)
    
    # Add content based on size
    pdf.set_font("Arial", size=12)
    
    # Basic financial content
    pdf.multi_cell(0, 10, "Executive Summary:", 0, 'L')
    pdf.multi_cell(0, 10, "This report provides a comprehensive analysis of XYZ Corporation's financial performance for the fiscal year 2024. Our analysis covers key financial metrics, growth trends, risk assessment, and strategic recommendations.", 0, 'L')
    pdf.ln(5)
    
    pdf.multi_cell(0, 10, "Key Financial Metrics:", 0, 'L')
    pdf.multi_cell(0, 10, "- Revenue: $245.3 million (+12% YoY)\n- EBITDA: $78.2 million (+8% YoY)\n- Net Profit: $42.5 million (+5% YoY)\n- Debt-to-Equity Ratio: 0.82\n- Return on Assets (ROA): 14.3%\n- Return on Equity (ROE): 18.7%", 0, 'L')
    pdf.ln(5)
    
    # For large PDF, add more content to make it bigger
    if size == 'large':
        # Add detailed analysis sections to increase the size
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt="1. Revenue Analysis", ln=True, align='L')
        pdf.ln(5)
        pdf.set_font("Arial", size=12)
        
        # Detailed revenue analysis
        pdf.multi_cell(0, 10, "The company's revenue streams can be broken down as follows:", 0, 'L')
        pdf.multi_cell(0, 10, "- Product Line A: $125.8 million (51% of total revenue)\n- Product Line B: $78.2 million (32% of total revenue)\n- Product Line C: $41.3 million (17% of total revenue)", 0, 'L')
        pdf.ln(5)
        
        # Add quarterly breakdown
        pdf.multi_cell(0, 10, "Quarterly Revenue Breakdown (in millions):", 0, 'L')
        pdf.multi_cell(0, 10, "- Q1 2024: $58.2\n- Q2 2024: $62.7\n- Q3 2024: $59.4\n- Q4 2024: $65.0", 0, 'L')
        pdf.ln(5)
        
        # Add geographic distribution
        pdf.multi_cell(0, 10, "Geographic Revenue Distribution:", 0, 'L')
        pdf.multi_cell(0, 10, "- North America: 54%\n- Europe: 28%\n- Asia-Pacific: 13%\n- Rest of World: 5%", 0, 'L')
        pdf.ln(5)
        
        # Add pages for expense analysis
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt="2. Expense Analysis", ln=True, align='L')
        pdf.ln(5)
        pdf.set_font("Arial", size=12)
        
        # Detailed expense breakdown
        pdf.multi_cell(0, 10, "Operating Expenses Breakdown:", 0, 'L')
        pdf.multi_cell(0, 10, "- Cost of Goods Sold (COGS): $142.3 million (58% of revenue)\n- Research & Development: $24.5 million (10% of revenue)\n- Sales & Marketing: $31.2 million (13% of revenue)\n- General & Administrative: $18.4 million (7.5% of revenue)\n- Other Operating Expenses: $8.6 million (3.5% of revenue)", 0, 'L')
        pdf.ln(5)
        
        # Add quarterly expense trends
        pdf.multi_cell(0, 10, "Quarterly Expense Trends (in millions):", 0, 'L')
        pdf.multi_cell(0, 10, "- Q1 2024: $54.1\n- Q2 2024: $55.3\n- Q3 2024: $57.8\n- Q4 2024: $57.8", 0, 'L')
        pdf.ln(5)
        
        # Add many more pages with financial data to make the file larger
        for i in range(10):
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, txt=f"Additional Analysis Section {i+1}", ln=True, align='L')
            pdf.ln(5)
            pdf.set_font("Arial", size=12)
            
            # Add detailed text
            for j in range(20):
                pdf.multi_cell(0, 10, f"Paragraph {j+1}: This is detailed financial analysis text for section {i+1}. It contains information about financial metrics, market trends, competitive analysis, and strategic recommendations. The purpose of this text is to create a large PDF document that requires chunking for memory management.", 0, 'L')
            
            # Add some tables or metrics
            pdf.ln(5)
            pdf.multi_cell(0, 10, f"Key Metrics for Section {i+1}:", 0, 'L')
            pdf.multi_cell(0, 10, f"- Metric A: {42.5 + i*2.3}%\n- Metric B: {18.7 - i*0.6}%\n- Metric C: {64.2 + i*1.1}%\n- Metric D: {23.8 - i*0.8}%\n- Metric E: {52.1 + i*1.5}%", 0, 'L')
            pdf.ln(5)
    
    # Save the PDF
    pdf.output(output_path)
    
    # Get file size in MB
    size_in_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"Generated {output_path} ({size_in_mb:.2f} MB)")

if __name__ == "__main__":
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate a small test PDF
    small_pdf_path = os.path.join(output_dir, "small_financial_report.pdf")
    generate_test_pdf(small_pdf_path, size='small')
    
    # Generate a large test PDF
    large_pdf_path = os.path.join(output_dir, "large_financial_report.pdf")
    generate_test_pdf(large_pdf_path, size='large')
