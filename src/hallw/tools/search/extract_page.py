import httpx
from langchain_core.tools import tool

from hallw.utils.config_mgr import config

from ..utils.tool_response import build_tool_response

TAVILY_EXTRACT_ENDPOINT = "https://api.tavily.com/extract"
SHUYAN_READER_ENDPOINT = "https://api.shuyanai.com/v1/reader"


async def _tavily_extract(url: str) -> str:
    """Extract page content via Tavily extract API."""
    api_key = config.tavily_api_key
    if not api_key:
        return build_tool_response(False, "Tavily API key not configured.")

    key_value = api_key.get_secret_value() if hasattr(api_key, "get_secret_value") else str(api_key)
    max_content_length = config.extract_max_length

    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "api_key": key_value,
        "urls": [url],
        "extract_depth": "advanced",
        "include_images": False,
        "include_favicon": False,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(TAVILY_EXTRACT_ENDPOINT, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()

            data = response.json()
            results = data.get("results", [])

            if not results:
                failed_res = data.get("failed_results", [])
                if failed_res:
                    return build_tool_response(
                        False, f"Tavily Fetch Error: Failed to extract {url}: {failed_res[0].get('error')}"
                    )
                return build_tool_response(False, f"Tavily Fetch Error: Unknown error extracting {url}")

            result_data = results[0]
            content = result_data.get("raw_content", "")
            if not content:
                return build_tool_response(False, f"Tavily Fetch Error: No content returned for {url}")

            if len(content) > max_content_length:
                content = content[:max_content_length] + "...(truncated)"

            return build_tool_response(
                True,
                f"Successfully read page from {url}",
                {"url": url, "content": content},
            )

    except httpx.HTTPStatusError as e:
        return build_tool_response(False, f"HTTP {e.response.status_code} Error: {str(e)}")
    except Exception as e:
        return build_tool_response(False, f"Error reading page {url}: {str(e)}")


async def _shuyan_extract(url: str) -> str:
    """Extract page content via Shuyan Web Reader API (`/v1/reader`)."""
    api_key = config.shuyan_api_key
    if not api_key:
        return build_tool_response(False, "Shuyan API key not configured.")

    key_value = api_key.get_secret_value() if hasattr(api_key, "get_secret_value") else str(api_key)
    max_content_length = config.extract_max_length

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {key_value}",
        "Content-Type": "application/json",
    }

    payload = {
        "url": url,
        "format": "markdown",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                SHUYAN_READER_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()

            content = data.get("data", {}).get("markdown", "")
            if not content:
                return build_tool_response(False, f"Shuyan Reader Error: No content returned for {url}")

            if len(content) > max_content_length:
                content = content[:max_content_length] + "...(truncated)"

            meta = data.get("data", {}).get("metadata", {})
            return build_tool_response(
                True,
                f"Successfully read page from {url}",
                {
                    "url": meta.get("url", url),
                    "title": meta.get("title", ""),
                    "content": content,
                },
            )

    except httpx.HTTPStatusError as e:
        return build_tool_response(False, f"HTTP {e.response.status_code} Error: {str(e)}")
    except Exception as e:
        return build_tool_response(False, f"Error reading page {url}: {str(e)}")


@tool
async def extract_page(url: str) -> str:
    """
    Fetch the content of a specific web page URL and convert it to clean Markdown.
    Best used when you already have a specific URL and need to read its full content.

    Args:
        url (str): The URL of the page to extract.

    Returns:
        The main text content of the page.
    """
    engine = config.search_engine

    if engine.lower() == "shuyan":
        return await _shuyan_extract(url)
    else:
        return await _tavily_extract(url)
