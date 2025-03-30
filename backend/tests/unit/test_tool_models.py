import pytest
from pydantic import ValidationError
from models.tools import (
    ToolSchema,
    ChartGenerationTool,
    TableGenerationTool,
    DEFAULT_TOOLS
)


class TestToolSchema:
    """Test the base ToolSchema model"""
    
    def test_valid_schema(self):
        """Test creating a valid tool schema"""
        schema = ToolSchema(
            name="test_tool",
            description="A test tool",
            input_schema={
                "type": "object",
                "properties": {
                    "param1": {"type": "string"}
                },
                "required": ["param1"]
            }
        )
        
        assert schema.name == "test_tool"
        assert schema.description == "A test tool"
        assert "param1" in schema.input_schema["properties"]
        
    def test_missing_required_fields(self):
        """Test validation error when required fields are missing"""
        with pytest.raises(ValidationError):
            # Missing input_schema
            ToolSchema(
                name="test_tool",
                description="A test tool"
            )
            
    def test_convert_to_claude_format(self):
        """Test converting the tool schema to Claude API format"""
        schema = ToolSchema(
            name="test_tool",
            description="A test tool",
            input_schema={
                "type": "object",
                "properties": {
                    "param1": {"type": "string"}
                }
            }
        )
        
        # Convert to dict for Claude API
        claude_format = schema.model_dump()
        
        assert claude_format["name"] == "test_tool"
        assert claude_format["description"] == "A test tool"
        assert claude_format["input_schema"]["properties"]["param1"]["type"] == "string"


class TestChartGenerationTool:
    """Test the ChartGenerationTool model"""
    
    def test_default_values(self):
        """Test the default values for ChartGenerationTool"""
        tool = ChartGenerationTool()
        
        assert tool.name == "generate_graph_data"
        assert "Generate structured JSON data" in tool.description
        assert tool.input_schema["required"] == ["chartType", "config", "data"]
        
    def test_enum_values(self):
        """Test that chart type enum values are correctly defined"""
        tool = ChartGenerationTool()
        
        # Check if the enum for chart types is correctly defined
        chart_types = tool.input_schema["properties"]["chartType"]["enum"]
        assert "bar" in chart_types
        assert "line" in chart_types
        assert "pie" in chart_types
        assert "multiBar" in chart_types
        assert "area" in chart_types
        assert "stackedArea" in chart_types
        
    def test_custom_values(self):
        """Test creating tool with custom values"""
        tool = ChartGenerationTool(
            name="custom_chart_tool",
            description="Custom chart tool"
        )
        
        assert tool.name == "custom_chart_tool"
        assert tool.description == "Custom chart tool"
        # Input schema should still be preserved
        assert "chartType" in tool.input_schema["properties"]


class TestTableGenerationTool:
    """Test the TableGenerationTool model"""
    
    def test_default_values(self):
        """Test the default values for TableGenerationTool"""
        tool = TableGenerationTool()
        
        assert tool.name == "generate_table_data"
        assert "Generate structured JSON data for creating financial data tables" in tool.description
        assert tool.input_schema["required"] == ["tableType", "config", "data"]
        
    def test_enum_values(self):
        """Test that table type enum values are correctly defined"""
        tool = TableGenerationTool()
        
        # Check if the enum for table types is correctly defined
        table_types = tool.input_schema["properties"]["tableType"]["enum"]
        assert "simple" in table_types
        assert "matrix" in table_types
        assert "comparison" in table_types


class TestDefaultTools:
    """Test the DEFAULT_TOOLS configuration"""
    
    def test_default_tools_list(self):
        """Test that DEFAULT_TOOLS contains the expected tools"""
        assert len(DEFAULT_TOOLS) == 2
        
        # Check that the tools are of the correct types
        tool_types = [type(tool) for tool in DEFAULT_TOOLS]
        assert ChartGenerationTool in tool_types
        assert TableGenerationTool in tool_types
        
        # Check the names of the tools
        tool_names = [tool.name for tool in DEFAULT_TOOLS]
        assert "generate_graph_data" in tool_names
        assert "generate_table_data" in tool_names 