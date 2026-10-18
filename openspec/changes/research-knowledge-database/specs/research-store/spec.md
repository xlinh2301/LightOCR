## ADDED Requirements
### Requirement: Preserve literature retrieval provenance
The research store SHALL record search queries and returned bibliographic metadata with source and retrieval time.
#### Scenario: Save a successful metadata search
- **WHEN** a literature metadata query returns papers
- **THEN** the query parameters and paper records are stored in the local database with provenance
### Requirement: Keep credentials and research data local
The project SHALL exclude API keys and local research databases from source control.
#### Scenario: Inspect repository changes
- **WHEN** `.env` and `research.db` exist locally
- **THEN** Git ignores them
