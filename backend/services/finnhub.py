import finnhub
from dotenv import load_dotenv
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

load_dotenv()


class FinnhubClient:
    def __init__(self):
        api_key = os.getenv("FINNHUB_API_KEY")
        if not api_key:
            raise ValueError("FINNHUB_API_KEY not found in environment variables")
        
        self.client = finnhub.Client(api_key=api_key)
    
    def get_company_profile(self, ticker: str) -> Dict[str, Any]:
        try:
            profile = self.client.company_profile2(symbol=ticker)
            return profile
        except Exception as e:
            print(f"Error fetching company profile: {e}")
            return {}
    
    def get_quote(self, ticker: str) -> Dict[str, Any]:
        try:
            quote = self.client.quote(ticker)
            return quote
        except Exception as e:
            print(f"Error fetching quote: {e}")
            return {}
    
    def get_company_news(self, ticker: str, days: int = 7) -> List[Dict[str, Any]]:
        try:
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            
            news = self.client.company_news(
                ticker,
                _from=from_date.strftime("%Y-%m-%d"),
                to=to_date.strftime("%Y-%m-%d")
            )
            return news[:10]  
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []
    
    def get_basic_financials(self, ticker: str) -> Dict[str, Any]:
        try:
            financials = self.client.company_basic_financials(ticker, 'all')
            return financials
        except Exception as e:
            print(f"Error fetching financials: {e}")
            return {}
    
    def get_recommendation_trends(self, ticker: str) -> List[Dict[str, Any]]:
        try:
            recommendations = self.client.recommendation_trends(ticker)
            return recommendations
        except Exception as e:
            print(f"Error fetching recommendations: {e}")
            return []
    
    def get_price_target(self, ticker: str) -> Dict[str, Any]:
        try:
            target = self.client.price_target(ticker)
            return target
        except Exception as e:
            print(f"Error fetching price target: {e}")
            return {}

finnhub_client = FinnhubClient()