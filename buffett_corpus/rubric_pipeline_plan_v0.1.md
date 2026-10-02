# Buffett rubric extraction pipeline — v0.1

## Goal

Turn first-party investment text into 50–100 atomic, trajectory-observable rubrics per investor, with evidence strong enough for a later expert comparison.

## Passes

1. **Corpus and provenance.** Keep the official source URL, source version/hash, year, section, and normalized text span. This stage is complete for the Buffett pilot.
2. **Principle extraction.** Ask a model to extract only explicit or strongly repeated investment claims. It must return a short claim, a verbatim fragment, and an evidence locator. It may not invent a rule from a company anecdote without marking it as an inference.
3. **Operationalization.** Convert each claim into one observable behavior in a trading-agent trajectory. Produce `criterion`, `applicability`, `source`, and `operationalization` in the fixed JSON schema.
4. **Verification.** Run a separate verifier prompt against the source span and draft. Check entailment, atomicity, applicability, observability, style specificity, and duplication. A failed check sends the item back for revision.
5. **Human calibration.** Review the first 15–20 Buffett items, revise the schema and prompts, then freeze v0.1 before expanding to 50–100 items and other investors.
6. **Versioned expansion.** Store the source snapshot, prompts, model configuration, and verifier output with each rubric batch so that a prompt change can be compared against the previous batch.

## Model roles

Use Codex to build and run the workflow, inspect source evidence, and edit failed records. For repeatable generation, use a structured-output LLM call with low temperature; do not rely on free-form one-shot Codex output for the full 300–800-item corpus. Use separate proposer and verifier calls, even if they use the same base model.

## Artifacts

- `source_chunks.jsonl`: source spans with provenance
- `principle_candidates.jsonl`: text-grounded claims
- `buffett_rubrics_v0.1.jsonl`: 20 draft atomic items
- `rubric_verification_v0.1.jsonl`: verifier decisions and reasons
- `final_rubrics.jsonl`: approved records only

## Important scoring choice

A rubric needs an applicability gate. If the trajectory never reaches the relevant decision situation, return `not_applicable` and omit the item from the score denominator. Only applicable items receive `criteria_met: true/false`. This prevents a trading agent from being penalized for not discussing a decision it never faced.
