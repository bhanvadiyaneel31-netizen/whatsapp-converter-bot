"""
converter.py
============
Handles both conversion directions:
  PDF  → DOCX  using pdf2docx
  DOCX → PDF   using LibreOffice (headless) — free & accurate

Install requirements:
  pip install pdf2docx
  sudo apt install libreoffice  (Linux/Render)
  brew install libreoffice       (Mac)
  Windows: install LibreOffice from https://www.libreoffice.org
"""

import os
import subprocess
import uuid
from pdf2docx import Converter as PDFConverter


def convert_file(input_path: str, input_ext: str) -> str:
    """
    Converts a file and returns the output file path.

    Args:
        input_path : Local path to the downloaded file
        input_ext  : '.pdf' or '.docx'

    Returns:
        Path to the converted output file.
    """
    if input_ext == ".pdf":
        return pdf_to_docx(input_path)
    elif input_ext == ".docx":
        return docx_to_pdf(input_path)
    else:
        raise ValueError(f"Unsupported extension: {input_ext}")


def pdf_to_docx(pdf_path: str) -> str:
    """
    Converts a PDF file to DOCX using pdf2docx library.
    Preserves layout, tables, and images where possible.
    """
    os.makedirs("output", exist_ok=True)

    output_name = f"{uuid.uuid4().hex}.docx"
    output_path = os.path.join("output", output_name)

    print(f"🔄 Converting PDF → DOCX: {pdf_path}")

    cv = PDFConverter(pdf_path)
    cv.convert(output_path, start=0, end=None)  # Convert all pages
    cv.close()

    print(f"✅ PDF → DOCX done: {output_path}")

    # Clean up input file after conversion
    _cleanup(pdf_path)

    return output_path


def docx_to_pdf(docx_path: str) -> str:
    """
    Converts a DOCX file to PDF using LibreOffice in headless mode.
    LibreOffice is free and produces high-quality PDFs.

    Alternative (Windows only): use docx2pdf library.
    """
    os.makedirs("output", exist_ok=True)

    print(f"🔄 Converting DOCX → PDF: {docx_path}")

    # LibreOffice headless conversion
    # --outdir = where to save the output
    result = subprocess.run(
        [
            "libreoffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", "output",
            docx_path
        ],
        capture_output=True,
        text=True,
        timeout=60
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"LibreOffice conversion failed:\n{result.stderr}"
        )

    # LibreOffice names the output file same as input but with .pdf
    base_name   = os.path.splitext(os.path.basename(docx_path))[0]
    output_path = os.path.join("output", f"{base_name}.pdf")

    if not os.path.exists(output_path):
        raise FileNotFoundError(
            f"Expected output file not found: {output_path}\n"
            f"LibreOffice stdout: {result.stdout}"
        )

    print(f"✅ DOCX → PDF done: {output_path}")

    # Clean up input file
    _cleanup(docx_path)

    return output_path


def _cleanup(file_path: str):
    """Deletes temporary input files after conversion to save disk space."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️  Cleaned up: {file_path}")
    except Exception as e:
        print(f"⚠️  Could not delete {file_path}: {e}")
