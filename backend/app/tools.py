from typing import Dict, Any, Optional, List
from app.vectorstore import get_collection

def tool_internal_kb(query: str) -> Dict[str, Any]:
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

from typing import Any, Dict, List, Optional

from app.vectorstore import get_collection


def tool_search_reports(
    query: str,
    user_id: str,
    bank: Optional[str] = None,
    asset_class: Optional[str] = None,
    report_id: Optional[str] = None,
    k: int = 6,
) -> Dict[str, Any]:
    col = get_collection()

    # Build filters as a list, then convert to Chroma where-clause
    filters: List[Dict[str, Any]] = [{"user_id": user_id}]  # ALWAYS isolate by user_id

    if bank:
        filters.append({"bank": bank})
    if asset_class:
        filters.append({"asset_class": asset_class})
    if report_id:
        filters.append({"report_id": report_id})

    # Chroma expects a single top-level operator when multiple filters exist
    where: Dict[str, Any] = filters[0] if len(filters) == 1 else {"$and": filters}

    res = col.query(query_texts=[query], where=where, n_results=k)

    chunks: List[str] = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]

    return {
        "type": "retrieval",
        "chunks": chunks,
        "metadatas": metas,
        "meta": {"k": k, "filters": where, "source": "chroma"},
    }

