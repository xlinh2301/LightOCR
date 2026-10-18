# Change: Configurable, audited train/development split sizes

## Why

The preserved local in-domain corpus has a newly constructed exploratory split containing 2,201 train examples and 244 previously exposed model-development examples. The trainer currently hard-codes the historical 1,467/244 counts, preventing a safe local fallback run.

## What changes

- Allow the run config to declare expected train and model-development counts while retaining the historical 1,467/244 defaults.
- Record expected counts and observed split identity in the data audit and run manifest.
- Add tests proving custom counts are accepted only when image/label coverage and split disjointness pass.
- Keep test and cross-data data inaccessible to this path.

## Out of scope

- Changing the model, optimizer, augmentation, or training objective.
- Treating the newly constructed split as comparable to the historical split or as independent confirmation.
- Reading test or cross-data samples.

## Success measures

- Existing historical split behavior remains the default.
- A declared custom split passes only when counts, labels, images, and overlap checks match.
