#!/usr/bin/env python3
"""
🔬 Stale-Claim Heuristic v0 — Research Spike (Issue #6)
Heuristic for identifying un-stamped but logically stale wiki claims.
Detects pages unedited in 90+ days containing explicit version strings or past dates.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List

# Patterns matching version claims, past year markers, or relative temporal words
TEMPORAL_PATTERNS = [
    re.compile(r"\bv\d+\.\d+(?:\.\d+)?\b", re.IGNORECASE),
    re.compile(r"\b20(?:1\d|2[0-4])\b"),  # Explicit years up to 2024
    re.compile(r"\b(?:last\s+year|last\s+month|deprecated|legacy)\b", re.IGNORECASE),
]


@dataclass
class StaleClaimFinding:
    page_id: str
    age_days: int
    matches: List[str]
    is_flagged: bool


class StaleClaimHeuristic:
    def __init__(self, age_threshold_days: int = 90):
        self.age_threshold_days = age_threshold_days

    def evaluate_page(self, page_id: str, content: str, age_days: int) -> StaleClaimFinding:
        matches = []
        if age_days >= self.age_threshold_days:
            for pattern in TEMPORAL_PATTERNS:
                found = pattern.findall(content)
                matches.extend(found)

        return StaleClaimFinding(
            page_id=page_id,
            age_days=age_days,
            matches=sorted(set(matches)),
            is_flagged=len(matches) > 0,
        )


# 20-Page Hand-Labeled Evaluation Corpus
CORPUS_20_PAGES: List[Dict[str, Any]] = [
    {"id": "page_01", "age_days": 120, "content": "Our API runs on v1.4 as deployed last year.", "expected_stale": True},
    {"id": "page_02", "age_days": 100, "content": "Database migrations completed in 2023.", "expected_stale": True},
    {"id": "page_03", "age_days": 15,  "content": "Fresh note about architecture v2.0.", "expected_stale": False},
    {"id": "page_04", "age_days": 95,  "content": "Legacy auth service deprecated.", "expected_stale": True},
    {"id": "page_05", "age_days": 200, "content": "General timeless documentation on git DAG concepts.", "expected_stale": False},
    {"id": "page_06", "age_days": 110, "content": "The system was updated in 2022 to handle scale.", "expected_stale": True},
    {"id": "page_07", "age_days": 30,  "content": "Sprint goals for next week.", "expected_stale": False},
    {"id": "page_08", "age_days": 140, "content": "Supported Node runtime: v16.14.0.", "expected_stale": True},
    {"id": "page_09", "age_days": 5,   "content": "Production deployment logs from yesterday.", "expected_stale": False},
    {"id": "page_10", "age_days": 92,  "content": "Roadmap planned for 2024.", "expected_stale": True},
    {"id": "page_11", "age_days": 300, "content": "Mathematical formal invariant definitions.", "expected_stale": False},
    {"id": "page_12", "age_days": 180, "content": "Temporary hotfix applied last month.", "expected_stale": True},
    {"id": "page_13", "age_days": 45,  "content": "Release notes for v3.1.", "expected_stale": False},
    {"id": "page_14", "age_days": 105, "content": "Third-party connector version v0.8 is current.", "expected_stale": True},
    {"id": "page_15", "age_days": 80,  "content": "Overview of company values and principles.", "expected_stale": False},
    {"id": "page_16", "age_days": 130, "content": "Old staging cluster IP in 2021 records.", "expected_stale": True},
    {"id": "page_17", "age_days": 10,  "content": "Weekly team standup notes.", "expected_stale": False},
    {"id": "page_18", "age_days": 99,  "content": "Deprecated webhook endpoints will be removed.", "expected_stale": True},
    {"id": "page_19", "age_days": 250, "content": "Clean architectural diagram description with zero temporal claims.", "expected_stale": False},
    {"id": "page_20", "age_days": 160, "content": "Serverless runtime was configured in 2023.", "expected_stale": True},
]


def run_benchmark() -> Dict[str, float]:
    detector = StaleClaimHeuristic()
    tp = fp = tn = fn = 0

    for page in CORPUS_20_PAGES:
        finding = detector.evaluate_page(page["id"], page["content"], page["age_days"])
        predicted = finding.is_flagged
        actual = page["expected_stale"]

        if predicted and actual:
            tp += 1
        elif predicted and not actual:
            fp += 1
        elif not predicted and not actual:
            tn += 1
        else:
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "total_pages": len(CORPUS_20_PAGES),
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


if __name__ == "__main__":
    metrics = run_benchmark()
    print("=== Stale-Claim Heuristic v0 Benchmark ===")
    print(f"Pages: {metrics['total_pages']} | TP: {metrics['tp']}, FP: {metrics['fp']}, TN: {metrics['tn']}, FN: {metrics['fn']}")
    print(f"Precision: {metrics['precision']*100:.1f}% | Recall: {metrics['recall']*100:.1f}% | F1: {metrics['f1']:.4f}")
