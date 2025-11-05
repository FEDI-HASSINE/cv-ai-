"""
File Parser Module
Handles extraction of text from various file formats (PDF, DOCX, TXT)

Enhancements:
- Robust text normalization to make PDF/DOCX extracted text coherent
    (fix hyphenation, collapse artificial line-breaks, preserve headings/bullets)
"""

import io
from typing import Optional, Dict, Any, List
from pathlib import Path
import re


def parse_pdf(file_bytes: bytes) -> str:
    """
    Extract text from PDF file
    
    Args:
        file_bytes: PDF file content as bytes
        
    Returns:
        Extracted text
    """
    try:
        import PyPDF2
        pdf_file = io.BytesIO(file_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text() or ""
            # Ensure each page ends with a blank line to preserve paragraph breaks across pages
            text += page_text.rstrip() + "\n\n"
        
        return text.strip()
    except ImportError:
        return "Error: PyPDF2 not installed. Please install it to parse PDF files."
    except Exception as e:
        return f"Error parsing PDF: {str(e)}"


def parse_docx(file_bytes: bytes) -> str:
    """
    Extract text from DOCX file
    
    Args:
        file_bytes: DOCX file content as bytes
        
    Returns:
        Extracted text
    """
    try:
        import docx
        doc_file = io.BytesIO(file_bytes)
        doc = docx.Document(doc_file)
        
        # Join paragraphs with blank lines to preserve structure
        paras: List[str] = [p.text.strip() for p in doc.paragraphs]
        text = "\n\n".join([p for p in paras if p])
        return text.strip()
    except ImportError:
        return "Error: python-docx not installed. Please install it to parse DOCX files."
    except Exception as e:
        return f"Error parsing DOCX: {str(e)}"


def parse_txt(file_bytes: bytes) -> str:
    """
    Extract text from TXT file
    
    Args:
        file_bytes: TXT file content as bytes
        
    Returns:
        Extracted text
    """
    try:
        return file_bytes.decode('utf-8').strip()
    except UnicodeDecodeError:
        try:
            return file_bytes.decode('latin-1').strip()
        except Exception as e:
            return f"Error parsing TXT: {str(e)}"


def _is_bullet_line(line: str) -> bool:
    """Detect bullet/numbered list lines to preserve line breaks.
    Examples: "- text", "* text", "• text", "1. text", "1) text".
    """
    l = line.lstrip()
    return bool(re.match(r"^([-*•]\s+|\d+[\.)]\s+)", l))


def _is_heading_line(line: str) -> bool:
    """Heuristic to detect headings (e.g., EDUCATION, RESEARCH EXPERIENCE & PROJECTS)."""
    s = line.strip()
    if not s:
        return False
    # Short lines, mostly uppercase, limited punctuation
    if len(s.split()) <= 8:
        letters = re.sub(r"[^A-Za-z]", "", s)
        if letters and letters.upper() == letters:
            return True
    # Trailing colon often indicates a heading
    return s.endswith(":")


def _fix_hyphenation(text: str) -> str:
    """Merge words broken by hyphen at line end: e.g., reli-\nability -> reliability"""
    # Replace common soft hyphen chars with regular hyphen if present
    text = text.replace("\u00ad", "-")
    return re.sub(r"(\w)-\n(\w)", r"\1\2", text)


def normalize_extracted_text(text: str) -> str:
    """
    Normalize raw extracted text into coherent paragraphs while preserving
    headings and bullet lists.
    - Unify newlines
    - Fix hyphenation across line breaks
    - Collapse artificial single line breaks within paragraphs into spaces
    - Preserve blank lines between paragraphs
    - Preserve bullet and numbered list formatting
    """
    if not text:
        return text

    # Normalize line endings and spaces
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\u00a0", " ")
    text = _fix_hyphenation(text)
    # Collapse 3+ newlines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    lines = [ln.rstrip() for ln in text.split("\n")]
    out_lines: List[str] = []
    paragraph_tokens: List[str] = []
    blank_run = 0  # count consecutive blank lines

    def flush_paragraph():
        nonlocal paragraph_tokens
        if paragraph_tokens:
            # Join tokens with single spaces
            paragraph_text = re.sub(r"\s+", " ", " ".join(paragraph_tokens)).strip()
            if paragraph_text:
                out_lines.append(paragraph_text)
            paragraph_tokens = []

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            # Treat a single blank line as a soft separator (do not break paragraph),
            # and two or more blank lines as a real paragraph break.
            blank_run += 1
            if blank_run >= 2:
                flush_paragraph()
                if out_lines and out_lines[-1] != "":
                    out_lines.append("")
                blank_run = 0
            # if blank_run == 1 -> soft break (ignored, words will be joined with spaces)
            continue
        else:
            blank_run = 0

        if _is_bullet_line(line) or _is_heading_line(line):
            # Keep bullets/headings on their own line
            flush_paragraph()
            out_lines.append(line)
            continue

        # Regular text: accumulate into paragraph
        paragraph_tokens.append(line)

    # Flush last paragraph
    flush_paragraph()

    # Collapse multiple blank lines to a single blank line
    normalized = []
    last_blank = False
    for l in out_lines:
        if l == "":
            if not last_blank:
                normalized.append(l)
            last_blank = True
        else:
            normalized.append(l)
            last_blank = False

    # Join using single newlines since explicit blank lines are already present
    return "\n".join(normalized).strip()


def parse_file(filename: str, file_bytes: bytes) -> Dict[str, Any]:
    """
    Parse file based on extension
    
    Args:
        filename: Name of the file
        file_bytes: File content as bytes
        
    Returns:
        Dictionary with parsed content and metadata
    """
    extension = Path(filename).suffix.lower()
    
    text = ""
    status = "success"
    error = None
    
    try:
        if extension == '.pdf':
            text = parse_pdf(file_bytes)
        elif extension in ['.docx', '.doc']:
            text = parse_docx(file_bytes)
        elif extension == '.txt':
            text = parse_txt(file_bytes)
        else:
            status = "error"
            error = f"Unsupported file format: {extension}"
            
        # Check if parsing was successful
        if text.startswith("Error"):
            status = "error"
            error = text
            text = ""
        else:
            # Normalize for better readability in UI
            text = normalize_extracted_text(text)
            
    except Exception as e:
        status = "error"
        error = str(e)
    
    return {
        "text": text,
        "filename": filename,
        "extension": extension,
        "status": status,
        "error": error,
        "char_count": len(text),
        "word_count": len(text.split()) if text else 0
    }


def parse_resume_file(file_path: str) -> str:
    """
    Convenience function used by the API to parse a resume from a file path.
    Returns normalized text or raises on error.
    """
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    data = p.read_bytes()
    result = parse_file(p.name, data)
    if result["status"] != "success":
        raise ValueError(result.get("error") or "Failed to parse file")
    return result["text"]
