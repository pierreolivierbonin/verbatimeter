import string
import unicodedata

_STRIP = set(string.punctuation)


def clean_text(text: str) -> list[str]:
    text = unicodedata.normalize("NFC", text)
    cleaned = "".join(
        ch for ch in text if ch not in _STRIP and not unicodedata.category(ch).startswith("P")
    ).casefold()
    return cleaned.split()


def calculate_rouge_L_score(
    reference_words: list[str], candidate_words: list[str], lcs_length: int
) -> float:
    precision = lcs_length / len(candidate_words) if candidate_words else 0
    recall = lcs_length / len(reference_words) if reference_words else 0

    if precision + recall > 0:
        rougeL_score = 2 * (precision * recall) / (precision + recall)
    else:
        rougeL_score = 0

    return rougeL_score


def calculate_LCS_and_rouge_L_score(reference: str, candidate: str) -> float:
    reference_words = clean_text(reference)
    candidate_words = clean_text(candidate)

    if not reference_words or not candidate_words:
        return 0.0

    return calculate_rouge_L_score(
        reference_words, candidate_words, _lcs_length(reference_words, candidate_words)
    )


def _lcs_length(reference_words: list[str], candidate_words: list[str]) -> int:
    n = len(candidate_words)

    prev = [0] * (n + 1)
    for ref_word in reference_words:
        cur = [0] * (n + 1)
        for j, cand_word in enumerate(candidate_words, 1):
            if ref_word == cand_word:
                cur[j] = prev[j - 1] + 1
            else:
                cur[j] = max(prev[j], cur[j - 1])
        prev = cur
    return prev[n]


def lcs_alignment(
    reference_words: list[str], candidate_words: list[str]
) -> tuple[int, list[int], list[int]]:
    m, n = len(reference_words), len(candidate_words)

    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i, ref_word in enumerate(reference_words, 1):
        for j, cand_word in enumerate(candidate_words, 1):
            if ref_word == cand_word:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    i, j = m, n
    ref_idx, cand_idx = [], []
    while i > 0 and j > 0:
        if reference_words[i - 1] == candidate_words[j - 1]:
            ref_idx.append(i - 1)
            cand_idx.append(j - 1)
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    ref_idx.reverse()
    cand_idx.reverse()
    return dp[m][n], ref_idx, cand_idx


def contiguous_alignment(
    reference_words: list[str], candidate_words: list[str], ngram: int = 3
) -> tuple[list[int], list[int]]:
    m, n = len(reference_words), len(candidate_words)

    prev = [0] * (n + 1)
    ref_matched, cand_matched = set(), set()

    for i, ref_word in enumerate(reference_words, 1):
        cur = [0] * (n + 1)
        for j, cand_word in enumerate(candidate_words, 1):
            if ref_word != cand_word:
                continue
            cur[j] = prev[j - 1] + 1
            extends = i < m and j < n and reference_words[i] == candidate_words[j]
            if cur[j] >= ngram and not extends:
                for k in range(cur[j]):
                    ref_matched.add(i - 1 - k)
                    cand_matched.add(j - 1 - k)
        prev = cur

    return sorted(ref_matched), sorted(cand_matched)


def word_char_spans(text: str) -> list[tuple[int, int]]:
    spans = []
    pos = 0
    length = len(text)
    while pos < length:
        while pos < length and text[pos].isspace():
            pos += 1
        if pos >= length:
            break
        start = pos
        while pos < length and not text[pos].isspace():
            pos += 1
        if clean_text(text[start:pos]):
            spans.append((start, pos))
    return spans


def segment_span(text: str, clean_indices: list[int]) -> str:
    idx = sorted(set(clean_indices))
    if not idx:
        return ""
    spans = word_char_spans(text)
    return text[spans[idx[0]][0] : spans[idx[-1]][1]]
