# Local Semantic Scholar status — 2026-10-16

- Local checkout: Windows workspace, run through WSL2 Ubuntu (Python 3.14.4).
- A project virtual environment is installed at `.venv/`; `lightocr db init` succeeds and `lightocr sources` reads the five initial source records.
- `.env` was copied from the gmoe project without printing the key. Windows ACL inheritance was disabled and read/write access was granted to the current user. `.env` remains ignored by Git.
- Initial Semantic Scholar Graph API requests from local WSL2 and gmoe returned HTTP 429 on 2026-10-16. Local requests later succeeded on 2026-10-17 for saved searches 2–7; search 8 returned 429, so no result rows were created for it. See `research.db` and `phase_1_semantic_scholar_screened.md` for exact query records and screening.
- Searches 2–7 provide broad discovery coverage, not exhaustive/systematic coverage. The broad search was noisy and returned application-specific papers, so only a small subset was promoted for primary-source verification. API 429 indicates rate/quota refusal; it does not identify the cause.
- The initial Phase 1 note and the screened paper facts are verified from proceedings/publisher/official repository sources, not inferred from Semantic Scholar metadata alone.
- Local project skills installed: OpenSpec Codex workflows, ARS-Codex, ASD-STE100, and a project-specific OpenScholar retrieval-only skill.

Do not retry in a tight loop. Check Semantic Scholar key/account quota and retry after the service's rate limit clears. Keep the failed 429 attempt distinct from any successful literature search.
