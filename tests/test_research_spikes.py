import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.contradiction_spike import run_spike_eval as run_contradiction_benchmark
from research.stale_claim_detector import run_benchmark as run_stale_benchmark


def test_stale_claim_heuristic_benchmark():
    metrics = run_stale_benchmark()
    assert metrics["total_pages"] == 20
    assert metrics["precision"] >= 0.90
    assert metrics["recall"] >= 0.90
    assert metrics["f1"] >= 0.90


def test_contradiction_spike_benchmark():
    metrics = run_contradiction_benchmark()
    assert metrics["total_pairs"] == 10
    assert metrics["precision"] == 1.0  # 100% precision on scalar conflict corpus
    assert metrics["recall"] == 1.0     # 100% recall on scalar conflict corpus
    assert metrics["f1"] == 1.0
