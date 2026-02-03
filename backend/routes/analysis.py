from fastapi import APIRouter, HTTPException
from backend.schemas.analysis import AnalysisRequest, AnalysisResponse
from backend.interactors.analysis import AnalysisInteractor

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_stock(request: AnalysisRequest):
    interactor = AnalysisInteractor()
    
    if not interactor.validate_ticker(request.ticker):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid ticker symbol: {request.ticker}"
        )
    
    try:
        response = interactor.execute_analysis(request)
        
        if response.status == "error":
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {response.error}"
            )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis error: {str(e)}"
        )


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Financial Analysis API"
    }