import base64
import concurrent.futures
import datetime
import io
import os
import subprocess

from hallw.utils.hallw_logger import logger

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_TEXT_LENGTH = 100_000  # characters
PDF_RENDER_SCALE = 2.0
PDF_MAX_IMAGE_DIMENSION = 1568
PDF_JPEG_QUALITY = 75
PDF_MAX_WORKERS = 4

IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".bmp",
    ".svg",
    ".ico",
    ".tiff",
    ".tif",
}

PDF_EXTENSIONS = {".pdf"}

DOCLING_EXTENSIONS = {
    ".docx",
    ".doc",
    ".pptx",
    ".xlsx",
    ".xls",
}

BINARY_EXTENSIONS = {
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".bin",
    ".o",
    ".obj",
    ".sys",
    ".drv",
    ".ocx",
    ".cpl",
    ".scr",
    ".msi",
}

# Mapping from extension to MIME type for images
IMAGE_MIME_MAP = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".tiff": "image/tiff",
    ".tif": "image/tiff",
}


def parse_file(file_path: str) -> list[dict] | None:
    """
    Parse a file of any file type.

    Args:
        file_path: Absolute path to the file.

    Returns:
        one or more blocks as part of HumanMessage
    """
    file_path = os.path.normpath(file_path)

    # Validate
    if not os.path.isfile(file_path):
        return None

    if not os.path.exists(file_path):
        return [{"type": "text", "text": "(file not exists)"}]

    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        return [{"type": "text", "text": "(file too large)"}]

    if file_size == 0:
        return [{"type": "text", "text": "(empty file)"}]

    ext = os.path.splitext(file_path)[1].lower()

    prefix_block = {"type": "text", "text": f"File: {file_path}"}

    # Route to appropriate handler
    if ext in IMAGE_EXTENSIONS:
        return [prefix_block, *_parse_image(file_path, ext)]
    elif ext in PDF_EXTENSIONS:
        return [prefix_block, *_parse_pdf(file_path)]
    elif ext in DOCLING_EXTENSIONS:
        return [prefix_block, *_parse_document(file_path)]
    elif ext in BINARY_EXTENSIONS:
        return [prefix_block, *_parse_binary(file_path, ext)]
    else:
        return [prefix_block, *_parse_text_or_fallback(file_path)]


def _parse_image(file_path: str, ext: str) -> list[dict]:
    """Read image file and convert to base64."""
    try:
        mime = IMAGE_MIME_MAP.get(ext, "image/png")
        with open(file_path, "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode("utf-8")
        return [
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}"},
            }
        ]
    except Exception as e:
        return [{"type": "text", "text": f"Failed to read image: {e}"}]


def _parse_pdf(file_path: str) -> list[dict]:
    """Render PDF pages to image blocks."""
    try:
        import pypdfium2 as pdfium

        pdf = pdfium.PdfDocument(file_path)
        page_count = len(pdf)
        pdf.close()

        page_blocks: list[dict] = []
        max_workers = min(PDF_MAX_WORKERS, max(1, page_count))

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_page = {
                executor.submit(_render_pdf_page, file_path, page_index): page_index for page_index in range(page_count)
            }
            page_results: dict[int, list[dict]] = {}

            for future in concurrent.futures.as_completed(future_to_page):
                page_index = future_to_page[future]
                page_results[page_index] = future.result()

        for page_index in range(page_count):
            page_blocks.extend(page_results[page_index])

        return page_blocks
    except Exception as e:
        logger.error(f"PDF parse failed for {file_path}: {e}")
        return [{"type": "text", "text": f"Failed to parse PDF: {e}"}]


def _render_pdf_page(file_path: str, page_index: int) -> list[dict]:
    import pypdfium2 as pdfium
    from PIL import Image

    pdf = pdfium.PdfDocument(file_path)
    page = pdf[page_index]
    try:
        bitmap = page.render(scale=PDF_RENDER_SCALE).to_pil()

        if bitmap.mode not in ("RGB", "L"):
            bitmap = bitmap.convert("RGB")

        # Cap image size to control payload size and vision token cost.
        if max(bitmap.size) > PDF_MAX_IMAGE_DIMENSION:
            bitmap.thumbnail((PDF_MAX_IMAGE_DIMENSION, PDF_MAX_IMAGE_DIMENSION), Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        bitmap.save(buffer, format="JPEG", quality=PDF_JPEG_QUALITY, optimize=True)
        b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]
    except Exception as e:
        logger.error(f"Failed to render PDF page {page_index} of {file_path}: {e}")
        return [{"type": "text", "text": f"(failed to render page {page_index + 1}: {e})"}]
    finally:
        page.close()
        pdf.close()


def _parse_document(file_path: str) -> list[dict]:
    """Parse DOC/DOCX/PPTX/XLSX using Docling DocumentConverter."""
    try:
        from docling.document_converter import DocumentConverter

        converter = DocumentConverter()
        result = converter.convert(file_path)
        content = result.document.export_to_markdown()

        if len(content) > MAX_TEXT_LENGTH:
            content = content[:MAX_TEXT_LENGTH] + "\n\n... (truncated)"

        return [{"type": "text", "text": content}]
    except Exception as e:
        logger.error(f"Docling parse failed for {file_path}: {e}")
        # Fallback: try reading as text
        return [{"type": "text", "text": f"Failed to parse document: {e}"}]


