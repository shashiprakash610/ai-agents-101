from typing import Dict, Any, Optional, List
from app.vectorstore import get_collection

def tool_internal_kb(query: str) -> Dict[str, Any]:
    # Mock internal knowledge base
    kb = {
        "Analyst A": {"hit_rate_12m": 0.62, "notes": "Strong equity factor calls; mixed macro timing."},
        "Analyst B": {"hit_rate_12m": 0.55, "notes": "Good credit selection; weaker FX timing."},
    }

    q = query.lower()
    if "analyst a" in q:
        return {"type": "internal_kb", "result": {"Analyst A": kb["Analyst A"]}}
    if "analyst b" in q:
        return {"type": "internal_kb", "result": {"Analyst B": kb["Analyst B"]}}

    return {"type": "internal_kb", "result": kb}

def tool_search_reports(
    query: str,
    bank: str | None = None,
    asset_class: str | None = None,
    report_id: str | None = None,
    k: int = 6,
):
    col = get_collection()

    where = {}

    if bank:
        where["bank"] = bank

    if asset_class:
        where["asset_class"] = asset_class

    if report_id:
        where["report_id"] = report_id

    kwargs = {"n_results": k}
    if where:
        kwargs["where"] = where

    res = col.query(query_texts=[query], **kwargs)

    chunks = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]

    return {
        "type": "retrieval",
        "chunks": chunks,
        "metadatas": metas,
        "meta": {
            "k": k,
            "filters": where,
            "source": "chroma",
        },
    }
