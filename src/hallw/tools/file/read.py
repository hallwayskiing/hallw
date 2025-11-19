from pathlib import Path

from langchain_core.tools import tool

from hallw.tools import build_tool_response
from hallw.utils import config


@tool
def file_read(file_path: str) -> str:
    """Read a file in AI-friendly format.

    Supports: txt, md, json, yaml, csv, html, pdf

    Args:
        file_path: Absolute or relative path to the file

    Returns:
        File content as formatted string
    """
    try:
        # Resolve path relative to configured base dir
        base_dir = Path(config.file_base_dir).resolve()
        target_path = (base_dir / file_path).resolve()

        if not target_path.exists():
            return build_tool_response(False, f"File not found: {target_path}")

        if not target_path.is_file():
            return build_tool_response(False, f"Path is not a file: {target_path}")

        # Get file extension
        ext = target_path.suffix.lower()
        loaders = _get_supported_formats()

        if ext not in loaders:
            supported = ", ".join(loaders.keys())
            return build_tool_response(
                False, f"Unsupported file type: {ext}", {"supported": supported}
            )

        try:
            content = loaders[ext](str(target_path))

        except Exception as e:
            return build_tool_response(False, f"Failed to read file: {e}")

        # Truncate if too long
        if len(content) > config.file_max_read_chars:
            content = (
                content[: config.file_max_read_chars]
                + f"\n... (truncated, total {len(content)} chars)"
            )

        return build_tool_response(
            True, "File content retrieved.", {"path": str(target_path), "content": content}
        )

    except Exception as e:
        return build_tool_response(False, f"Error: {e}")


def _get_supported_formats():
    """Return dict of supported file extensions and loaders."""
    return {
        ".txt": _read_text,
        ".py": _read_text,
        ".java": _read_text,
        ".js": _read_text,
        ".css": _read_text,
        ".php": _read_text,
        ".ini": _read_text,
        ".md": _read_markdown,
        ".json": _read_json,
        ".csv": _read_csv,
        ".html": _read_html,
        ".htm": _read_html,
        ".pdf": _read_pdf,
    }


def _read_text(path: str) -> str:
    """Read plain text file."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _read_markdown(path: str) -> str:
    """Read markdown file."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _read_json(path: str) -> str:
    """Read JSON file and format as string."""
    import json

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
        raise ValueError(f"Failed to parse JSON: {e}")


def _read_csv(path: str) -> str:
    """Read CSV file and format as readable text."""
    import csv

    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                return ""
            # Format as markdown table
            lines = []
            lines.append("| " + " | ".join(reader.fieldnames) + " |")
            lines.append("|" + "|".join(["-" * 3] * len(reader.fieldnames)) + "|")
            for row in reader:
                lines.append(
                    "| " + " | ".join(str(row.get(k, "")) for k in reader.fieldnames) + " |"
                )
            return "\n".join(lines)
    except Exception as e:
        raise ValueError(f"Failed to parse CSV: {e}")


def _read_html(path: str) -> str:
    """Read HTML file and extract readable text."""
    try:
        from html.parser import HTMLParser
        from io import StringIO

        class TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = StringIO()
                self.skip_content = False

            def handle_starttag(self, tag, attrs):
                if tag in ("script", "style", "meta", "link"):
                    self.skip_content = True

            def handle_endtag(self, tag):
                if tag in ("script", "style", "meta", "link"):
                    self.skip_content = False
                elif tag in ("p", "div", "br", "h1", "h2", "h3", "h4", "h5", "h6"):
                    self.text.write("\n")

            def handle_data(self, data):
                if not self.skip_content:
                    stripped = data.strip()
                    if stripped:
                        self.text.write(stripped + "\n")

            def get_text(self):
                return self.text.getvalue()

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        extractor = TextExtractor()
        extractor.feed(content)
        return str(extractor.get_text().strip())
    except Exception as e:
        raise ValueError(f"Failed to parse HTML: {e}")


def _read_pdf(path: str) -> str:
    """Read PDF file and extract text."""
    try:
        import PyPDF2

        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = []
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text.append(page.extract_text())
            return "\n".join(text)
    except ImportError:
        raise ImportError("PyPDF2 not installed. Install with: pip install pypdf2")
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {e}")