def _parse_binary(file_path: str, ext: str) -> list[dict]:
    """
    Analyze binary files:
    1. Extract visible strings
    2. For PE files (.exe, .dll, etc.), analyze PE structure with pefile
    """
    sections: list[str] = []

    # 1. Extract strings
    strings_output = _extract_strings(file_path)
    if strings_output:
        sections.append("## Extracted Strings\n```\n" + strings_output + "\n```")

    # 2. PE analysis for Windows executables
    if ext in {".exe", ".dll", ".sys", ".drv", ".ocx", ".cpl", ".scr", ".msi"}:
        pe_info = _analyze_pe(file_path)
        if pe_info:
            sections.append("## PE Structure Analysis\n" + pe_info)

    if not sections:
        return [{"type": "text", "text": "(No readable content extracted from binary file)"}]

    content = "\n\n".join(sections)
    if len(content) > MAX_TEXT_LENGTH:
        content = content[:MAX_TEXT_LENGTH] + "\n\n... (truncated)"

    return [{"type": "text", "text": content}]


def _extract_strings(file_path: str, min_length: int = 4) -> str:
    """Extract printable strings from a binary file."""
    try:
        # Try using 'strings' command (available on most systems)
        result = subprocess.run(
            ["strings", "-n", str(min_length), file_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split("\n")
            # Limit to first 500 lines
            if len(lines) > 500:
                lines = lines[:500]
                lines.append(f"... ({len(lines)} more lines)")
            return "\n".join(lines)
        return "(no strings found)"
    except FileNotFoundError:
        return "(strings command not found)"
    except subprocess.TimeoutExpired:
        return "(strings command timed out)"
    except Exception as e:
        return f"(strings command failed: {e})"


def _analyze_pe(file_path: str) -> str:
    """Analyze PE structure using pefile library."""
    try:
        import pefile

        pe = pefile.PE(file_path, fast_load=True)
        pe.parse_data_directories(
            directories=[
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"],
                pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"],
            ]
        )

        info_lines: list[str] = []

        timestamp = pe.FILE_HEADER.TimeDateStamp
        compile_time = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
        info_lines.append(f"**Compile Time:** {compile_time.isoformat()}")

        machine_types = {0x14C: "x86", 0x8664: "x64", 0xAA64: "ARM64"}
        machine = machine_types.get(pe.FILE_HEADER.Machine, f"0x{pe.FILE_HEADER.Machine:X}")
        info_lines.append(f"**Machine:** {machine}")
        info_lines.append(f"**Sections:** {pe.FILE_HEADER.NumberOfSections}")

        # Sections
        section_info = []
        for section in pe.sections:
            name = section.Name.decode("utf-8", errors="replace").strip("\x00")
            section_info.append(f"  - `{name}` (VSize: {section.Misc_VirtualSize}, RawSize: {section.SizeOfRawData})")
        if section_info:
            info_lines.append("\n**Section Details:**")
            info_lines.extend(section_info)

        # Imports
        if hasattr(pe, "DIRECTORY_ENTRY_IMPORT"):
            imports = []
            for entry in pe.DIRECTORY_ENTRY_IMPORT:
                dll_name = entry.dll.decode("utf-8", errors="replace")
                func_count = len(entry.imports)
                funcs = [imp.name.decode("utf-8", errors="replace") for imp in entry.imports[:5] if imp.name]
                preview = ", ".join(funcs)
                if func_count > 5:
                    preview += f", ... (+{func_count - 5} more)"
                imports.append(f"  - `{dll_name}` ({func_count} functions): {preview}")

            if imports:
                info_lines.append(f"\n**Imports ({len(pe.DIRECTORY_ENTRY_IMPORT)} DLLs):**")
                info_lines.extend(imports[:20])
                if len(imports) > 20:
                    info_lines.append(f"  ... (+{len(imports) - 20} more DLLs)")

        # Exports
        if hasattr(pe, "DIRECTORY_ENTRY_EXPORT"):
            exports = []
            for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols[:20]:
                name = exp.name.decode("utf-8", errors="replace") if exp.name else f"ordinal_{exp.ordinal}"
                exports.append(f"  - `{name}`")
            if exports:
                total = len(pe.DIRECTORY_ENTRY_EXPORT.symbols)
                info_lines.append(f"\n**Exports ({total} symbols):**")
                info_lines.extend(exports)
                if total > 20:
                    info_lines.append(f"  ... (+{total - 20} more)")

        pe.close()
        return "\n".join(info_lines)

    except Exception as e:
        return f"(PE analysis failed: {e})"


def _parse_text_or_fallback(file_path: str) -> list[dict]:
    """Try reading as text; if it fails (binary), fall back to string extraction."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read(MAX_TEXT_LENGTH)

        # Check if we truncated
        file_size = os.path.getsize(file_path)
        if file_size > MAX_TEXT_LENGTH:
            content += "\n\n... (truncated)"

        return [{"type": "text", "text": content}]

    except UnicodeDecodeError:
        # It's a binary file we don't recognize by extension
        ext = os.path.splitext(file_path)[1].lower()
        return _parse_binary(file_path, ext)
    except Exception as e:
        return [{"type": "text", "text": f"Failed to read file: {e}"}]
