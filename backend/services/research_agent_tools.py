from langchain.tools import tool
from typing import Dict, Any, List
from backend.services.finnhub import finnhub_client
import json


@tool
def get_company_news(ticker: str) -> str:
    """
    Fetch recent company news and updates for a given stock ticker.
    
    Args:
        ticker: Stock ticker symbol (e.g., AAPL, TSLA)
        
    Returns:
        JSON string containing recent news articles
    """
    try:
        news = finnhub_client.get_company_news(ticker, days=7)
        
        if not news:
            return json.dumps({"error": "No news found", "news": []})
        
        formatted_news = []
        for article in news[:10]:
            formatted_news.append({
                "headline": article.get("headline", ""),
                "summary": article.get("summary", ""),
                "source": article.get("source", ""),
                "url": article.get("url", ""),
                "datetime": article.get("datetime", "")
            })
        
        return json.dumps({"news": formatted_news}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "news": []})


@tool
def get_analyst_recommendations(ticker: str) -> str:
    """
    Fetch analyst recommendations and ratings for a stock.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        JSON string containing analyst recommendations
    """
    try:
        recommendations = finnhub_client.get_recommendation_trends(ticker)
        
        if not recommendations:
            return json.dumps({"error": "No recommendations found", "recommendations": []})
        
        return json.dumps({"recommendations": recommendations}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "recommendations": []})


@tool
def get_price_target_consensus(ticker: str) -> str:
    """
    Fetch price target consensus from analysts.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        JSON string containing price target information
    """
    try:
        price_target = finnhub_client.get_price_target(ticker)
        
        if not price_target:
            return json.dumps({"error": "No price target data found"})
        
        return json.dumps(price_target, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def get_company_profile(ticker: str) -> str:
    """
    Fetch company profile and basic information.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        JSON string containing company profile
    """
    try:
        profile = finnhub_client.get_company_profile(ticker)
        
        if not profile:
            return json.dumps({"error": "No company profile found"})
        company_info = {
            "name": profile.get("name", ""),
            "ticker": profile.get("ticker", ""),
            "industry": profile.get("finnhubIndustry", ""),
            "marketCap": profile.get("marketCapitalization", 0),
            "country": profile.get("country", ""),
            "currency": profile.get("currency", ""),
            "exchange": profile.get("exchange", ""),
            "ipo": profile.get("ipo", ""),
            "logo": profile.get("logo", ""),
            "weburl": profile.get("weburl", "")
        }
        
        return json.dumps(company_info, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


research_tools = [
    get_company_news,
    get_analyst_recommendations,
    get_price_target_consensus,
    get_company_profile
]