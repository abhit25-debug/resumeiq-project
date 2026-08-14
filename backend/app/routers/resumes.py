from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from pypdf import PdfReader
from docx import Document

from app.services.resume_parser import parse_resume
from app.services.ats_analyzer import analyze_resume


router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"],
)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


def extract_pdf_text(file_path: Path) -> str:
    reader = PdfReader(str(file_path))

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)

    return "\n".join(pages).strip()


def extract_docx_text(file_path: Path) -> str:
    document = Document(str(file_path))

    paragraphs = [
        paragraph.text.strip()
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    return "\n".join(paragraphs)


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file was provided.",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported.",
        )

    contents = await file.read()

    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size must be less than 10 MB.",
        )

    safe_filename = Path(file.filename).name
    file_path = UPLOAD_DIR / safe_filename

    file_path.write_bytes(contents)

    # Extract text from the uploaded document
    if extension == ".pdf":
        text = extract_pdf_text(file_path)
    else:
        text = extract_docx_text(file_path)

    if not text:
        raise HTTPException(
            status_code=400,
            detail="Could not extract any text from the resume.",
        )

    # Parse the extracted resume text
    parsed_resume = parse_resume(text)

    # Calculate ATS score and suggestions
    ats_analysis = analyze_resume(
        parsed_resume,
        text,
    )

    return {
        "message": "Resume uploaded, parsed, and analyzed successfully.",
        "filename": safe_filename,
        "file_type": extension.replace(".", ""),
        "text_length": len(text),
        "resume": parsed_resume,
        "ats_analysis": ats_analysis,
    }