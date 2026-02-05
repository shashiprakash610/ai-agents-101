import os
import tempfile
import uuid

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from pydantic import BaseModel

from app.auth import get_user_id
from app.db import init_db, get_db

from app.agents import router_decide, respond_with_context
from app.tools import tool_internal_kb, tool_search_reports
from app.ingest import read_pdf_text, build_records
from app.vectorstore import get_collection


app = FastAPI()


@app.on_event("startup")
async def _startup():
    await init_db()


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
    user_id: str
    message: str
    bank: str | None = None
    asset_class: str | None = None
    report_id: str | None = None



class CreateChatRequest(BaseModel):
    report_id: str | None = None
    title: str | None = None

class ChatSummary(BaseModel):
    chat_id: str
    title: str | None
    report_id: str | None
    created_at: str

class SendMessageRequest(BaseModel):
    message: str
    bank: str | None = None
    asset_class: str | None = None


# @app.post("/chat")
# def chat(req: ChatRequest):
#     decision = router_decide(req.message)
#     route = decision.get("route", "retrieve_summarize")

#     # Tool execution (agent "acts")
#     if route == "internal_kb":
#         tool_out = tool_internal_kb(req.message)
#     else:
#         # for retrieve_summarize / retrieve_extract / compare we simulate retrieval for now
#         tool_out = tool_search_reports( req.message,user_id=req.user_id,bank=req.bank,asset_class=req.asset_class,report_id=req.report_id,)



#     final_answer = respond_with_context(req.message, route, tool_out)
#     return {
#         "input": req.message,
#         "decision": decision,
#         "tool_output": tool_out,
#         "answer": final_answer
#     }


@app.post("/chats")
async def create_chat(
    req: CreateChatRequest,
    user_id: str = Depends(get_user_id),
    db=Depends(get_db),
):
    chat_id = str(uuid.uuid4())
    title = req.title or "New chat"

    # If report_id provided, ensure it belongs to this user (prevents leaking)
    if req.report_id:
        cur = await db.execute(
            "SELECT report_id FROM reports WHERE report_id = ? AND user_id = ?",
            (req.report_id, user_id),
        )
        row = await cur.fetchone()
        await cur.close()
        if row is None:
            raise HTTPException(status_code=404, detail="Report not found for this user")




@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    bank: str = "Unknown",
    asset_class: str = "multi-asset",
    title: str = "Untitled",
    date: str = "unknown",
    user_id: str = Depends(get_user_id),
    db=Depends(get_db),
):
    suffix = os.path.splitext(file.filename or "")[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        text = read_pdf_text(tmp_path)

        metadata = {
            "user_id": user_id,
            "bank": bank,
            "asset_class": asset_class,
            "title": title,
            "date": date,
            "filename": file.filename or "",
        }

        report_id, chunks, metadatas, ids = build_records(text, metadata)

        # Index into Chroma
        col = get_collection()
        col.add(documents=chunks, metadatas=metadatas, ids=ids)

        # Store report row in SQLite
        await db.execute(
            """
            INSERT OR REPLACE INTO reports(report_id, user_id, filename, title, bank, asset_class, date)
            VALUES(?, ?, ?, ?, ?, ?, ?)
            """,
            (report_id, user_id, file.filename or "", title, bank, asset_class, date),
        )
        await db.commit()

        return {"report_id": report_id, "chunks_indexed": len(chunks)}
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


@app.get("/chats")
async def list_chats(
    user_id: str = Depends(get_user_id),
    db=Depends(get_db),
):
    cur = await db.execute(
        "SELECT chat_id, title, report_id, created_at FROM chats WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    )
    rows = await cur.fetchall()
    await cur.close()

    return [
        {"chat_id": r["chat_id"], "title": r["title"], "report_id": r["report_id"], "created_at": r["created_at"]}
        for r in rows
    ]


@app.get("/chats/{chat_id}/messages")
async def get_messages(
    chat_id: str,
    user_id: str = Depends(get_user_id),
    db=Depends(get_db),
):
    # Ensure chat belongs to user
    cur = await db.execute("SELECT chat_id FROM chats WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))
    chat = await cur.fetchone()
    await cur.close()
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")

    cur = await db.execute(
        "SELECT message_id, role, content, created_at FROM messages WHERE chat_id = ? ORDER BY message_id ASC",
        (chat_id,),
    )
    rows = await cur.fetchall()
    await cur.close()

    return [
        {"message_id": r["message_id"], "role": r["role"], "content": r["content"], "created_at": r["created_at"]}
        for r in rows
    ]

@app.post("/chats/{chat_id}/messages")
async def send_message(
    chat_id: str,
    req: SendMessageRequest,
    user_id: str = Depends(get_user_id),
    db=Depends(get_db),
):
    # Load chat (and its report_id) + enforce ownership
    cur = await db.execute(
        "SELECT chat_id, report_id FROM chats WHERE chat_id = ? AND user_id = ?",
        (chat_id, user_id),
    )
    chat = await cur.fetchone()
    await cur.close()
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")

    report_id = chat["report_id"]

    # Store user message
    await db.execute(
        "INSERT INTO messages(chat_id, role, content) VALUES(?, 'user', ?)",
        (chat_id, req.message),
    )
    await db.commit()

    # Agent routing
    decision = router_decide(req.message)
    route = decision.get("route", "retrieve_summarize")

    # Tools (notice: report_id comes from the chat, not the user)
    if route == "internal_kb":
        tool_out = tool_internal_kb(req.message)
    else:
        tool_out = tool_search_reports(
            req.message,
            user_id=user_id,
            bank=req.bank,
            asset_class=req.asset_class,
            report_id=report_id,   # ✅ context comes from chat session
        )

    answer = respond_with_context(req.message, route, tool_out)

    # Store assistant message
    await db.execute(
        "INSERT INTO messages(chat_id, role, content) VALUES(?, 'assistant', ?)",
        (chat_id, answer),
    )
    await db.commit()

    return {
        "chat_id": chat_id,
        "decision": decision,
        "tool_output_meta": tool_out.get("meta", {}),
        "answer": answer,
    }
