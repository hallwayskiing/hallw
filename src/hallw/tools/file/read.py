from pathlib import Path

import pypdf
from langchain_core.tools import tool

from hallw.tools import build_tool_response
from hallw.utils import config


@tool
def file_read(file_path: str) -> str:
    """Read a file. Automatically handles text-based files and specific formats.

    Supports:
    1. Specialized parsing: .csv, .html, .pdf, .json
    2. General text: .txt, .py, .md, .yaml, .log, .ini, .env, etc.
    3. Binary files (images, executables) will return an error.

    Args:
        file_path: Absolute or relative path to the file

    Returns:
        File content as formatted string
    """
    try:
        # Resolve path relative to configured base dir
        base_dir = Path(config.file_read_dir).resolve()
        target_path = (base_dir / file_path).resolve()

        if not target_path.exists():
            return build_tool_response(False, f"File not found: {target_path}")

        if not target_path.is_file():
            return build_tool_response(False, f"Path is not a file: {target_path}")

        # Get file extension
        ext = target_path.suffix.lower()

        # 1. Check for specialized loaders (formatting logic)
        special_loaders = _get_specialized_loaders()

        try:
            if ext in special_loaders:
                # Use specific parser for structured data
                content = special_loaders[ext](str(target_path))
            else:
                # 2. Fallback: Try to read as generic text
                if _is_binary_file(str(target_path)):
                    return build_tool_response(False, f"Cannot read binary file: {ext}")

                content = _read_any_text(str(target_path))

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


def _get_specialized_loaders():
    """Return dict of extensions that require special parsing logic."""
    return {
        ".json": _read_json,  # Keep JSON to format it nicely
        ".csv": _read_csv,
        ".html": _read_html,
        ".htm": _read_html,
        ".pdf": _read_pdf,
        # You can add .docx or .pptx here if you install python-docx etc.
    }


def _is_binary_file(path: str) -> bool:
    """Check if file is binary by looking for null bytes in the first chunk."""
    try:
        with open(path, "rb") as f:
            chunk = f.read(1024)
            # A file containing null bytes is typically binary
            return b"\0" in chunk
    except Exception:
        return False


def _read_any_text(path: str) -> str:
    """Try to read file as text with UTF-8, falling back to Latin-1."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        # Fallback for some legacy files
        try:
            with open(path, "r", encoding="latin-1") as f:
                return f.read()
        except Exception:
            raise ValueError("File encoding not supported (not UTF-8 or Latin-1)")


# ==========================================
# Specific Loaders
# ==========================================


def _read_json(path: str) -> str:
    """Read JSON file and format as string."""
    import json

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception:
        # If JSON parse fails, try reading as plain text instead of crashing
        try:
            return _read_any_text(path)
        except Exception as e:
            raise ValueError(f"Failed to parse JSON: {e}")


def _read_csv(path: str) -> str:
    """Read CSV file and format as readable text."""
    import csv

    try:
        with open(path, "r", encoding="utf-8") as f:
            # Use Sniffer to handle different delimiters automatically
            sample = f.read(1024)
            f.seek(0)
            dialect = csv.Sniffer().sniff(sample)
            reader = csv.DictReader(f, dialect=dialect)

            if reader.fieldnames is None:
                return ""

            # Format as markdown table
            lines = []
            lines.append("| " + " | ".join(reader.fieldnames) + " |")
            lines.append("|" + "|".join(["---"] * len(reader.fieldnames)) + "|")

            row_count = 0
            for row in reader:
                # Limit CSV rows to prevent context explosion
                if row_count > 50:
                    lines.append(f"\n... (truncated, {row_count} rows total)")
                    break
                lines.append(
                    "| " + " | ".join(str(row.get(k, "")) for k in reader.fieldnames) + " |"
                )
                row_count += 1

            return "\n".join(lines)
    except Exception:
        # Fallback: Read as raw text if CSV parsing fails
        return _read_any_text(path)


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
                if tag in ("script", "style", "meta", "link", "noscript"):
                    self.skip_content = True

            def handle_endtag(self, tag):
                if tag in ("script", "style", "meta", "link", "noscript"):
                    self.skip_content = False
                elif tag in ("p", "div", "br", "tr", "li", "h1", "h2", "h3"):
                    self.text.write("\n")

            def handle_data(self, data):
                if not self.skip_content:
                    stripped = data.strip()
                    if stripped:
                        self.text.write(stripped + " ")

            def get_text(self):
                return self.text.getvalue()

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        extractor = TextExtractor()
        extractor.feed(content)
        return str(extractor.get_text().strip())
    except Exception:
        # Fallback to raw HTML if parsing fails
        return _read_any_text(path)


def _read_pdf(path: str) -> str:
    """Read PDF file and extract text."""
    try:
        with open(path, "rb") as f:
            reader = pypdf.PdfReader(f)
            text = []
            # Limit pages to prevent context overflow
            max_pages = 20
            for i, page in enumerate(reader.pages):
                if i >= max_pages:
                    text.append("\n... (PDF truncated)")
                    break
                extracted = page.extract_text()
                if extracted:
                    text.append(extracted)
            return "\n".join(text)

    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {e}")
