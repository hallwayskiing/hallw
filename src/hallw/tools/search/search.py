from urllib.parse import quote

import httpx
from langchain_core.tools import tool

from hallw.tools import build_tool_response
from hallw.utils.config_mgr import config

BRAVE_SEARCH_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"
BRAVE_SUMMARY_ENDPOINT = "https://api.search.brave.com/res/v1/summarizer/search"
BOCHA_SEARCH_ENDPOINT = "https://api.bochaai.com/v1/web-search"


async def _brave_search(query: str) -> str:
    """Brave web search with AI summary + extra snippets + entity info."""

    api_key = config.brave_search_api_key
    if not api_key:
        return build_tool_response(False, "Brave API key not configured.")

    key_value = api_key.get_secret_value() if hasattr(api_key, "get_secret_value") else str(api_key)

    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": key_value,
    }

    try:
        async with httpx.AsyncClient() as client:
            # ---------------------------------------------------
            # 1. Web Search (extra snippets + summary trigger)
            # ---------------------------------------------------

            search_params = {
                "q": query,
                "count": config.search_result_count or 10,
                "extra_snippets": 1,
                "summary": 1,
            }

            search_res = await client.get(
                BRAVE_SEARCH_ENDPOINT,
                headers=headers,
                params=search_params,
                timeout=15.0,
            )

            search_res.raise_for_status()
            search_data = search_res.json()

            # ---------------------------------------------------
            # 2. AI Summary + Entity Info
            # ---------------------------------------------------

            summary_text = ""
            entities_info: dict = {}

            summary_key = search_data.get("summarizer", {}).get("key")

            if summary_key:
                encoded_key = quote(summary_key, safe="")

                summary_params = {
                    "key": encoded_key,
                    "entity_info": 1,
                    "format": "markdown",
                }

                summary_res = await client.get(
                    BRAVE_SUMMARY_ENDPOINT,
                    headers=headers,
                    params=summary_params,
                    timeout=15.0,
                )

                if summary_res.status_code == 200:
                    summary_data = summary_res.json()

                    summary_text = summary_data.get("summary", {}).get("answer", "")
                    entities_info = summary_data.get("entities_info", {}) or {}

            # ---------------------------------------------------
            # 3. Supporting Sources
            # ---------------------------------------------------

            web_results = search_data.get("web", {}).get("results", [])

            sources = []
            for item in web_results:
                snippets = " ".join(item.get("extra_snippets") or [])

                sources.append(
                    {
                        "title": item.get("title"),
                        "url": item.get("url"),
                        "content": f"{item.get('description', '')} {snippets}".strip(),
                    }
                )

    except Exception as e:
        return build_tool_response(False, f"Brave API Error: {str(e)}")

    # ---------------------------------------------------
    # 4. Format Output
    # ---------------------------------------------------

    output_parts = []

    if summary_text:
        output_parts.append(f"## AI Summary\n{summary_text}")

    if entities_info:
        entity_lines = []
        for name, ent in entities_info.items():
            desc = ent.get("description", "")
            entity_lines.append(f"- **{name}**: {desc}")

        output_parts.append("## Entities\n" + "\n".join(entity_lines))

    if sources:
        source_lines = []
        for s in sources:
            source_lines.append(f"### {s['title']}\n{s['content']}\n{s['url']}")

        output_parts.append("## Supporting Sources\n" + "\n\n".join(source_lines))

    final_content = "\n\n---\n\n".join(output_parts)

    return build_tool_response(
        True,
        f"Brave search completed for '{query}'.",
        {
            "query": query,
            "summary": summary_text,
            "entities": entities_info,
            "sources": sources,
            "content": final_content,
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

    # Format Output
    output_parts = []

    if summary_text:
        output_parts.append(f"## AI Summary\n{summary_text}")

    if sources:
        source_lines = []
        for s in sources:
            source_lines.append(f"### {s['title']}\n{s['content']}\n{s['url']}")

        output_parts.append("## Supporting Sources\n" + "\n\n".join(source_lines))

    final_content = "\n\n---\n\n".join(output_parts)

    return build_tool_response(
        True,
        f"Bocha search completed for '{query}'.",
        {
            "query": query,
            "summary": summary_text,
            "sources": sources,
            "content": final_content,
        },
    )


@tool
async def search(query: str) -> str:
    """
    Web search using the configured search engine (Brave or Bocha).
    """
    engine = config.search_engine or "brave"

    if engine == "bocha":
        return await _bocha_search(query)
    else:
        return await _brave_search(query)
