# Protocol v1 — Lightweight Vision Architectures for General Text Recognition

**Review type:** Systematic evidence map with structured narrative synthesis; no meta-analysis planned.  
**Status:** Protocol approved by the project author on 2026-10-17; searching completed for the planned database queries, title/abstract screening remains in progress; not registered.  
**Date:** 2026-10-17. **Search window:** 2024-01-01 through 2026-10-17.  
**Reviewers:** One AI-assisted reviewer (Codex) unless a second independent reviewer joins. Screening will be reported as single-reviewer; no inter-rater agreement will be claimed.

## Rationale and questions

Efficient visual recognition has advanced across compact CNN, hybrid CNN/Transformer, attention, and state-space designs. General text recognition has different constraints from ImageNet classification: inputs are often wide, fine character strokes matter, features must preserve horizontal sequence information, and output quality is measured by character/word errors rather than class accuracy. The review will keep direct recognizer evidence separate from indirect general-vision encoder evidence.

**Primary question:** What lightweight neural architectures and efficiency techniques published from 2024 through 2026 have been evaluated for general text recognition, and what recognition-quality, parameter, compute, and deployment evidence do they report?

**Secondary question:** Which compact general-purpose vision architectures from the same period report size/efficiency trade-offs and design properties plausibly relevant to text-recognition encoders, and what evidence is still needed to establish transfer?

### PICOS adapted for computational methods

- **Population:** Images containing text for scene, document, printed, or handwritten recognition; secondary stratum: general image-recognition backbones intended for constrained deployment.
- **Intervention:** A neural architecture, backbone, sequence encoder, or training/inference method designed or evaluated for compactness, low compute, or deployment efficiency.
- **Comparator:** Other recognizers/backbones, model-size variants, non-efficient baselines, or none. Lack of a comparator is extracted as a limitation, not an automatic exclusion.
- **Primary outcomes:** Recognition quality (CER, WER, word accuracy, exact match, or equivalent) and parameter count.
- **Secondary outcomes:** FLOPs/MACs, memory, checkpoint size, latency/throughput, hardware/runtime, input resolution/aspect ratio, feature stride, training data/recipe, and code/checkpoint availability.
- **Study design:** Empirical architecture/model papers with quantitative evaluation. Peer-reviewed studies and preprints are eligible but tagged separately.

## Eligibility

### Include

1. Publicly available from 2024-01-01 to 2026-10-17.
2. Proposes, evaluates, or directly compares an architecture/efficiency method for (a) general text recognition or (b) a compact general-purpose vision encoder relevant to constrained recognition.
3. Reports a quantitative task result and enough model identity information to verify it.
4. For the primary compact-model stratum, authors explicitly describe the model as lightweight/efficient/mobile/tiny/compact or evaluate it under a deployment constraint. Tag models at or below 2M as the near-1M subgroup. Larger models enter only when they are direct comparators for a compact method or a text recognizer, in a separate scale stratum; report exact size rather than assuming that a family name implies a parameter budget.
5. Full text or sufficiently detailed public methods/results are available for extraction. Abstract-only records remain pending and are not used for detailed claims.

### Exclude

1. Detection-only, segmentation-only, restoration, medical/task-specific classification, or other applications without an evaluated general text recognizer or relevant general-purpose compact architecture.
2. Non-neural methods, surveys/editorials without original evaluation, tutorials, slides, patents, and duplicate/preprint versions. Keep the most complete version and link its related versions.
3. Outside the date window, unverifiable identity, or no quantitative results.
4. OCR embedded in a large multimodal/LLM system when standalone recognizer/encoder efficiency and recognition results cannot be separated.

## Information sources and search plan

1. **Semantic Scholar Graph API** for discovery metadata and abstracts.
2. **OpenAlex Works API** as an independent bibliographic discovery source and duplicate cross-check.
3. **Primary proceedings/publisher sources** (CVF Open Access, ECCV/Springer, ACL Anthology, OpenReview, arXiv, and official author repositories) to verify publication status and claims, not to replace database hit counts.
4. Backward/forward citation chasing from included studies, recorded separately from database searches.

Run the main search only after protocol confirmation. Record exact timestamp, query, filters, API endpoint, raw hits, export snapshot, and errors in `search_log.csv`. An HTTP 429 or other failed request is an attempted search with zero retrieved records.

### Draft query blocks

