from typing import Annotated, TypedDict, Sequence, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from backend.services.llm import get_research_llm, get_analyst_llm, get_writer_llm
from backend.services.research_agent_tools import research_tools
from backend.services.analyst_agent_tools import analyst_tools
import operator


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    ticker: str
    company_name: str
    research_complete: bool
    analysis_complete: bool
    report_complete: bool
    research_data: str
    analysis_data: str
    next_agent: str


# ============================================================================
# MARKET RESEARCHER AGENT - Uses ReAct Pattern
# ============================================================================

def create_researcher_agent():
    class ResearcherState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], operator.add]
        ticker: str
        company_name: str
    
    def researcher_node(state: ResearcherState):
        print("\n🔍 Market Researcher Agent - Reasoning...")
        
        ticker = state["ticker"]
        company_name = state["company_name"]
        
        system_prompt = f"""You are a senior market research analyst at a top-tier investment firm, analyzing {company_name} ({ticker}).

PHASE 1 - DATA GATHERING:
Use ALL available tools to gather comprehensive market intelligence:
1. get_company_profile - Company overview and fundamentals
2. get_company_news - Recent developments and news
3. get_analyst_recommendations - Professional analyst opinions
4. get_price_target_consensus - Price target forecasts

Call ALL tools with ticker: {ticker}

PHASE 2 - ANALYSIS & REPORT WRITING:
After gathering all data, write a comprehensive market research report (minimum 1200 words).

CRITICAL REQUIREMENTS:
- Analyze the data you gathered and decide what's most important to highlight
- Create your own report structure based on what the data reveals
- Include ALL relevant information from the tools
- Write in a professional, institutional research style
- Use markdown headers (##) for major sections - these will appear BOLD
- Include specific numbers, percentages, dates, and data points
- Use proper spacing: "The price is $50.25" NOT "$50.25,andtheprice"

CONTENT GUIDELINES (organize as you see fit):
- Start with an executive summary of your key findings
- Discuss the company's business, industry position, and competitive landscape
- Analyze recent news, developments, and their implications
- Cover analyst sentiment, recommendations, and price targets
- Identify key investment drivers (both positive and negative)
- Discuss risks, challenges, and concerns
- Provide your investment outlook and key metrics to monitor

IMPORTANT:
- Let the data guide your report structure - don't force a rigid format
- If certain data is unavailable, focus on what you have
- Be thorough and detailed - this is institutional-quality research
- Write naturally and professionally, not like filling out a template
- Make it comprehensive and insightful

Begin by calling ALL the tools, then write your comprehensive analysis."""

        messages = [HumanMessage(content=system_prompt)] + list(state["messages"])
        
        llm = get_research_llm()
        llm_with_tools = llm.bind_tools(research_tools)
        
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def should_continue(state: ResearcherState) -> Literal["tools", "end"]:
        messages = state["messages"]
        last_message = messages[-1]
        
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            print(f"   → Agent decided to call {len(last_message.tool_calls)} tool(s)")
            return "tools"
        
        print("   → Agent completed research")
        return "end"
    
    workflow = StateGraph(ResearcherState)
    
    workflow.add_node("agent", researcher_node)
    workflow.add_node("tools", ToolNode(research_tools))
    
    workflow.set_entry_point("agent")
    
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()


# ============================================================================
# DATA ANALYST AGENT - Uses ReAct Pattern
# ============================================================================

def create_analyst_agent():

    class AnalystState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], operator.add]
        ticker: str
        company_name: str
    
    def analyst_node(state: AnalystState):
        print("\n📊 Data Analyst Agent - Reasoning...")
        
        ticker = state["ticker"]
        company_name = state["company_name"]
        
        system_prompt = f"""You are a senior financial analyst and CFA charterholder analyzing {company_name} ({ticker}).

PHASE 1 - DATA GATHERING:
Use ALL available tools to gather comprehensive financial data:
1. get_stock_quote - Current stock price and performance
2. get_financial_metrics - Key financial metrics and KPIs
3. get_historical_price_data - Historical price trends (6 months)
4. calculate_technical_indicators - Technical analysis indicators

Call ALL tools with ticker: {ticker}

PHASE 2 - ANALYSIS & REPORT WRITING:
After gathering all data, write a comprehensive financial analysis report (minimum 1500 words).

CRITICAL REQUIREMENTS:
- Analyze the data you gathered and decide what's most important to highlight
- Create your own report structure based on what the financial data reveals
- Include ALL relevant metrics and data points from the tools
- Write in a professional, institutional analysis style
- Use markdown headers (##) for major sections - these will appear BOLD
- Include specific numbers, ratios, percentages, and trends
- Use proper spacing: "The P/E ratio is 25.5x" NOT "25.5x,andtheP/E"

CONTENT GUIDELINES (organize as you see fit):
- Start with an executive summary of your financial assessment
- Discuss valuation metrics and whether the stock is fairly valued
- Analyze profitability, liquidity, and leverage metrics
- Cover historical performance and price trends
- Discuss technical indicators and trading signals
- Identify financial strengths and weaknesses
- Assess growth trajectory and momentum
- Highlight key risks from a financial perspective
- Provide investment recommendation with supporting analysis

IMPORTANT:
- Let the financial data guide your report structure
- If certain metrics are unavailable, focus on what you have
- Be thorough and quantitative - this is professional financial analysis
- Write naturally, not like filling out a checklist
- Provide deep insights, not just data regurgitation
- Make it comprehensive and actionable

Begin by calling ALL the tools, then write your comprehensive financial analysis."""

        messages = [HumanMessage(content=system_prompt)] + list(state["messages"])
        
        llm = get_analyst_llm()
        llm_with_tools = llm.bind_tools(analyst_tools)
        
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def should_continue(state: AnalystState) -> Literal["tools", "end"]:
        messages = state["messages"]
        last_message = messages[-1]
        
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            print(f"   → Agent decided to call {len(last_message.tool_calls)} tool(s)")
            return "tools"
        
        print("   → Agent completed analysis")
        return "end"
    
    workflow = StateGraph(AnalystState)
    
    workflow.add_node("agent", analyst_node)
    workflow.add_node("tools", ToolNode(analyst_tools))
    
    workflow.set_entry_point("agent")
    
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()


