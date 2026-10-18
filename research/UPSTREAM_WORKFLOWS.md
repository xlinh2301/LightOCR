# Upstream workflow provenance

- OpenSpec: initialized in this project using `@fission-ai/openspec@latest`; Codex integration skills are in `.agents/skills/openspec-*`.
- ARS-Codex: copied `skills/academic-research-suite/` from https://github.com/Imbad0202/academic-research-skills-codex at commit `71528d9349bcdacfbe94111f06d9e2d82215a44d`. This is the Codex-native distribution of the Academic Research Skills workflow.
- ASD-STE100: copied the upstream repository from https://github.com/danyuchn/asd-ste100-skill at commit `3944283c183eea13fe5bd902b572da3b4de8bf44`; includes its skill, references, examples, and linter.
- OpenScholar: upstream repository https://github.com/akariasai/openscholar is documented as retrieval-augmented language-model synthesis. This project does not install or run its generation/training stack. `.agents/skills/openscholar-retrieval/` constrains use to retrieval only; the local client calls Semantic Scholar's Graph API and Codex performs synthesis.

Upstream skills are vendored project-local copies. Review upstream licenses and update intentionally; preserve their attribution/license files.
