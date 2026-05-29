"""
converter.py
============
Handles both conversion directions:
  PDF  → DOCX  using pdf2docx
  DOCX → PDF   using LibreOffice (headless)
"""

import os
import subprocess
import uuid
import shutil
from pdf2docx import Converter as PDFConverter


def get_libreoffice_path():
    """Find LibreOffice binary across different OS."""
    # Try system PATH first (Linux/Render)
    path = shutil.which("libreoffice") or shutil.which("soffice")
    if path:
        return path
    # Mac fallback
    mac_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    if os.path.exists(mac_path):
        return mac_path
    return None


def convert_file(input_path: str, input_ext: str) -> str:
    if input_ext == ".pdf":
        return pdf_to_docx(input_path)
    elif input_ext == ".docx":
        return docx_to_pdf(input_path)
    else:
        raise ValueError(f"Unsupported extension: {input_ext}")


def pdf_to_docx(pdf_path: str) -> str:
    os.makedirs("output", exist_ok=True)
    output_name = f"{uuid.uuid4().hex}.docx"
    output_path = os.path.join("output", output_name)

    print(f"🔄 Converting PDF → DOCX: {pdf_path}")
    cv = PDFConverter(pdf_path)
    cv.convert(output_path, start=0, end=None)
    cv.close()
    print(f"✅ PDF → DOCX done: {output_path}")
    _cleanup(pdf_path)
    return output_path


def docx_to_pdf(docx_path: str) -> str:
    os.makedirs("output", exist_ok=True)
    print(f"🔄 Converting DOCX → PDF: {docx_path}")

    libreoffice = get_libreoffice_path()
    if not libreoffice:
        raise RuntimeError(
            "LibreOffice not found. Install it:\n"
            "  Linux: apt-get install libreoffice\n"
            "  Mac: brew install --cask libreoffice"
        )

    print(f"   Using LibreOffice: {libreoffice}")
    result = subprocess.run(
        [libreoffice, "--headless", "--convert-to", "pdf", "--outdir", "output", docx_path],
        capture_output=True, text=True, timeout=60
    )

    if result.returncode != 0:
        raise RuntimeError(f"LibreOffice failed:\n{result.stderr}")

    base_name = os.path.splitext(os.path.basename(docx_path))[0]
    output_path = os.path.join("output", f"{base_name}.pdf")

    if not os.path.exists(output_path):
        raise FileNotFoundError(f"Output not found: {output_path}")

    print(f"✅ DOCX → PDF done: {output_path}")
    _cleanup(docx_path)
    return output_path


def _cleanup(file_path: str):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️  Cleaned up: {file_path}")
    except Exception as e:
        print(f"⚠️  Could not delete {file_path}: {e}")