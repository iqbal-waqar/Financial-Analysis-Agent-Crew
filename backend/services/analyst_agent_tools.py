from langchain.tools import tool
from typing import Dict, Any
from backend.services.finnhub import finnhub_client
import json
import yfinance as yf
import pandas as pd




@tool
def get_stock_quote(ticker: str) -> str:
    """
    Fetch real-time stock quote data including current price, change, volume, etc.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        JSON string containing quote data
    """
    try:
        quote = finnhub_client.get_quote(ticker)
        
        if not quote:
            return json.dumps({"error": "No quote data found"})
        
        quote_data = {
            "current_price": quote.get("c", 0),
            "change": quote.get("d", 0),
            "percent_change": quote.get("dp", 0),
            "high": quote.get("h", 0),
            "low": quote.get("l", 0),
            "open": quote.get("o", 0),
            "previous_close": quote.get("pc", 0),
            "timestamp": quote.get("t", 0)
        }
        
        return json.dumps(quote_data, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def get_financial_metrics(ticker: str) -> str:
    """
    Fetch comprehensive financial metrics and KPIs for a stock.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        JSON string containing financial metrics
    """
    try:
        financials = finnhub_client.get_basic_financials(ticker)
        
        if not financials or "metric" not in financials:
            return json.dumps({"error": "No financial metrics found"})
        
        metrics = financials.get("metric", {})
        
        key_metrics = {
            "pe_ratio": metrics.get("peNormalizedAnnual", 0),
            "eps": metrics.get("epsBasicExclExtraItemsTTM", 0),
            "market_cap": metrics.get("marketCapitalization", 0),
            "week_52_high": metrics.get("52WeekHigh", 0),
            "week_52_low": metrics.get("52WeekLow", 0),
            "beta": metrics.get("beta", 0),
            "volume_avg_10d": metrics.get("10DayAverageTradingVolume", 0),
            "dividend_yield": metrics.get("dividendYieldIndicatedAnnual", 0),
            "profit_margin": metrics.get("netProfitMarginTTM", 0),
            "roe": metrics.get("roeTTM", 0),
            "roa": metrics.get("roaTTM", 0),
            "debt_to_equity": metrics.get("totalDebt/totalEquityQuarterly", 0),
            "current_ratio": metrics.get("currentRatioQuarterly", 0),
            "revenue_per_share": metrics.get("revenuePerShareTTM", 0),
            "book_value_per_share": metrics.get("bookValuePerShareQuarterly", 0)
        }
        
        return json.dumps(key_metrics, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def get_historical_price_data(ticker: str, period: str = "6mo") -> str:
    """
    Fetch historical price data for technical analysis.
    
    Args:
        ticker: Stock ticker symbol
        period: Time period (1mo, 3mo, 6mo, 1y, 2y, 5y)
        
    Returns:
        JSON string containing historical price statistics
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        
        if hist.empty:
            return json.dumps({"error": "No historical data found"})
        
        stats = {
            "period": period,
            "data_points": len(hist),
            "start_date": hist.index[0].strftime("%Y-%m-%d"),
            "end_date": hist.index[-1].strftime("%Y-%m-%d"),
            "highest_price": float(hist["High"].max()),
            "lowest_price": float(hist["Low"].min()),
            "average_price": float(hist["Close"].mean()),
            "price_volatility": float(hist["Close"].std()),
            "average_volume": float(hist["Volume"].mean()),
            "total_return_pct": float(((hist["Close"][-1] - hist["Close"][0]) / hist["Close"][0]) * 100),
            "current_price": float(hist["Close"][-1]),
            "starting_price": float(hist["Close"][0])
        }
        
        recent_data = hist.tail(30)
        stats["recent_30d_trend"] = "upward" if recent_data["Close"][-1] > recent_data["Close"][0] else "downward"
        stats["recent_30d_change_pct"] = float(((recent_data["Close"][-1] - recent_data["Close"][0]) / recent_data["Close"][0]) * 100)
        
        return json.dumps(stats, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def calculate_technical_indicators(ticker: str) -> str:
    """
    Calculate key technical indicators (Moving Averages, RSI, etc.).
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        JSON string containing technical indicators
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="3mo")
        
        if hist.empty:
            return json.dumps({"error": "No data for technical indicators"})
        
        hist["SMA_20"] = hist["Close"].rolling(window=20).mean()
        hist["SMA_50"] = hist["Close"].rolling(window=50).mean()
        
        delta = hist["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        hist["RSI"] = 100 - (100 / (1 + rs))
        
        current_price = float(hist["Close"][-1])
        sma_20 = float(hist["SMA_20"][-1]) if not pd.isna(hist["SMA_20"][-1]) else 0
        sma_50 = float(hist["SMA_50"][-1]) if not pd.isna(hist["SMA_50"][-1]) else 0
        rsi = float(hist["RSI"][-1]) if not pd.isna(hist["RSI"][-1]) else 0
        
        indicators = {
            "current_price": current_price,
            "sma_20": sma_20,
            "sma_50": sma_50,
            "rsi_14": rsi,
            "price_vs_sma20": "above" if current_price > sma_20 else "below",
            "price_vs_sma50": "above" if current_price > sma_50 else "below",
            "rsi_signal": "overbought" if rsi > 70 else "oversold" if rsi < 30 else "neutral",
            "trend_signal": "bullish" if sma_20 > sma_50 else "bearish"
        }
        
        return json.dumps(indicators, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


analyst_tools = [
    get_stock_quote,
    get_financial_metrics,
    get_historical_price_data,
    calculate_technical_indicators
]