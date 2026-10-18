# Research metadata and evidence store

## Purpose
Provide a provenance-aware local database for literature metadata and source-linked research claims.

## Requirements
### Requirement: Preserve retrieval provenance
The system SHALL store each query, year bounds, source API, retrieval time, result count, and retrieved source metadata.
#### Scenario: Successful API search
- **WHEN** Semantic Scholar returns results
- **THEN** the query and paper metadata are saved locally
### Requirement: Link claims to evidence
The system SHALL link each research claim to a paper identifier and evidence locator.
#### Scenario: Claim recorded
- **WHEN** a claim is entered
- **THEN** its source, locator, evidence type, confidence, and timestamp are retained
### Requirement: Protect secrets and restricted content
The system SHALL exclude credentials and local research data from Git.
#### Scenario: Git status check
- **WHEN** credentials or local databases exist
- **THEN** Git ignores these files by default
