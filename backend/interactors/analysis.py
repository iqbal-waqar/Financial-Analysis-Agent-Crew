from backend.schemas.analysis import AnalysisRequest, AnalysisResponse, AgentStatus
from backend.services.graph import run_financial_analysis
from datetime import datetime


class AnalysisInteractor:

    def execute_analysis(self, request: AnalysisRequest) -> AnalysisResponse:

        try:
            result = run_financial_analysis(
                ticker=request.ticker,
                company_name=request.company_name
            )

            research_data = result.get("research_data", {})
            analysis_data = result.get("analysis_data", {})
            report_data = result.get("report_data", {})

            agent_statuses = [
                AgentStatus(
                    agent_name="Market Researcher",
                    status="completed" if research_data else "failed",
                    message="Research completed successfully" if research_data else "Research failed",
                    timestamp=datetime.now()
                ),
                AgentStatus(
                    agent_name="Data Analyst",
                    status="completed" if analysis_data else "failed",
                    message="Analysis completed successfully" if analysis_data else "Analysis failed",
                    timestamp=datetime.now()
                ),
                AgentStatus(
                    agent_name="Report Writer",
                    status="completed" if report_data else "failed",
                    message="Report completed successfully" if report_data else "Report failed",
                    timestamp=datetime.now()
                )
            ]

            response = AnalysisResponse(
                ticker=request.ticker.upper(),
                company_name=request.company_name or request.ticker.upper(),
                status=result.get("status", "completed"),
                research_data=research_data if research_data else None,
                analysis_data=analysis_data if analysis_data else None,
                report_data=report_data if report_data else None,
                agent_statuses=agent_statuses,
                error=result.get("error"),
                timestamp=datetime.now()
            )
            
            return response
            
        except Exception as e:

            return AnalysisResponse(
                ticker=request.ticker.upper(),
                company_name=request.company_name,
                status="error",
                error=str(e),
                agent_statuses=[],
                timestamp=datetime.now()
            )
    
    
    def validate_ticker(self, ticker: str) -> bool:
        if not ticker:
            return False
        
        ticker = ticker.strip().upper()
        if len(ticker) < 1 or len(ticker) > 5:
            return False
        
        if not ticker.isalpha():
            return False
        
        return True