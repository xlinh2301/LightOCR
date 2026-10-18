"""Run the protocol's two OpenAlex searches and store raw responses + metadata."""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from lightocr_research.db import connect

RAW = Path(__file__).resolve().parent / "raw_openalex"
DATE_FILTER = "from_publication_date:2024-01-01,to_publication_date:2026-10-17"
QUERIES = [
    ("direct_text_recognition", '("scene text recognition" OR "text recognition" OR "document recognition" OR "handwritten text recognition" OR "handwriting recognition") AND (lightweight OR efficient OR compact OR tiny OR mobile OR edge OR "low-compute")'),
    ("compact_vision_encoders", '("lightweight vision" OR "mobile vision" OR "tiny vision transformer" OR "compact vision model" OR "efficient vision backbone") AND (architecture OR backbone OR CNN OR transformer OR attention OR "state-space")'),
]
FIELDS = "id,doi,title,publication_year,publication_date,authorships,primary_location,best_oa_location,abstract_inverted_index,cited_by_count,type,ids"


def reconstruct_abstract(index: dict | None) -> str | None:
    if not index:
        return None
    words: list[str] = []
    for token, positions in index.items():
        for pos in positions:
            while len(words) <= pos:
                words.append("")
            words[pos] = token
    result = " ".join(w for w in words if w)
    return result or None


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    with connect() as db:
        for label, query in QUERIES:
            params = {
                "search.title_and_abstract": query,
                "filter": DATE_FILTER,
                "per-page": 100,
                "select": FIELDS,
            }
            headers = {"User-Agent": "LightOCRResearch/0.1 (systematic-review discovery)"}
            response = requests.get("https://api.openalex.org/works", params={**params, "page": 1}, headers=headers, timeout=45)
            response.raise_for_status()
            first_page = response.json()
            hit_count = first_page.get("meta", {}).get("count", 0)
            results = list(first_page.get("results", []))
            raw_pages = [first_page]
            pages = (hit_count + params["per-page"] - 1) // params["per-page"]
            for page in range(2, pages + 1):
                response = requests.get("https://api.openalex.org/works", params={**params, "page": page}, headers=headers, timeout=45)
                response.raise_for_status()
                page_payload = response.json()
                raw_pages.append(page_payload)
                results.extend(page_payload.get("results", []))
                time.sleep(0.2)
            search_id = db.execute(
                "INSERT INTO searches(query,year_from,year_to,source_api,retrieved_at,result_count) VALUES(?,?,?,?,?,?)",
                (query, 2024, 2026, "OpenAlex", now, len(results)),
            ).lastrowid
            raw_path = RAW / f"openalex_{search_id}_{label}.json"
            raw_path.write_text(json.dumps({"meta": first_page.get("meta"), "pages": raw_pages}, ensure_ascii=False, indent=2), encoding="utf-8")
            for item in results:
                paper_id = item.get("id")
                title = item.get("title")
                if not paper_id or not title:
                    continue
                authors = [
                    a.get("author", {}).get("display_name", "")
                    for a in item.get("authorships", [])
                ]
                primary = item.get("primary_location") or {}
                source = primary.get("source") or {}
                best_oa = item.get("best_oa_location") or {}
                inserted = db.execute(
                    """INSERT OR IGNORE INTO sources
                    (paper_id,title,authors_json,year,venue,abstract,doi,url,pdf_url,citation_count,
                     publication_types_json,retrieved_at,search_id,screening_status,notes)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        paper_id,
                        title,
                        json.dumps(authors, ensure_ascii=False),
                        item.get("publication_year"),
                        source.get("display_name"),
                        reconstruct_abstract(item.get("abstract_inverted_index")),
                        (item.get("doi") or "").removeprefix("https://doi.org/") or None,
                        primary.get("landing_page_url") or paper_id,
                        best_oa.get("pdf_url"),
                        item.get("cited_by_count"),
                        json.dumps([item.get("type")] if item.get("type") else []),
                        now,
                        search_id,
                        "unreviewed",
                        f"OpenAlex query={label}; OpenAlex ID={paper_id}; total API hits={hit_count}",
                    ),
                )
                if inserted.rowcount:
                    db.execute(
                        "INSERT INTO source_fts(paper_id,title,abstract) VALUES(?,?,?)",
                        (paper_id, title, reconstruct_abstract(item.get("abstract_inverted_index")) or ""),
                    )
            print(
                json.dumps(
                    {
                        "search_id": search_id,
                        "label": label,
                        "query": query,
                        "retrieved": len(results),
                        "api_total_hits": hit_count,
                        "pages": len(raw_pages),
                        "raw_path": str(raw_path),
                    },
                    ensure_ascii=False,
                )
            )


if __name__ == "__main__":
    main()
