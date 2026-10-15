# Buffett rubric samples v0.1 — review notes

This is a deliberately small draft: 20 atomic candidates, not a final scoring system. Each item has one criterion, an applicability gate, first-party provenance, and an operationalization for a trajectory grader.

## Proposed review questions

1. **Atomicity:** Does each `criterion` test one behavior? If a sentence can be split into two independent pass/fail judgments, split it.
2. **Traceability:** Does the cited text state the principle, rather than merely illustrate it in a company-specific anecdote?
3. **Operational validity:** Could a grader point to a concrete span of the agent trajectory as evidence?
4. **Applicability:** Is there a clear reason to omit the item when the relevant decision situation does not occur?
5. **Style specificity:** Would a generic competent investor receive the same score, or does the item capture Buffett's distinctive emphasis?
6. **Inference control:** Is the transformation from text to behavior marked as an `operationalization` rather than presented as a quotation?

## Scoring convention for this draft

The grader should return `criteria_met: true/false` only when `applicability` is satisfied. When the applicability gate is not satisfied, return `not_applicable` and omit the item from the denominator. This avoids penalizing a trajectory for not discussing a decision it never faced.

## Known design choices to revisit

- Whether the final evaluator should support `not_applicable` explicitly or create task-specific rubric subsets before grading.
- Whether a single source needs corroboration before a candidate is promoted to the final rubric bank.
- Whether negative criteria should be represented as prohibited behaviors or as positive requirements.
- Whether `pass_if` and `fail_if` should be shortened further for grader reliability.
