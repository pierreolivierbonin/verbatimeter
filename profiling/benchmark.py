import random
import string
import time

from verbatimeter import check

_SIZES = [
    (500, 100),
    (1000, 100),
    (2000, 100),
    (4000, 100),
    (1000, 200),
    (1000, 400),
    (1000, 800),
    (4000, 400),
]


def _words(n, rng):
    return " ".join(
        "".join(rng.choice(string.ascii_lowercase) for _ in range(rng.randint(3, 9)))
        for _ in range(n)
    )


def _best_ms(fn, repeats=5):
    fn()
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - start)
    return best * 1e3


def benchmark(sizes=_SIZES, repeats=5, seed=0):
    rng = random.Random(seed)
    rows = []
    for source_words, cand_words in sizes:
        source = _words(source_words, rng)
        candidate = _words(cand_words, rng)
        contiguous = _best_ms(lambda: check(candidate, source), repeats)
        subsequence = _best_ms(lambda: check(candidate, source, mode="subsequence"), repeats)
        rows.append(
            {
                "S": source_words,
                "C": cand_words,
                "SxC": source_words * cand_words,
                "contiguous_ms": contiguous,
                "subsequence_ms": subsequence,
                "contiguous_ns_per_SxC": contiguous * 1e6 / (source_words * cand_words),
            }
        )
    return rows


def main():
    header = f"{'S (source)':>10} {'C (cand)':>9} {'S*C':>10} {'contiguous':>12} {'subsequence':>13} {'ns/(S*C)':>10}"
    print(header)
    print("-" * len(header))
    for r in benchmark():
        print(
            f"{r['S']:>10} {r['C']:>9} {r['SxC']:>10} "
            f"{r['contiguous_ms']:>10.1f}ms {r['subsequence_ms']:>11.1f}ms "
            f"{r['contiguous_ns_per_SxC']:>10.1f}"
        )


if __name__ == "__main__":
    main()
