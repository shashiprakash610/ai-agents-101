import re
import uuid
from typing import Dict, List, Tuple
from pypdf import PdfReader

def read_pdf_text(path: str) -> str:
    reader = PdfReader(path)
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts)

def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> List[str]:
    text = re.sub(r"\s+", " ", text).strip()
    chunks = []
    i = 0
    while i < len(text):
        end = min(len(text), i + chunk_size)
        chunks.append(text[i:end])
        if end == len(text):
            break
        i = max(0, end - overlap)
    return chunks

def build_records(text: str, metadata: Dict[str, str]) -> Tuple[str, List[str], List[Dict[str, str]], List[str]]:
    report_id = str(uuid.uuid4())
    chunks = chunk_text(text)

    metadatas = []
    ids = []
    for idx in range(len(chunks)):
        md = dict(metadata)
        md.update({"report_id": report_id, "chunk_id": str(idx)})
        metadatas.append(md)
        ids.append(f"{report_id}:{idx}")

    return report_id, chunks, metadatas, ids
