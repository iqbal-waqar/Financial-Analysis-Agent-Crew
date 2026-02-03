# 📊 Financial Analysis Multi-Agent System

A sophisticated AI-powered financial analysis platform that uses **LangGraph multi-agent architecture** to analyze stocks with real-time market data.

## 🤖 How It Works

This system uses **three specialized AI agents** that work together in a sequential pipeline, each with autonomous decision-making capabilities:

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INPUT: Stock Ticker                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 1: Market Researcher Agent 🔍                        │
│  ├─ Calls: get_company_profile()                            │
│  ├─ Calls: get_company_news()                               │
│  ├─ Calls: get_analyst_recommendations()                    │
│  ├─ Calls: get_price_target_consensus()                     │
│  └─ Output: Comprehensive market research (1200+ words)     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 2: Data Analyst Agent 📈                             │
│  ├─ Calls: get_stock_quote()                                │
│  ├─ Calls: get_financial_metrics()                          │
│  ├─ Calls: get_historical_price_data()                      │
│  ├─ Calls: calculate_technical_indicators()                 │
│  └─ Output: Detailed financial analysis (1500+ words)       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  STAGE 3: Report Writer Agent 📝                            │
│  ├─ Synthesizes research + analysis                         │
│  └─ Output: Executive summary (200-300 words)               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ Final Report │
                  └──────────────┘
```

---

## 🧠 Agent Architecture: ReAct Pattern

Each agent follows the **ReAct (Reasoning + Acting) pattern** from LangGraph:

### **How an Agent Works:**

```python
1. REASONING PHASE
   ↓
   Agent receives task: "Analyze AAPL"
   Agent thinks: "I need company data, news, and analyst opinions"
   Agent decides: "I'll call get_company_profile first"
   
2. ACTION PHASE
   ↓
   Agent calls: get_company_profile(ticker="AAPL")
   Tool executes: Fetches real data from Finnhub API
   
3. OBSERVATION PHASE
   ↓
   Agent receives: {name: "Apple Inc.", industry: "Technology", ...}
   Agent thinks: "Good, now I need recent news"
   Agent decides: "I'll call get_company_news next"
   
4. LOOP CONTINUES
   ↓
   Agent keeps calling tools until it has all needed data
   
5. SYNTHESIS PHASE
   ↓
   Agent thinks: "I have all the data, time to write the report"
   Agent writes: Comprehensive analysis based on gathered data
```

### **Key Features:**

✅ **Autonomous Decision-Making**: Agents decide which tools to call and when  
✅ **Dynamic Tool Selection**: Not hardcoded - agents adapt based on task  
✅ **Iterative Reasoning**: Agents can call multiple tools in sequence  
✅ **Self-Termination**: Agents know when they have enough data  

---

## 🔧 Tool Calling System

### **How Tools Work:**

Each agent has access to **specialized tools** that fetch real-time data:

#### **1. Market Researcher Tools:**

```python
@tool
def get_company_profile(ticker: str) -> str:
    """Fetches company fundamentals from Finnhub API"""
    client = finnhub.Client(api_key=FINNHUB_API_KEY)
    profile = client.company_profile2(symbol=ticker)
    # Returns: name, industry, market cap, IPO date, etc.
```

```python
@tool
def get_company_news(ticker: str) -> str:
    """Fetches recent news from Finnhub API"""
    client = finnhub.Client(api_key=FINNHUB_API_KEY)
    news = client.company_news(ticker, from_date, to_date)
    # Returns: headlines, summaries, sources, dates
```

#### **2. Data Analyst Tools:**

```python
@tool
def get_stock_quote(ticker: str) -> str:
    """Fetches real-time stock price from Finnhub API"""
    client = finnhub.Client(api_key=FINNHUB_API_KEY)
    quote = client.quote(symbol=ticker)
    # Returns: current price, change, high, low, volume
```

```python
@tool
def get_financial_metrics(ticker: str) -> str:
    """Fetches financial KPIs from Finnhub API"""
    client = finnhub.Client(api_key=FINNHUB_API_KEY)
    metrics = client.company_basic_financials(ticker, 'all')
    # Returns: P/E ratio, EPS, ROE, debt/equity, etc.