# ============================================================================
# REPORT WRITER AGENT - Uses ReAct Pattern
# ============================================================================

def create_writer_agent():

    class WriterState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], operator.add]
        ticker: str
        company_name: str
        research_data: str
        analysis_data: str
    
    def writer_node(state: WriterState):
        print("\n📝 Report Writer Agent - Creating Summary...")
        
        ticker = state["ticker"]
        company_name = state["company_name"]
        research_data = state.get("research_data", "")
        analysis_data = state.get("analysis_data", "")
        
        system_prompt = f"""You are a professional report writer summarizing financial analysis for {company_name} ({ticker}).

You have access to:
- Market Research Data
- Financial Analysis Data

Your task is to create a CONCISE EXECUTIVE SUMMARY that synthesizes both reports.

SUMMARY REQUIREMENTS:
Write a 3-4 paragraph executive summary (200-300 words) covering:

1. **Investment Thesis**: Overall recommendation and key rationale
2. **Key Strengths**: Main positive factors from research and analysis
3. **Key Risks**: Main concerns and risk factors
4. **Conclusion**: Clear actionable takeaway for investors

FORMATTING RULES:
- Use proper spacing and punctuation
- Write complete sentences
- No markdown headers (plain text paragraphs)
- Be concise but comprehensive

Market Research Summary:
{research_data[:1000]}...

Financial Analysis Summary:
{analysis_data[:1000]}...

Provide your executive summary now (no tool calls needed)."""

        messages = [HumanMessage(content=system_prompt)]
        
        llm = get_writer_llm()
        response = llm.invoke(messages)
        
        return {"messages": [response]}
    
    workflow = StateGraph(WriterState)
    workflow.add_node("agent", writer_node)
    workflow.set_entry_point("agent")
    workflow.add_edge("agent", END)
    
    return workflow.compile()


# ============================================================================
# WRAPPER CLASSES - Maintain compatibility with existing code
# ============================================================================

class MarketResearcherAgent:
    def __init__(self):
        self.agent = create_researcher_agent()
    
    def __call__(self, state: AgentState) -> AgentState:
        print("\n🔍 Market Researcher Agent activated...")
        
        researcher_state = {
            "messages": [],
            "ticker": state["ticker"],
            "company_name": state["company_name"]
        }
        
        result = self.agent.invoke(researcher_state)
        
        research_data = ""
        for msg in result["messages"]:
            if isinstance(msg, AIMessage):
                if not msg.tool_calls:
                    research_data += msg.content + "\n"
        
        print(f"✓ Extracted research data length: {len(research_data)} characters")
        
        return {
            **state,
            "messages": state["messages"] + [AIMessage(content=f"Market research completed for {state['ticker']}")],
            "research_complete": True,
            "research_data": research_data,
            "next_agent": "analyst"
        }


class DataAnalystAgent:

    def __init__(self):
        self.agent = create_analyst_agent()
    
    def __call__(self, state: AgentState) -> AgentState:
        print("\n📊 Data Analyst Agent activated...")
        
        analyst_state = {
            "messages": [],
            "ticker": state["ticker"],
            "company_name": state["company_name"]
        }
        
        result = self.agent.invoke(analyst_state)
        
        analysis_data = ""
        for msg in result["messages"]:
            if isinstance(msg, AIMessage):
                if not msg.tool_calls:
                    analysis_data += msg.content + "\n"
        
        print(f"✓ Extracted analysis data length: {len(analysis_data)} characters")
        
        return {
            **state,
            "messages": state["messages"] + [AIMessage(content=f"Financial analysis completed for {state['ticker']}")],
            "analysis_complete": True,
            "analysis_data": analysis_data,
            "next_agent": "writer"
        }


class ReportWriterAgent:

    def __init__(self):
        self.agent = create_writer_agent()
    
    def __call__(self, state: AgentState) -> AgentState:
        print("\n📝 Report Writer Agent activated...")
        
        writer_state = {
            "messages": [],
            "ticker": state["ticker"],
            "company_name": state["company_name"],
            "research_data": state.get("research_data", ""),
            "analysis_data": state.get("analysis_data", "")
        }
        
        result = self.agent.invoke(writer_state)
        
        summary_text = ""
        for msg in result["messages"]:
            if isinstance(msg, AIMessage):
                summary_text += msg.content + "\n"
        
        print(f"✓ Generated executive summary: {len(summary_text)} characters")
        
        return {
            **state,
            "messages": state["messages"] + [AIMessage(content=f"Executive summary generated for {state['ticker']}")],
            "report_complete": True,
            "summary": summary_text,
            "next_agent": "end"
        }


# ============================================================================
# SINGLETON INSTANCES
# ============================================================================

_researcher_agent = None
_analyst_agent = None
_writer_agent = None

def get_researcher_agent():
    global _researcher_agent
    if _researcher_agent is None:
        _researcher_agent = MarketResearcherAgent()
    return _researcher_agent

def get_analyst_agent():
    global _analyst_agent
    if _analyst_agent is None:
        _analyst_agent = DataAnalystAgent()
    return _analyst_agent

def get_writer_agent():
    global _writer_agent
    if _writer_agent is None:
        _writer_agent = ReportWriterAgent()
    return _writer_agent