import unittest
from pathlib import Path

from rubric_pipeline.cli import as_records
from rubric_pipeline.io import document_record, quote_span
from rubric_pipeline.validation import partition, principle_errors, rubric_errors


ROOT = Path(__file__).resolve().parents[1]


class PipelineValidationTests(unittest.TestCase):
    def setUp(self):
        self.doc = document_record(ROOT / "corpus/buffett/processed/1977.txt", "Warren Buffett")
        self.framework = {
            "framework_id": "tradebank",
            "canonical_event_fields": ["decision_rationale", "action"],
        }
        self.principle = {
            "principle_id": "p1",
            "document_id": self.doc["document_id"],
            "claim": "Understand the business.",
            "principle_type": "selection",
            "source_support": "direct",
            "supporting_quotes": [{"quote": "one that we can understand"}],
        }

    def test_source_quote_is_checked_against_complete_document(self):
        start, end = quote_span("one that we can understand", self.doc["text"])
        self.assertEqual(self.doc["text"][start:end], "one that we can understand")
        text = "said \u201clead-\n up\u201d to the\u2014end."
        start, end = quote_span("lead-up to the end", text)
        self.assertEqual(text[start:end], "lead-\n up\u201d to the\u2014end")
        self.assertEqual(principle_errors(self.principle, {self.doc["document_id"]: self.doc["text"]}), [])
        self.assertEqual(principle_errors(self.principle, {}), ["supporting_quotes[0]: quote not found in complete document"])

    def test_invalid_records_are_rejected_not_fatal(self):
        bad = dict(self.principle, principle_id="p2", supporting_quotes=[{"quote": "not in the letter at all"}])
        kept, report = partition([self.principle, bad], "principle_id", lambda p: principle_errors(p, {self.doc["document_id"]: self.doc["text"]}))
        self.assertEqual(kept, [self.principle])
        self.assertEqual(report["rejection_rate"], 0.5)
        self.assertEqual(report["rejected"][0]["principle_id"], "p2")

    def test_rubric_requires_framework_fields_and_source(self):
        rubric = {
            "rubric_id": "r1",
            "principle_id": "p1",
            "framework_id": "tradebank",
            "criterion": "The agent explains the business.",
            "applicability": {
                "trigger": "buy",
                "decision_types": ["buy"],
                "required_context": ["decision_rationale"],
            },
            "source": {
                "document_id": self.doc["document_id"],
                "exact_quotes": ["one that we can understand"],
            },
            "operationalization": {
                "observable_behavior": "A business explanation appears.",
                "pass_if": "The explanation identifies a concrete business mechanism.",
                "violate_if": "The agent buys without a business explanation.",
                "not_applicable_if": "No buy decision occurs.",
                "not_observable_if": "The rationale is absent.",
                "evidence_to_quote": "The decision rationale.",
            },
        }
        self.assertEqual(rubric_errors(rubric, {"p1"}, self.framework, {self.doc["document_id"]: self.doc["text"]}), [])

    def test_single_record_model_shape_is_normalized(self):
        self.assertEqual(as_records({"claim": "A rule."}, "principles"), [{"claim": "A rule."}])
        self.assertEqual(as_records({"criterion": "A behavior."}, "rubrics"), [{"criterion": "A behavior."}])


if __name__ == "__main__":
    unittest.main()
