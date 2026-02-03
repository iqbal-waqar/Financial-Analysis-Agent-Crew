from typing import TypedDict, Literal, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
from backend.services.agents import get_researcher_agent, get_analyst_agent, get_writer_agent
import operator


class AnalysisState(TypedDict):
    ticker: str
    company_name: str
    current_stage: str
    research_data: dict
    analysis_data: dict
    report_data: dict
    status: str
    error: str
    messages: Annotated[Sequence[BaseMessage], operator.add]


def research_stage(state: AnalysisState) -> AnalysisState:
    print(f"[STAGE 1/3] Starting Market Research for {state['ticker']}...")
    
    try:
        researcher = get_researcher_agent()
        
        agent_state = {
            "messages": state.get("messages", []),
            "ticker": state["ticker"],
            "company_name": state.get("company_name", state["ticker"]),
            "research_complete": False,
            "analysis_complete": False,
            "report_complete": False,
            "research_data": "",
            "analysis_data": "",
            "next_agent": "analyst"
        }
        
        result = researcher(agent_state)
        
        research_summary = result.get("research_data", "")
        
        state["research_data"] = {"summary": research_summary}
        state["current_stage"] = "analysis"
        state["messages"] = result.get("messages", [])
        
        print(f"[STAGE 1/3] Market Research completed ✓")
        
    except Exception as e:
        state["error"] = f"Research stage error: {str(e)}"
        state["status"] = "error"
        print(f"[STAGE 1/3] Market Research failed: {str(e)}")
    
    return state


def analysis_stage(state: AnalysisState) -> AnalysisState:
    print(f"[STAGE 2/3] Starting Data Analysis for {state['ticker']}...")
    
    try:
        analyst = get_analyst_agent()
        
        agent_state = {
            "messages": state.get("messages", []),
            "ticker": state["ticker"],
            "company_name": state.get("company_name", state["ticker"]),
            "research_complete": True,
            "analysis_complete": False,
            "report_complete": False,
            "research_data": state.get("research_data", {}).get("summary", ""),
            "analysis_data": "",
            "next_agent": "writer"
        }
        
        result = analyst(agent_state)
        
        analysis_summary = result.get("analysis_data", "")
        
        state["analysis_data"] = {"summary": analysis_summary}
        state["current_stage"] = "report"
        state["messages"] = result.get("messages", [])
        
        print(f"[STAGE 2/3] Data Analysis completed ✓")
        
    except Exception as e:
        state["error"] = f"Analysis stage error: {str(e)}"
        state["status"] = "error"
        print(f"[STAGE 2/3] Data Analysis failed: {str(e)}")
    
    return state


def report_stage(state: AnalysisState) -> AnalysisState:
    print(f"[STAGE 3/3] Starting Executive Summary Generation for {state['ticker']}...")
    
    try:
        writer = get_writer_agent()
        
        research_summary = state.get("research_data", {}).get("summary", "No research data available")
        analysis_summary = state.get("analysis_data", {}).get("summary", "No analysis data available")
        
        agent_state = {
            "messages": state.get("messages", []),
            "ticker": state["ticker"],
            "company_name": state.get("company_name", state["ticker"]),
            "research_complete": True,
            "analysis_complete": True,
            "report_complete": False,
            "research_data": research_summary,
            "analysis_data": analysis_summary,
            "next_agent": "end"
        }
        
        result = writer(agent_state)
        
        summary_text = result.get("summary", "Executive summary generated successfully")
        
        state["report_data"] = {"report_text": summary_text}
        state["current_stage"] = "completed"
        state["status"] = "completed"
        state["messages"] = result.get("messages", [])
        
        print(f"[STAGE 3/3] Executive Summary completed ✓")
        print(f"\n{'='*80}")
        print(f"Financial Analysis Complete for {state['ticker']}")
        print(f"{'='*80}\n")
        
    except Exception as e:
        state["error"] = f"Report stage error: {str(e)}"
        state["status"] = "error"
        print(f"[STAGE 3/3] Executive Summary failed: {str(e)}")
    
    return state


def should_continue(state: AnalysisState) -> Literal["analysis", "report", "end"]:
    if state.get("status") == "error":
        return "end"
    
    current_stage = state.get("current_stage", "research")
    
    if current_stage == "analysis":
        return "analysis"
    elif current_stage == "report":
        return "report"
    else:
        return "end"


def create_analysis_graph():
    workflow = StateGraph(AnalysisState)
    
    workflow.add_node("research", research_stage)
    workflow.add_node("analysis", analysis_stage)
    workflow.add_node("report", report_stage)
    
    workflow.set_entry_point("research")
    
    workflow.add_conditional_edges(
        "research",
        should_continue,
        {
            "analysis": "analysis",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "analysis",
        should_continue,
        {
            "report": "report",
            "end": END
        }
    )
    
    workflow.add_edge("report", END)
    
    graph = workflow.compile()
    
    return graph


analysis_graph = create_analysis_graph()


def run_financial_analysis(ticker: str, company_name: str = None) -> dict:
    initial_state = {
        "ticker": ticker.upper(),
        "company_name": company_name or ticker.upper(),
        "current_stage": "research",
        "research_data": {},
        "analysis_data": {},
        "report_data": {},
        "status": "in_progress",
        "error": "",
        "messages": []
    }
    
    print(f"\n{'='*80}")
    print(f"Starting Financial Analysis for {ticker.upper()}")
    print(f"{'='*80}\n")
    
    result = analysis_graph.invoke(initial_state)
    
    return result