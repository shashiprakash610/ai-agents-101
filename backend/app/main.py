from fastapi import FastAPI
from pydantic import BaseModel
from app.agents import router_decide, respond_with_context

from app.tools import tool_internal_kb, tool_search_reports

import os
import tempfile
from fastapi import UploadFile, File
from app.ingest import read_pdf_text, build_records
from app.vectorstore import get_collection


app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Agentic Research Assistant API"}

class RouteRequest(BaseModel):
    message: str

@app.post("/route")
def route(req: RouteRequest):
    decision = router_decide(req.message)
    return {"input": req.message, "decision": decision}

class ChatRequest(BaseModel):
    message: str
    bank: str | None = None
    asset_class: str | None = None
    report_id: str | None = None


@app.post("/chat")
def chat(req: ChatRequest):
    decision = router_decide(req.message)
    route = decision.get("route", "retrieve_summarize")

    # Tool execution (agent "acts")
    if route == "internal_kb":
        tool_out = tool_internal_kb(req.message)
    else:
        # for retrieve_summarize / retrieve_extract / compare we simulate retrieval for now
        tool_out = tool_search_reports(req.message, bank=req.bank)


    final_answer = respond_with_context(req.message, route, tool_out)
    return {
        "input": req.message,
        "decision": decision,
        "tool_output": tool_out,
        "answer": final_answer
    }


@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    bank: str = "Unknown",
    asset_class: str = "multi-asset",
    title: str = "Untitled",
    date: str = "unknown",
):
    suffix = os.path.splitext(file.filename or "")[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        text = read_pdf_text(tmp_path)
        metadata = {"bank": bank, "asset_class": asset_class, "title": title, "date": date}

        report_id, chunks, metadatas, ids = build_records(text, metadata)
        col = get_collection()
        col.add(documents=chunks, metadatas=metadatas, ids=ids)

        return {"report_id": report_id, "chunks_indexed": len(chunks)}
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
