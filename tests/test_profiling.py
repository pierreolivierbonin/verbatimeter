import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "profiling"))

import benchmark


def test_benchmark_runs_against_real_code():
    rows = benchmark.benchmark(sizes=[(200, 50), (400, 50)], repeats=1)
    assert len(rows) == 2
    for r in rows:
        assert r["SxC"] == r["S"] * r["C"]
        assert r["contiguous_ms"] >= 0
        assert r["subsequence_ms"] >= 0
        assert r["contiguous_ns_per_SxC"] > 0