```

```python
@tool
def get_historical_price_data(ticker: str, period: str) -> str:
    """Fetches historical prices from Yahoo Finance"""
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    # Returns: 6 months of OHLC data, trends, volatility
```

---

## 📡 Real-Time Data Sources

### **Primary: Finnhub API** 🌐

- **Company Profiles**: Business info, industry, market cap
- **Stock Quotes**: Real-time prices (~15 min delay on free tier)
- **Company News**: Latest news articles and developments
- **Analyst Data**: Recommendations, ratings, consensus
- **Financial Metrics**: P/E, EPS, ROE, margins, ratios

### **Secondary: Yahoo Finance (yfinance)** 📈

- **Historical Prices**: 6-month OHLC data
- **Technical Indicators**: SMA, RSI, trend analysis
- **Price Statistics**: Volatility, returns, momentum

### **Data Freshness:**

| Data Type | Update Frequency |
|-----------|------------------|
| Stock Prices | ~15 min delay (free tier) |
| Company News | Real-time |
| Analyst Ratings | Updated as published |
| Financial Metrics | Quarterly/Annual |
| Historical Data | Daily close |

---

## 🔄 Complete Execution Flow

### **Step-by-Step Process:**

1. **User Input**: Enter stock ticker (e.g., "AAPL")

2. **Market Researcher Agent Activates**:
   ```
   Agent: "I need to research AAPL"
   Agent: "Calling get_company_profile(AAPL)"
   Tool: Fetches data from Finnhub → Returns company info
   Agent: "Got it. Now calling get_company_news(AAPL)"
   Tool: Fetches news from Finnhub → Returns 7 days of news
   Agent: "Good. Now calling get_analyst_recommendations(AAPL)"
   Tool: Fetches analyst data → Returns ratings breakdown
   Agent: "Perfect. I have enough data to write the report"
   Agent: Writes 1200+ word market research report
   ```

3. **Data Analyst Agent Activates**:
   ```
   Agent: "I need to analyze AAPL financials"
   Agent: "Calling get_stock_quote(AAPL)"
   Tool: Fetches current price from Finnhub → Returns quote data
   Agent: "Now calling get_financial_metrics(AAPL)"
   Tool: Fetches metrics from Finnhub → Returns P/E, EPS, etc.
   Agent: "Calling get_historical_price_data(AAPL, 6mo)"
   Tool: Fetches from Yahoo Finance → Returns 6 months of prices
   Agent: "Finally calling calculate_technical_indicators(AAPL)"
   Tool: Calculates SMA, RSI → Returns technical signals
   Agent: "I have complete financial picture"
   Agent: Writes 1500+ word financial analysis
   ```

4. **Report Writer Agent Activates**:
   ```
   Agent: "I have research and analysis data"
   Agent: "Synthesizing key insights"
   Agent: Writes 200-300 word executive summary
   ```

5. **Output**: Complete financial analysis displayed in web UI

---

## 🏗️ Technical Architecture

### **Backend Stack:**

- **LangGraph**: Multi-agent orchestration framework
- **LangChain**: LLM integration and tool binding
- **Groq**: Fast LLM inference (llama-3.3-70b-versatile)
- **FastAPI**: REST API backend
- **Finnhub SDK**: Market data integration
- **yfinance**: Historical price data

### **Frontend Stack:**

- **Streamlit**: Interactive web interface
- **Markdown Rendering**: Rich text display

### **Agent Implementation:**

```python
# Each agent is a LangGraph compiled graph
def create_researcher_agent():
    workflow = StateGraph(ResearcherState)
    
    # Agent reasoning node
    workflow.add_node("agent", researcher_node)
    
    # Tool execution node
    workflow.add_node("tools", ToolNode(research_tools))
    
    # Conditional routing: tools → agent → tools → ... → end
    workflow.add_conditional_edges("agent", should_continue)
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()
```

---

## 🚀 Key Features

### **1. Autonomous Agents**
- Agents decide which tools to call (not hardcoded)
- Dynamic reasoning based on task requirements
- Self-directed execution flow

### **2. Real-Time Market Data**
- Live stock prices from Finnhub
- Recent news and developments
- Current analyst recommendations
- Up-to-date financial metrics

### **3. Comprehensive Analysis**
- 1200+ word market research reports
- 1500+ word financial analysis
- Data-driven insights and recommendations

### **4. Professional Output**
- Institutional-quality research
- Structured markdown formatting
- Specific numbers and data points

---

## 📊 Example Tool Call Sequence

**For ticker "TSLA":**

```
1. Market Researcher:
   ├─ get_company_profile("TSLA")
   │  └─ Finnhub API → {name: "Tesla Inc.", industry: "Auto", ...}
   ├─ get_company_news("TSLA")
   │  └─ Finnhub API → [{headline: "Tesla Q4 earnings...", ...}, ...]
   ├─ get_analyst_recommendations("TSLA")
   │  └─ Finnhub API → {buy: 15, hold: 8, sell: 3, ...}
   └─ get_price_target_consensus("TSLA")
       └─ Finnhub API → {targetHigh: 350, targetMean: 250, ...}

2. Data Analyst:
   ├─ get_stock_quote("TSLA")
   │  └─ Finnhub API → {c: 242.50, h: 245.20, l: 238.10, ...}
   ├─ get_financial_metrics("TSLA")
   │  └─ Finnhub API → {peRatio: 65.2, eps: 3.72, roe: 18.5, ...}
   ├─ get_historical_price_data("TSLA", "6mo")
   │  └─ Yahoo Finance → [DataFrame with 126 days of OHLC data]
   └─ calculate_technical_indicators("TSLA")
       └─ Calculated → {sma_20: 238.45, rsi_14: 58.2, ...}

3. Report Writer:
   └─ Synthesizes all data → Executive summary
```

---

## 🎯 Why This Architecture?

### **Traditional Approach (Hardcoded):**
```python
# ❌ Rigid, inflexible
def analyze_stock(ticker):
    profile = get_company_profile(ticker)
    news = get_company_news(ticker)
    quote = get_stock_quote(ticker)
    # Always calls same tools in same order
```

### **Our Approach (Autonomous Agents):**
```python
# ✅ Flexible, intelligent
def researcher_agent(ticker):
    # Agent decides what to do
    # Agent calls tools based on reasoning
    # Agent adapts to available data
    # Agent knows when to stop
```

**Benefits:**
- 🧠 **Intelligent**: Agents reason about what data they need
- 🔄 **Adaptive**: Can handle missing data gracefully
- 🎯 **Efficient**: Only calls necessary tools
- 📈 **Scalable**: Easy to add new tools/capabilities

