#!/usr/bin/env python3
"""
🔬 Contradiction Detector Spike v0 — Research Spike (Issue #7)
Problem Definition for v0:
Detecting contradictory factual assertions across wiki pages where two notes
reference the exact same Entity (e.g., 'API Gateway', 'Postgres Cluster', 'Token Expiry')
but make conflicting scalar assertions (e.g. conflicting ports, dates, or version numbers).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


@dataclass
class EntityClaim:
    entity: str
    property_name: str
    value: str
    source_page: str


@dataclass
class ContradictionFinding:
    entity: str
    property_name: str
    page_a: str
    val_a: str
    page_b: str
    val_b: str


class ContradictionDetectorV0:
    """
    Lightweight rule-based contradiction detector spike for scalar facts.
    """
    PATTERNS = [
        # Entity runs on port N: "Hermes runs on port 11435"
        (r"\b([A-Za-z0-9_-]+)\s+(?:runs\s+on\s+port|listens\s+on\s+port|port)\s*[:=]?\s*(\d+)\b", "port"),
        # Entity version is X: "Postgres version is 16"
        (r"\b([A-Za-z0-9_-]+)\s+(?:version|v)\s*[:=]?\s*(\d+(?:\.\d+)?)\b", "version"),
        # Entity timeout is Ns: "API timeout is 30s"
        (r"\b([A-Za-z0-9_-]+)\s+(?:timeout)\s*[:=]?\s*(\d+s?)\b", "timeout"),
    ]

    def extract_claims(self, page_id: str, text: str) -> List[EntityClaim]:
        claims = []
        for pat_str, prop_name in self.PATTERNS:
            rx = re.compile(pat_str, re.IGNORECASE)
            for m in rx.finditer(text):
                ent = m.group(1).lower()
                val = m.group(2).lower()
                claims.append(EntityClaim(entity=ent, property_name=prop_name, value=val, source_page=page_id))
        return claims

    def detect_contradictions(self, pages: List[Dict[str, str]]) -> List[ContradictionFinding]:
        findings = []
        registry: Dict[Tuple[str, str], EntityClaim] = {}

        for p in pages:
            claims = self.extract_claims(p["id"], p["content"])
            for c in claims:
                key = (c.entity, c.property_name)
                if key in registry:
                    existing = registry[key]
                    if existing.value != c.value and existing.source_page != c.source_page:
                        findings.append(ContradictionFinding(
                            entity=c.entity,
                            property_name=c.property_name,
                            page_a=existing.source_page,
                            val_a=existing.value,
                            page_b=c.source_page,
                            val_b=c.value
                        ))
                else:
                    registry[key] = c
        return findings


# 20-Page Hand-Labeled Contradiction Evaluation Corpus
# 10 pairs: 5 contradictory pairs (10 pages) + 5 harmonious pairs (10 pages)
CORPUS_20_PAGES: List[Dict[str, Any]] = [
    # Pair 1: Port conflict (Contradiction)
    {"id": "doc_01", "content": "Hermes runs on port 11435 for local inference.", "pair_id": 1, "is_contradiction": True},
    {"id": "doc_02", "content": "Hermes runs on port 8080 according to old notes.", "pair_id": 1, "is_contradiction": True},
    # Pair 2: Postgres Version conflict (Contradiction)
    {"id": "doc_03", "content": "Postgres version 16 is deployed in production.", "pair_id": 2, "is_contradiction": True},
    {"id": "doc_04", "content": "Postgres version 14 is running across all databases.", "pair_id": 2, "is_contradiction": True},
    # Pair 3: Timeout conflict (Contradiction)
    {"id": "doc_05", "content": "Gateway timeout 30s enforced.", "pair_id": 3, "is_contradiction": True},
    {"id": "doc_06", "content": "Gateway timeout 60s configured.", "pair_id": 3, "is_contradiction": True},
    # Pair 4: Qdrant Port conflict (Contradiction)
    {"id": "doc_07", "content": "Qdrant port 6333 is open.", "pair_id": 4, "is_contradiction": True},
    {"id": "doc_08", "content": "Qdrant port 6334 is open.", "pair_id": 4, "is_contradiction": True},
    # Pair 5: Redis version conflict (Contradiction)
    {"id": "doc_09", "content": "Redis version 7 is in use.", "pair_id": 5, "is_contradiction": True},
    {"id": "doc_10", "content": "Redis version 6 is in use.", "pair_id": 5, "is_contradiction": True},
    # Pair 6: Harmonious Port agreement
    {"id": "doc_11", "content": "Cockpit port 8888 is active.", "pair_id": 6, "is_contradiction": False},
    {"id": "doc_12", "content": "Cockpit port 8888 serves the dashboard.", "pair_id": 6, "is_contradiction": False},
    # Pair 7: Harmonious Version agreement
    {"id": "doc_13", "content": "Python version 3.12 required.", "pair_id": 7, "is_contradiction": False},
    {"id": "doc_14", "content": "Python version 3.12 tested.", "pair_id": 7, "is_contradiction": False},
    # Pair 8: Distinct entities
    {"id": "doc_15", "content": "OpenClaw port 18790 running.", "pair_id": 8, "is_contradiction": False},
    {"id": "doc_16", "content": "Paperclip port 3100 running.", "pair_id": 8, "is_contradiction": False},
    # Pair 9: Non-scalar descriptions
    {"id": "doc_17", "content": "Architecture emphasizes modularity.", "pair_id": 9, "is_contradiction": False},
    {"id": "doc_18", "content": "Modularity improves maintainability.", "pair_id": 9, "is_contradiction": False},
    # Pair 10: Harmonious timeout
    {"id": "doc_19", "content": "Worker timeout 120s set.", "pair_id": 10, "is_contradiction": False},
    {"id": "doc_20", "content": "Worker timeout 120s confirmed.", "pair_id": 10, "is_contradiction": False},
]


def run_spike_eval() -> Dict[str, Any]:
    detector = ContradictionDetectorV0()
    # Group by pair_id to evaluate pair-level accuracy
    pairs: Dict[int, List[Dict[str, Any]]] = {}
    for p in CORPUS_20_PAGES:
        pairs.setdefault(p["pair_id"], []).append(p)

    tp = fp = tn = fn = 0
    for pid, pair_pages in pairs.items():
        findings = detector.detect_contradictions(pair_pages)
        predicted = len(findings) > 0
        actual = pair_pages[0]["is_contradiction"]

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
        "total_pairs": len(pairs),
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


if __name__ == "__main__":
    metrics = run_spike_eval()
    print("=== Contradiction Detector Spike v0 Benchmark ===")
    print(f"Pairs: {metrics['total_pairs']} | TP: {metrics['tp']}, FP: {metrics['fp']}, TN: {metrics['tn']}, FN: {metrics['fn']}")
    print(f"Precision: {metrics['precision']*100:.1f}% | Recall: {metrics['recall']*100:.1f}% | F1: {metrics['f1']:.4f}")
