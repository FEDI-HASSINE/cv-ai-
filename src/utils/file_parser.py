"""
File Parser Module
Handles extraction of text from various file formats (PDF, DOCX, TXT)
"""

import io
from typing import Optional, Dict, Any
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
            text += page.extract_text() + "\n"
        
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
        
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
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
