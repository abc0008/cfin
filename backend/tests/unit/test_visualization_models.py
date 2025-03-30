import pytest
from pydantic import ValidationError
from models.visualization import (
    MetricConfig,
    ChartConfig,
    ChartData,
    TableColumn,
    TableConfig,
    TableData,
    VisualizationData
)


class TestMetricConfig:
    """Test the MetricConfig model"""
    
    def test_valid_metric_config(self):
        """Test creating a valid metric config"""
        config = MetricConfig(
            label="Revenue"
        )
        
        assert config.label == "Revenue"
        assert config.color is None
        
    def test_with_color(self):
        """Test creating a config with color"""
        config = MetricConfig(
            label="Revenue",
            color="#FF0000"
        )
        
        assert config.label == "Revenue"
        assert config.color == "#FF0000"
        
    def test_missing_required_field(self):
        """Test validation error when label is missing"""
        with pytest.raises(ValidationError):
            MetricConfig()


class TestChartConfig:
    """Test the ChartConfig model"""
    
    def test_valid_chart_config(self):
        """Test creating a valid chart config"""
        config = ChartConfig(
            title="Revenue Over Time",
            description="Chart showing revenue trends"
        )
        
        assert config.title == "Revenue Over Time"
        assert config.description == "Chart showing revenue trends"
        assert config.trend is None
        assert config.footer is None
        assert config.totalLabel is None
        assert config.xAxisKey is None
        
    def test_with_optional_fields(self):
        """Test creating a config with optional fields"""
        config = ChartConfig(
            title="Revenue Over Time",
            description="Chart showing revenue trends",
            trend={"direction": "up", "percent": 15},
            footer="Data source: Financial reports",
            totalLabel="Total Revenue",
            xAxisKey="year"
        )
        
        assert config.title == "Revenue Over Time"
        assert config.description == "Chart showing revenue trends"
        assert config.trend == {"direction": "up", "percent": 15}
        assert config.footer == "Data source: Financial reports"
        assert config.totalLabel == "Total Revenue"
        assert config.xAxisKey == "year"
        
    def test_missing_required_fields(self):
        """Test validation error when required fields are missing"""
        with pytest.raises(ValidationError):
            ChartConfig(
                title="Revenue Over Time"
                # Missing description
            )


class TestChartData:
    """Test the ChartData model"""
    
    def test_valid_chart_data(self):
        """Test creating valid chart data"""
        data = ChartData(
            chartType="bar",
            config=ChartConfig(
                title="Revenue by Quarter",
                description="Chart showing quarterly revenue"
            ),
            data=[
                {"quarter": "Q1", "value": 100000},
                {"quarter": "Q2", "value": 120000}
            ],
            chartConfig={
                "value": MetricConfig(
                    label="Revenue",
                    color="#0000FF"
                )
            }
        )
        
        assert data.chartType == "bar"
        assert data.config.title == "Revenue by Quarter"
        assert len(data.data) == 2
        assert data.data[0]["quarter"] == "Q1"
        assert data.chartConfig["value"].label == "Revenue"
        
    def test_invalid_chart_type(self):
        """Test validation error when chart type is invalid"""
        with pytest.raises(ValidationError):
            ChartData(
                chartType="invalid_type",  # Not in Literal allowlist
                config=ChartConfig(
                    title="Revenue by Quarter",
                    description="Chart showing quarterly revenue"
                ),
                data=[],
                chartConfig={}
            )
            
    def test_model_to_dict(self):
        """Test converting the model to a dictionary"""
        data = ChartData(
            chartType="bar",
            config=ChartConfig(
                title="Revenue by Quarter",
                description="Chart showing quarterly revenue"
            ),
            data=[
                {"quarter": "Q1", "value": 100000},
                {"quarter": "Q2", "value": 120000}
            ],
            chartConfig={
                "value": MetricConfig(
                    label="Revenue",
                    color="#0000FF"
                )
            }
        )
        
        # Convert to dict for serialization
        data_dict = data.model_dump()
        
        assert data_dict["chartType"] == "bar"
        assert data_dict["config"]["title"] == "Revenue by Quarter"
        assert len(data_dict["data"]) == 2
        assert data_dict["chartConfig"]["value"]["label"] == "Revenue"


class TestTableData:
    """Test the TableData model"""
    
    def test_valid_table_data(self):
        """Test creating valid table data"""
        data = TableData(
            tableType="simple",
            config=TableConfig(
                title="Financial Metrics",
                description="Key financial metrics",
                columns=[
                    TableColumn(key="metric", label="Metric"),
                    TableColumn(key="value", label="Value", format="currency")
                ]
            ),
            data=[
                {"metric": "Revenue", "value": 1000000},
                {"metric": "Expenses", "value": 750000}
            ]
        )
        
        assert data.tableType == "simple"
        assert data.config.title == "Financial Metrics"
        assert len(data.config.columns) == 2
        assert data.config.columns[1].format == "currency"
        assert len(data.data) == 2
        assert data.data[0]["metric"] == "Revenue"
        
    def test_invalid_table_type(self):
        """Test validation error when table type is invalid"""
        with pytest.raises(ValidationError):
            TableData(
                tableType="invalid_type",  # Not in Literal allowlist
                config=TableConfig(
                    title="Financial Metrics",
                    description="Key financial metrics",
                    columns=[
                        TableColumn(key="metric", label="Metric")
                    ]
                ),
                data=[]
            )


class TestVisualizationData:
    """Test the VisualizationData model"""
    
    def test_empty_visualization_data(self):
        """Test creating empty visualization data"""
        data = VisualizationData()
        
        assert len(data.charts) == 0
        assert len(data.tables) == 0
        assert data.monetaryValues == {}
        assert data.percentages == {}
        assert data.keywordFrequency == {}
        
    def test_with_charts_and_tables(self):
        """Test creating visualization data with charts and tables"""
        chart = ChartData(
            chartType="bar",
            config=ChartConfig(
                title="Revenue by Quarter",
                description="Chart showing quarterly revenue"
            ),
            data=[
                {"quarter": "Q1", "value": 100000}
            ],
            chartConfig={
                "value": MetricConfig(label="Revenue")
            }
        )
        
        table = TableData(
            tableType="simple",
            config=TableConfig(
                title="Financial Metrics",
                description="Key financial metrics",
                columns=[
                    TableColumn(key="metric", label="Metric")
                ]
            ),
            data=[
                {"metric": "Revenue", "value": 1000000}
            ]
        )
        
        data = VisualizationData(
            charts=[chart],
            tables=[table],
            monetaryValues={"type": "bar", "data": [{"label": "Revenue", "value": 1000000}]},
            percentages={"type": "bar", "data": [{"label": "Profit Margin", "value": 25}]}
        )
        
        assert len(data.charts) == 1
        assert len(data.tables) == 1
        assert data.charts[0].chartType == "bar"
        assert data.tables[0].tableType == "simple"
        assert data.monetaryValues["type"] == "bar"
        assert data.percentages["data"][0]["label"] == "Profit Margin" 