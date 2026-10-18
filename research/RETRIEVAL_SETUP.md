# Literature retrieval setup

- OpenScholar is a retrieval reference only. Do not run its LLM inference, training, or model downloads.
- Metadata retrieval uses the local Semantic Scholar Graph API client and key from `.env`.
- Never display or log API keys.
- Record query, year bounds, timestamp, result count, and paper IDs.
- HTTP 429 means the API refused the request due to rate/quota policy. A failed request is not a literature result. Do not loop retries. Check the account quota and retry later.
- Verify included claims against the primary paper, proceedings, or official author repository.
- First remote and local WSL2 attempts returned HTTP 429 on 2026-10-16. Later local retrieval succeeded on 2026-10-17: searches 2–7 are stored in `research.db` (300 result rows across the saved searches; search 1 contains five manually catalogued initial sources, not an API query). Search 8 was attempted after searches 6–7 and returned HTTP 429; it produced no records. The remote API remains unverified after the initial 429.
- Search queries and screened subset are documented in `phase_1_semantic_scholar_screened.md`. Scholar results are discovery metadata only; screen and verify against proceedings, publisher pages, or official author repositories before using claims.
