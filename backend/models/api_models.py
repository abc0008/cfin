from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal

class RetryExtractionRequest(BaseModel):
    """
    Request model for retrying document extraction
    """
    extraction_type: Literal["structured_financial_data", "text_only", "tables_only"] = Field(
        "structured_financial_data", 
        description="Type of extraction to perform"
    )
    options: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional options for extraction"
    ) 