from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AnalysisRequest(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol (e.g., AAPL, TSLA)")
    company_name: Optional[str] = Field(None, description="Company name (optional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "company_name": "Apple Inc."
            }
        }

class AgentStatus(BaseModel):
    agent_name: str
    status: str
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ResearchData(BaseModel):
    summary: Optional[str] = None
    
    class Config:
        extra = "allow"  


class AnalysisData(BaseModel):
    summary: Optional[str] = None
    
    class Config:
        extra = "allow"  


class ReportData(BaseModel):
    report_text: str


class AnalysisResponse(BaseModel):
    ticker: str
    company_name: Optional[str] = None
    status: str
    research_data: Optional[ResearchData] = None
    analysis_data: Optional[AnalysisData] = None
    report_data: Optional[ReportData] = None
    agent_statuses: List[AgentStatus] = []
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "company_name": "Apple Inc.",
                "status": "completed",
                "timestamp": "2026-01-30T10:00:00"
            }
        }