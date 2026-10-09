import unittest
from pathlib import Path

from buffett_corpus.pipeline.cli import as_records
from buffett_corpus.pipeline.io import document_record, quote_in_document
from buffett_corpus.pipeline.validation import validate_principles, validate_rubrics


ROOT = Path(__file__).resolve().parents[1]


class PipelineValidationTests(unittest.TestCase):
    def setUp(self):
        self.doc = document_record(ROOT / "buffett_corpus/processed/1977.txt", "Warren Buffett")
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
            "supporting_quotes": [{"quote": "one that we can understand", "locator": "line 264"}],
        }

    def test_source_quote_is_checked_against_complete_document(self):
        self.assertTrue(quote_in_document("one that we can understand", self.doc["text"]))
        report = validate_principles([self.principle], documents={self.doc["document_id"]: self.doc["text"]})
        self.assertTrue(report["valid"])

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
        report = validate_rubrics(
            [rubric],
            principles=[self.principle],
            framework=self.framework,
            documents={self.doc["document_id"]: self.doc["text"]},
        )
        self.assertTrue(report["valid"])

    def test_single_record_model_shape_is_normalized(self):
        self.assertEqual(as_records({"claim": "A rule."}, "principles"), [{"claim": "A rule."}])
        self.assertEqual(as_records({"criterion": "A behavior."}, "rubrics"), [{"criterion": "A behavior."}])


if __name__ == "__main__":
    unittest.main()
