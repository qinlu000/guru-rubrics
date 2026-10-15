"""Small deterministic checks for the two generated JSONL files."""
from __future__ import annotations

import re
from .io import quote_in_document


def _missing(record: dict, fields: list[str]) -> list[str]:
    return [field for field in fields if not record.get(field)]


def validate_principles(principles: list[dict], documents: dict[str, str]) -> dict:
    errors = []
    ids = set()
    for i, item in enumerate(principles):
        where = f"principles[{i}]"
        missing = _missing(item, ["principle_id", "document_id", "claim", "principle_type", "source_support", "supporting_quotes"])
        errors.extend({"where": where, "message": f"missing {field}"} for field in missing)
        if item.get("principle_id") in ids:
            errors.append({"where": where, "message": "duplicate principle_id"})
        ids.add(item.get("principle_id"))
        for j, evidence in enumerate(item.get("supporting_quotes", [])):
            if not isinstance(evidence, dict) or not evidence.get("quote") or not evidence.get("locator"):
                errors.append({"where": f"{where}.supporting_quotes[{j}]", "message": "quote and locator are required"})
            elif item.get("document_id") in documents and not quote_in_document(evidence["quote"], documents[item["document_id"]]):
                errors.append({"where": f"{where}.supporting_quotes[{j}]", "message": "quote not found in complete document"})
    return {"valid": not errors, "record_count": len(principles), "errors": errors}


def validate_rubrics(rubrics: list[dict], principles: list[dict], framework: dict, documents: dict[str, str]) -> dict:
    errors = []
    warnings = []
    principle_ids = {item.get("principle_id") for item in principles}
    fields = {item if isinstance(item, str) else item.get("name") for item in framework.get("canonical_event_fields", [])}
    ids = set()
    for i, item in enumerate(rubrics):
        where = f"rubrics[{i}]"
        errors.extend({"where": where, "message": f"missing {field}"} for field in _missing(item, ["rubric_id", "principle_id", "framework_id", "criterion", "applicability", "source", "operationalization"]))
        if item.get("rubric_id") in ids:
            errors.append({"where": where, "message": "duplicate rubric_id"})
        ids.add(item.get("rubric_id"))
        if item.get("principle_id") not in principle_ids:
            errors.append({"where": where, "message": "principle_id is not in the principle library"})
        if item.get("framework_id") != framework.get("framework_id"):
            errors.append({"where": where, "message": "framework_id does not match framework"})
        applicability = item.get("applicability", {})
        errors.extend({"where": where + ".applicability", "message": f"missing {field}"} for field in _missing(applicability, ["trigger", "decision_types", "required_context"]))
        for field in applicability.get("required_context", []):
            if fields and field not in fields:
                warnings.append({"where": where, "message": f"required_context not in framework: {field}"})
        operation = item.get("operationalization", {})
        errors.extend({"where": where + ".operationalization", "message": f"missing {field}"} for field in _missing(operation, ["observable_behavior", "pass_if", "violate_if", "not_applicable_if", "not_observable_if", "evidence_to_quote"]))
        if ";" in item.get("criterion", "") or re.search(r"\b(and|as well as)\b|并且|以及", item.get("criterion", ""), re.I):
            warnings.append({"where": where, "message": "criterion may contain more than one behavior"})
        source = item.get("source", {})
        for j, quote in enumerate(source.get("exact_quotes", [])):
            if source.get("document_id") in documents and not quote_in_document(quote, documents[source["document_id"]]):
                errors.append({"where": f"{where}.source.exact_quotes[{j}]", "message": "quote not found in complete document"})
    return {"valid": not errors, "record_count": len(rubrics), "errors": errors, "warnings": warnings}
