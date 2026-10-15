"""Deterministic per-record checks; records that fail are rejected, not repaired."""
from __future__ import annotations

import re
from typing import Callable

from .io import quote_in_document

PRINCIPLE_FIELDS = ["principle_id", "document_id", "claim", "principle_type", "source_support", "supporting_quotes"]
RUBRIC_FIELDS = ["rubric_id", "principle_id", "framework_id", "criterion", "applicability", "source", "operationalization"]
APPLICABILITY_FIELDS = ["trigger", "decision_types", "required_context"]
OPERATIONALIZATION_FIELDS = ["observable_behavior", "pass_if", "violate_if", "not_applicable_if", "not_observable_if", "evidence_to_quote"]


def _missing(record: dict, fields: list[str], where: str = "") -> list[str]:
    return [f"missing {where}{field}" for field in fields if not record.get(field)]


def principle_errors(item: dict, documents: dict[str, str]) -> list[str]:
    errors = _missing(item, PRINCIPLE_FIELDS)
    document = documents.get(item.get("document_id"), "")
    for j, evidence in enumerate(item.get("supporting_quotes", [])):
        if not isinstance(evidence, dict) or not evidence.get("quote") or not evidence.get("locator"):
            errors.append(f"supporting_quotes[{j}]: quote and locator are required")
        elif not quote_in_document(evidence["quote"], document):
            errors.append(f"supporting_quotes[{j}]: quote not found in complete document")
    return errors


def rubric_errors(item: dict, principle_ids: set[str], framework: dict, documents: dict[str, str]) -> list[str]:
    errors = _missing(item, RUBRIC_FIELDS)
    errors += _missing(item.get("applicability", {}), APPLICABILITY_FIELDS, "applicability.")
    errors += _missing(item.get("operationalization", {}), OPERATIONALIZATION_FIELDS, "operationalization.")
    if item.get("principle_id") not in principle_ids:
        errors.append("principle_id is not in the principle library")
    if item.get("framework_id") != framework["framework_id"]:
        errors.append("framework_id does not match framework")
    source = item.get("source", {})
    document = documents.get(source.get("document_id"), "")
    for j, quote in enumerate(source.get("exact_quotes", [])):
        if not quote_in_document(quote, document):
            errors.append(f"source.exact_quotes[{j}]: quote not found in complete document")
    return errors


def rubric_warnings(item: dict, framework: dict) -> list[str]:
    fields = set(framework["canonical_event_fields"])
    warnings = [f"required_context not in framework: {f}" for f in item.get("applicability", {}).get("required_context", []) if f not in fields]
    if ";" in item.get("criterion", "") or re.search(r"\b(and|as well as)\b|并且|以及", item.get("criterion", ""), re.I):
        warnings.append("criterion may contain more than one behavior")
    return warnings


def partition(records: list[dict], id_field: str, errors: Callable[[dict], list[str]]) -> tuple[list[dict], dict]:
    """Split records into accepted ones and a rejection report."""
    accepted, rejected = [], []
    for record in records:
        found = errors(record)
        if found:
            rejected.append({id_field: record.get(id_field), "errors": found})
        else:
            accepted.append(record)
    return accepted, {
        "record_count": len(records),
        "accepted": len(accepted),
        "rejection_rate": len(rejected) / len(records) if records else 0.0,
        "rejected": rejected,
    }
