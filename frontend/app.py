import streamlit as st
import requests

st.set_page_config(
    page_title="Financial Analysis Agent Crew",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://localhost:8000/api"

st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-weight: bold;
        margin: 0.25rem;
    }
    .status-completed {
        background-color: #d4edda;
        color: #155724;
    }
    .status-in-progress {
        background-color: #fff3cd;
        color: #856404;
    }
    .status-error {
        background-color: #f8d7da;
        color: #721c24;
    }
    </style>
    """, unsafe_allow_html=True)


def display_header():
    st.markdown('<h1 class="main-header">📊 Financial Analysis Agent Crew</h1>', unsafe_allow_html=True)
    st.markdown("### Multi-Agent AI System for Comprehensive Stock Analysis")
    st.markdown("---")


def display_sidebar():
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/1f77b4/ffffff?text=AI+Agents", use_container_width=True)
        
        st.markdown("### 🤖 Agent Team")
        st.markdown("""
        **1. Market Researcher** 🔍
        - Gathers latest news
        - Analyzes sentiment
        - Reviews analyst opinions
        
        **2. Data Analyst** 📈
        - Pulls price data
        - Calculates KPIs
        - Technical analysis
        
        **3. Report Writer** 📝
        - Synthesizes insights
        - Creates executive summary
        - Provides recommendations
        """)
        
        st.markdown("---")
        st.markdown("### ⚙️ Technologies")
        st.markdown("""
        - **LangGraph** - Multi-agent orchestration
        - **Groq LLM** - AI intelligence
        - **Finnhub API** - Real-time data
        - **FastAPI** - Backend service
        """)


def analyze_stock(ticker: str, company_name: str = None):
    try:
        with st.spinner(f"🔄 Analyzing {ticker}... This may take a minute..."):
            response = requests.post(
                f"{API_BASE_URL}/analyze",
                json={
                    "ticker": ticker,
                    "company_name": company_name
                },
                timeout=300 
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
                return None
                
    except requests.exceptions.Timeout:
        st.error("⏰ Request timeout. The analysis is taking too long. Please try again.")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None


def display_agent_status(agent_statuses):
    st.markdown("### 🤖 Agent Execution Status")
    
    cols = st.columns(3)
    
    for idx, status in enumerate(agent_statuses):
        with cols[idx]:
            status_class = {
                "completed": "status-completed",
                "in_progress": "status-in-progress",
                "error": "status-error",
                "failed": "status-error"
            }.get(status["status"], "status-in-progress")
            
            st.markdown(f"""
            <div class="agent-card">
                <h4>{status['agent_name']}</h4>
                <span class="status-badge {status_class}">{status['status'].upper()}</span>
                <p style="margin-top: 0.5rem; font-size: 0.9rem;">{status.get('message', '')}</p>
            </div>
            """, unsafe_allow_html=True)


def display_research_data(research_data):
    if not research_data:
        return
    
    st.markdown("### 🔍 Market Research Insights")
    
    with st.expander("📰 Research Summary", expanded=True):
        summary = research_data.get("summary", "No summary available")
        st.markdown(summary)


def display_analysis_data(analysis_data):
    if not analysis_data:
        return
    
    st.markdown("### 📈 Financial Analysis")
    
    with st.expander("💹 Quantitative Analysis", expanded=True):
        summary = analysis_data.get("summary", "No analysis available")
        st.markdown(summary)


def display_report(report_data):
    if not report_data:
        return
    
    st.markdown("### 📝 Executive Summary")
    
    report_text = report_data.get("report_text", "No report available")
    
    with st.expander("📄 Investment Summary", expanded=True):
        st.markdown(report_text)



def main():
    display_header()
    display_sidebar()
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        ticker = st.text_input(
            "🎯 Stock Ticker Symbol",
            placeholder="e.g., AAPL, TSLA, GOOGL",
            help="Enter a valid stock ticker symbol"
        ).upper()
    
    with col2:
        company_name = st.text_input(
            "🏢 Company Name (Optional)",
            placeholder="e.g., Apple Inc.",
            help="Optional: Enter company name for better context"
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_button = st.button("🚀 Analyze", type="primary", use_container_width=True)
    
    if analyze_button and ticker:
        st.markdown("---")
        
        result = analyze_stock(ticker, company_name if company_name else None)
        
        if result:
            st.session_state.last_analysis = result
            
            st.success(f"✅ Analysis completed for {result['ticker']}!")
            
            if result.get("agent_statuses"):
                display_agent_status(result["agent_statuses"])
            
            st.markdown("---")
            
            tab1, tab2, tab3 = st.tabs(["🔍 Research", "📈 Analysis", "📝 Report"])
            
            with tab1:
                display_research_data(result.get("research_data"))
            
            with tab2:
                display_analysis_data(result.get("analysis_data"))
            
            with tab3:
                display_report(result.get("report_data"))
            
    elif analyze_button and not ticker:
        st.warning("⚠️ Please enter a stock ticker symbol")
    
    if not analyze_button and "last_analysis" in st.session_state:
        st.markdown("---")
        st.info("📌 Showing last analysis results. Enter a new ticker to analyze another stock.")
        
        result = st.session_state.last_analysis
        
        if result.get("agent_statuses"):
            display_agent_status(result["agent_statuses"])
        
        st.markdown("---")
        
        tab1, tab2, tab3 = st.tabs(["🔍 Research", "📈 Analysis", "📝 Report"])
        
        with tab1:
            display_research_data(result.get("research_data"))
        
        with tab2:
            display_analysis_data(result.get("analysis_data"))
        
        with tab3:
            display_report(result.get("report_data"))
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>Powered by LangGraph 🦜 | Groq 🚀 | Finnhub 📊</p>
        <p style="font-size: 0.8rem;">Multi-Agent Financial Analysis System</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()