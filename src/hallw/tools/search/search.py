import httpx
from langchain_core.tools import tool

from hallw.utils.config_mgr import config

from ..utils.tool_response import build_tool_response

TAVILY_SEARCH_ENDPOINT = "https://api.tavily.com/search"
BOCHA_SEARCH_ENDPOINT = "https://api.bochaai.com/v1/web-search"


async def _tavily_search(query: str) -> str:
    """Tavily web search API."""

    api_key = config.tavily_api_key
    if not api_key:
        return build_tool_response(False, "Tavily API key not configured.")

    key_value = api_key.get_secret_value() if hasattr(api_key, "get_secret_value") else str(api_key)

    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "api_key": key_value,
        "query": query,
        "auto_parameter": True,
        "include_answer": False,
        "include_raw_content": False,
        "max_results": config.search_result_count or 5,
        "include_images": False,
        "include_image_descriptions": False,
        "include_favicon": False,
        "include_usage": False,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                TAVILY_SEARCH_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

            web_results = data.get("results", [])
            sources = []

            for item in web_results:
                sources.append(
                    {
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "content": item.get("content", ""),
                    }
                )

    except Exception as e:
        return build_tool_response(False, f"Tavily API Error: {str(e)}")

    return build_tool_response(
        True,
        f"Tavily search completed for '{query}'.",
        {
            "query": query,
            "sources": sources,
        },
    )


async def _bocha_search(query: str) -> str:
    """Bocha AI web search."""

    api_key = config.bocha_api_key
    if not api_key:
        return build_tool_response(False, "Bocha API key not configured.")

    key_value = api_key.get_secret_value() if hasattr(api_key, "get_secret_value") else str(api_key)

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {key_value}",
        "Content-Type": "application/json",
    }

    payload = {
        "query": query,
        "count": config.search_result_count,
        "summary": True,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                BOCHA_SEARCH_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=15.0,
            )

            response.raise_for_status()
            data = response.json()

            # Parse Bocha response
            summary_text = data.get("summary", "")
            web_results = data.get("data", {}).get("webPages", {}).get("value", [])

            sources = []
            for result in web_results:
                sources.append(
                    {
                        "title": result.get("name", ""),
                        "url": result.get("url", ""),
                        "content": result.get("snippet", ""),
                    }
                )

    except Exception as e:
        return build_tool_response(False, f"Bocha API Error: {str(e)}")

    return build_tool_response(
        True,
        f"Bocha search completed for '{query}'.",
        {
            "query": query,
            "summary": summary_text,
            "sources": sources,
        },
    )


@tool
async def search(query: str) -> str:
    """
    Web search using the configured search engine (Tavily or Bocha).
    """
    engine = config.search_engine or "tavily"

    if engine == "bocha":
        return await _bocha_search(query)
    else:
        return await _tavily_search(query)
