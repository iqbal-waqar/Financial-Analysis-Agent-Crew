from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()


def get_llm(temperature: float = 0.7, model: str = None):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    
    model_name = model or os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    
    llm = ChatGroq(
        groq_api_key=api_key,
        model_name=model_name,
        temperature=temperature,
        max_tokens=8192 
    )
    
    return llm


def get_research_llm(temperature: float = 0.7):
    return get_llm(temperature=temperature)


def get_analyst_llm(temperature: float = 0.3):
    return get_llm(temperature=temperature)


def get_writer_llm(temperature: float = 0.5):
    return get_llm(temperature=temperature)