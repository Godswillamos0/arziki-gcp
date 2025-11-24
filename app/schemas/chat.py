from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ChatMessageDTO(BaseModel):
    message: str
    timestamp: Optional[datetime]
    
    
class ChatHistoryDTO(BaseModel):
    user_id: str
    messages: List[ChatMessageDTO] = Field(default_factory=list)
    
    class Config:
        orm_mode = True
        
        
class GenerateAnalyticsReportDTO(BaseModel):
    report_type: str = Field(..., description="Type of analytics report to generate (e.g., 'sales', 'inventory')")
    timeframe: str = Field(..., description="Timeframe for the report (e.g., 'monthly', 'quarterly', 'yearly')")
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_type": "sales",
                "timeframe": "monthly"
            }
        }
        
        
class BussinessDataDTO(BaseModel):
    """
    DTO for business data, including metadata and product information.
    """
    business_name: str
    metadata: dict
    products: List[dict]

    model_config = {
        "json_schema_extra": {
            "example": {
                "business_name": "My Business",
                "metadata": {
                    "industry": "Retail",
                    "size": "50-100 employees",
                    "location": "New York, USA"
                },
                "products": [
                    {
                        "name": "Product A",
                        "category": "Electronics",
                        "price": 199.99,
                        "stock": 150
                    },
                    {
                        "name": "Product B",
                        "category": "Apparel",
                        "price": 49.99,
                        "stock": 300
                    }
                ]
            }
        }
    }
        
         