Run each block separately in both databases where supported; record each platform's translated syntax. For OpenAlex, use the Works `search.title_and_abstract` Boolean query parameter with the date filter. A preliminary API syntax check showed that concatenated quoted terms gave near-zero/poorly interpretable retrieval; this was treated as query debugging, not main screening. The amended syntax preserves the concept blocks below and is logged before interpreting results.

**Direct text recognition**

```text
("scene text recognition" OR "text recognition" OR OCR OR "optical character recognition" OR "document recognition"
  OR "handwritten text recognition" OR "handwriting recognition")
AND (lightweight OR efficient OR compact OR tiny OR mobile OR edge OR low-compute)
```

**General compact vision encoders**

```text
("lightweight vision" OR "mobile vision" OR "tiny vision transformer"
  OR "compact vision model" OR "efficient vision backbone")
AND (architecture OR backbone OR CNN OR transformer OR attention OR state-space)
```

No `NOT` block will be used in first-pass retrieval because it may remove relevant hybrid methods; irrelevant application areas will be excluded at screening.

## Record management and selection

1. Export DOI, title, authors, year, venue, abstract, URL, source, query ID, and timestamp.
2. Deduplicate by DOI, then normalized title plus year; link preprint/proceedings/journal versions.
3. Pilot title/abstract criteria, freeze clarifications in the amendment log, then screen all titles and abstracts.
4. Retrieve full text for potentially eligible records; log one primary full-text exclusion reason.
5. Codex performs one screening pass. A second independent reviewer is recommended before claiming independent dual screening; if unavailable, report single-reviewer screening.
6. Generate PRISMA-style counts only from post-confirmation main searches. Pre-protocol searches are a separate pilot corpus, not silently counted as confirmatory retrieval.

## Data extraction

Extract citation/version, publication status, architecture family, variant, task stratum, parameter count (backbone or full recognizer), FLOPs/MACs, checkpoint size, input resolution/aspect ratio, feature strides, datasets/splits, training/pretraining, augmentation/distillation, decoder/language model, metrics, hardware/runtime/backend/precision/batch size, baseline/training parity, uncertainty/repeated-run data, code/checkpoint/license, funding/COI, and a source locator for each numeric claim.

Mark unavailable values `not reported`; do not impute. Track conflicting preprint/proceedings values by version and prefer the final peer-reviewed paper when available.

## Methodological appraisal

RoB 2 and ROBINS-I are not suitable for architecture benchmark papers. Use this descriptive checklist, explicitly **not a validated risk-of-bias instrument**: dataset provenance and split integrity; baseline/training-budget fairness; parameter/FLOP definitions; hardware/runtime/latency methods; task-appropriate metrics and uncertainty; code/weights/data/license availability; and whether text-specific detail preservation is directly evaluated. Do not collapse items into one quality score; use them to qualify claims.

## Synthesis

Separate (A) direct text-recognition evidence, (B) indirect general-vision encoder evidence, and (C) larger comparisons. Synthesize by CNN, hybrid, Transformer, state-space, and other sequence-encoder families; scale strata (≤2M, >2–10M, >10M comparators); and direct versus indirect OCR evidence. Compare parameter counts only when the counted component is comparable. Treat latency as hardware/backend-specific. Do not compare ImageNet accuracy directly with CER/WER or pool incompatible datasets, input shapes, decoders, training recipes, or hardware. No meta-analysis is planned because outcomes/protocols are expected to be heterogeneous.

## Amendments and registration

This protocol followed broad exploratory Semantic Scholar searches that remain separate from the main review. The author approved the protocol on 2026-10-17. The database searches began after approval. No external registration has been made. Date and justify all later changes in `amendments.md`. Final reporting will adapt PRISMA 2020 to computational architecture evidence and state deviations/unavailable full texts. The current review is an interim synthesis because screening is incomplete; do not describe it as a completed PRISMA systematic review.

## Existing pilot corpus — not main-review screening

Before this protocol, Semantic Scholar searches 2–7 returned 300 hits and the local database contains 279 distinct records tied to those queries. The source table also contains five manually catalogued initial papers and one proceedings-verified SHViT record. The pilot retrieval focused on architectures and has only two titles obviously mentioning OCR/text recognition; it does not adequately cover the direct text-recognition question. No systematic title/abstract/full-text screening under this protocol has begun. See `../phase_1_semantic_scholar_screened.md` for the exploratory vision-architecture notes.
