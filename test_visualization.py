#!/usr/bin/env python3
"""
Test script for tool-based visualizations.
This script generates sample chart and table data in the tool format
and serves it through a simple web server for testing.
"""

import json
import http.server
import socketserver
import datetime
from uuid import uuid4
from typing import Dict, List, Any, Optional, Union

# Sample visualization data
def generate_sample_chart() -> Dict[str, Any]:
    """Generate a sample bar chart in the tool format."""
    return {
        "chartType": "bar",
        "config": {
            "title": "Revenue by Quarter",
            "description": "Quarterly revenue for 2022-2023",
            "xAxisKey": "quarter"
        },
        "series": [
            {
                "name": "2022",
                "data": [
                    {"x": "Q1", "y": 1250000, "category": "Q1"},
                    {"x": "Q2", "y": 1420000, "category": "Q2"},
                    {"x": "Q3", "y": 1550000, "category": "Q3"},
                    {"x": "Q4", "y": 1820000, "category": "Q4"}
                ],
                "color": "#4F46E5"
            },
            {
                "name": "2023",
                "data": [
                    {"x": "Q1", "y": 1350000, "category": "Q1"},
                    {"x": "Q2", "y": 1520000, "category": "Q2"},
                    {"x": "Q3", "y": 1750000, "category": "Q3"},
                    {"x": "Q4", "y": 1950000, "category": "Q4"}
                ],
                "color": "#EF4444"
            }
        ],
        "xAxisTitle": "Quarter",
        "yAxisTitle": "Revenue ($)",
        "legendPosition": "top"
    }

def generate_sample_line_chart() -> Dict[str, Any]:
    """Generate a sample line chart in the tool format."""
    return {
        "chartType": "line",
        "config": {
            "title": "Monthly Expenses",
            "description": "Monthly expenses for 2023",
            "xAxisKey": "month"
        },
        "series": [
            {
                "name": "Operating Expenses",
                "data": [
                    {"x": "Jan", "y": 450000, "category": "Jan"},
                    {"x": "Feb", "y": 420000, "category": "Feb"},
                    {"x": "Mar", "y": 480000, "category": "Mar"},
                    {"x": "Apr", "y": 460000, "category": "Apr"},
                    {"x": "May", "y": 500000, "category": "May"},
                    {"x": "Jun", "y": 520000, "category": "Jun"}
                ],
                "color": "#10B981"
            },
            {
                "name": "Marketing Expenses",
                "data": [
                    {"x": "Jan", "y": 150000, "category": "Jan"},
                    {"x": "Feb", "y": 180000, "category": "Feb"},
                    {"x": "Mar", "y": 200000, "category": "Mar"},
                    {"x": "Apr", "y": 190000, "category": "Apr"},
                    {"x": "May", "y": 220000, "category": "May"},
                    {"x": "Jun", "y": 250000, "category": "Jun"}
                ],
                "color": "#F59E0B"
            }
        ],
        "xAxisTitle": "Month",
        "yAxisTitle": "Expenses ($)",
        "legendPosition": "bottom"
    }

def generate_sample_table() -> Dict[str, Any]:
    """Generate a sample table in the tool format."""
    return {
        "tableType": "comparison",
        "config": {
            "title": "Financial Metrics Comparison",
            "description": "Year-over-Year comparison of key financial metrics",
            "columns": [
                {"key": "metric", "label": "Metric", "format": "text"},
                {"key": "2022", "label": "2022", "format": "currency"},
                {"key": "2023", "label": "2023", "format": "currency"},
                {"key": "change", "label": "Change", "format": "currency"},
                {"key": "percentChange", "label": "% Change", "format": "percentage"}
            ]
        },
        "data": [
            {
                "metric": "Revenue",
                "2022": 6040000,
                "2023": 6570000,
                "change": 530000,
                "percentChange": 8.77
            },
            {
                "metric": "Gross Profit",
                "2022": 3624000,
                "2023": 4072000,
                "change": 448000,
                "percentChange": 12.36
            },
            {
                "metric": "Operating Income",
                "2022": 1812000,
                "2023": 2190000,
                "change": 378000,
                "percentChange": 20.86
            },
            {
                "metric": "Net Income",
                "2022": 1208000,
                "2023": 1478000,
                "change": 270000,
                "percentChange": 22.35
            }
        ]
    }

def generate_analysis_result() -> Dict[str, Any]:
    """Generate a complete analysis result with tool-based visualization data."""
    return {
        "id": str(uuid4()),
        "documentIds": ["doc-12345"],
        "analysisType": "comprehensive",
        "timestamp": datetime.datetime.now().isoformat(),
        "analysisText": """
Financial Analysis:

The financial data indicates strong performance for 2023 compared to 2022. 
Revenue increased by 8.77% from $6.04 million to $6.57 million. 
More notably, profitability metrics showed even stronger improvement, with:
- Gross profit up 12.36% to $4.07 million
- Operating income up 20.86% to $2.19 million
- Net income up 22.35% to $1.48 million

The operating expense and marketing expense patterns show consistent investment 
with a gradual increase throughout the first half of 2023.

Quarterly revenue analysis shows steady growth across all quarters year-over-year, 
with the strongest performance in Q3 and Q4.
        """.strip(),
        "visualizationData": {
            "charts": [
                generate_sample_chart(),
                generate_sample_line_chart()
            ],
            "tables": [
                generate_sample_table()
            ]
        },
        "metrics": [
            {
                "name": "Revenue",
                "value": 6570000,
                "previousValue": 6040000,
                "percentChange": 8.77,
                "unit": "$",
                "category": "Income Statement",
                "trend": "up"
            },
            {
                "name": "Net Income",
                "value": 1478000,
                "previousValue": 1208000,
                "percentChange": 22.35,
                "unit": "$",
                "category": "Income Statement",
                "trend": "up"
            },
            {
                "name": "Gross Margin",
                "value": 62.0,
                "previousValue": 60.0,
                "percentChange": 3.33,
                "unit": "%",
                "category": "Profitability",
                "trend": "up"
            }
        ]
    }

class TestHandler(http.server.SimpleHTTPRequestHandler):
    """
    Custom HTTP request handler for serving sample API responses.
    """
    
    def do_GET(self):
        """Handle GET requests with sample data."""
        if self.path == "/api/analysis/test-viz":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")  # Enable CORS
            self.end_headers()
            
            analysis_result = generate_analysis_result()
            self.wfile.write(json.dumps(analysis_result).encode())
        else:
            # Default behavior for other paths
            super().do_GET()
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

def main():
    """Start the test server."""
    port = 8000
    handler = TestHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving test visualization data at http://localhost:{port}/api/analysis/test-viz")
        print("Press Ctrl+C to stop the server")
        httpd.serve_forever()

if __name__ == "__main__":
    main() 