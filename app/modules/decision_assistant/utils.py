from app.core.settings import settings
from openai import OpenAI
from tavily import TavilyClient

oai_client = OpenAI(
    api_key=settings.openrouter_api_key, base_url=settings.openrouter_base_url
)
tavily_client = TavilyClient(api_key=settings.tavily_api_key)
