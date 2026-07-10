import argparse
import inspect
import json
import os
import re
import sys
from collections.abc import Callable, Iterator
from dataclasses import asdict, dataclass, field
from functools import cache, wraps
from typing import Literal, TextIO

from .align import (
    calculate_LCS_and_rouge_L_score,
    clean_text,
    contiguous_alignment,
    lcs_alignment,
    segment_span,
)

Mode = Literal["contiguous", "subsequence"]
Scope = Literal["all", "quotes"]
TokenCounter = Callable[[str], int] | None


@cache
def _bundled_cl100k_base():
    import base64
    import gzip
    from importlib.resources import files

    import tiktoken

    data = gzip.decompress(
        files("verbatimeter").joinpath("data/cl100k_base.tiktoken.gz").read_bytes()
    )
    ranks = {
        base64.b64decode(token): int(rank)
        for token, rank in (line.split() for line in data.splitlines() if line)
    }
    return tiktoken.Encoding(
        name="cl100k_base",
        pat_str=r"""'(?i:[sdmt]|ll|ve|re)|[^\r\n\p{L}\p{N}]?+\p{L}++|\p{N}{1,3}+| ?[^\s\p{L}\p{N}]++[\r\n]*+|\s++$|\s*[\r\n]|\s+(?!\S)|\s""",
        mergeable_ranks=ranks,
        special_tokens={
            "<|endoftext|>": 100257,
            "<|fim_prefix|>": 100258,
            "<|fim_middle|>": 100259,
            "<|fim_suffix|>": 100260,
            "<|endofprompt|>": 100276,
        },
    )


def _tiktoken_count(text: str) -> int:
    return len(_bundled_cl100k_base().encode(text))


_QUOTE_RE = re.compile(
    r'(?<!\d)"([^"]*)"'
    r"|“([^”]*)”"
    r"|«\s*([^»]*?)\s*»"
    r"|„([^“”]*)[“”]"
)


def extract_quotes(answer: str) -> list[str]:
    seen = set()
    quotes = []
    for groups in _QUOTE_RE.findall(answer):
        quote = next((g for g in groups if g), "").strip()
        if not clean_text(quote) or quote in seen:
            continue
        seen.add(quote)
        quotes.append(quote)
    return quotes


@dataclass
class WordSpan:
    text: str
    verbatim: bool | None


@dataclass
class Result:
    text: str
    source_segment: str
    words: list[WordSpan]
    fragments: list[str]
    rouge_l: float
    matched_ratio: float
    differing_tokens: int
    total_tokens: int

    @property
    def longest_fragment(self) -> int:
        return max((len(clean_text(f)) for f in self.fragments), default=0)


@dataclass
class CheckResult:
    scope: str
    results: list[Result] = field(default_factory=list)

    @property
    def total_differing_tokens(self) -> int:
        return sum(r.differing_tokens for r in self.results)

    @property
    def mean_rouge_l(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.rouge_l for r in self.results) / len(self.results)


def _align(
    source_words: list[str], candidate_words: list[str], mode: Mode, ngram: int
) -> tuple[list[int], list[int]]:
    if mode == "contiguous":
        return contiguous_alignment(source_words, candidate_words, ngram)
    if mode == "subsequence":
        _, ref_idx, cand_idx = lcs_alignment(source_words, candidate_words)
        return ref_idx, cand_idx
    raise ValueError(f"unknown mode: {mode!r}")


def _word_spans(text: str, matched: set[int]) -> list[WordSpan]:
    spans = []
    clean_idx = 0
    for token in text.split():
        if clean_text(token):
            spans.append(WordSpan(token, clean_idx in matched))
            clean_idx += 1
        else:
            spans.append(WordSpan(token, None))
    return spans


def _fragments(words: list[WordSpan]) -> list[str]:
    fragments, run, pending = [], [], []
    for span in words:
        if span.verbatim is True:
            if run and pending:
                run.extend(pending)
            pending = []
            run.append(span.text)
        elif span.verbatim is None:
            if run:
                pending.append(span.text)
        else:
            if run:
                fragments.append(" ".join(run))
            run, pending = [], []
    if run:
        fragments.append(" ".join(run))
    return fragments


def check(
    text: str,
    source: str,
    *,
    ngram: int = 3,
    mode: Mode = "contiguous",
    count_tokens: TokenCounter = None,
) -> Result:
    if ngram < 3:
        raise ValueError(f"ngram must be >= 3, got {ngram}")
    counter = count_tokens or _tiktoken_count
    candidate_words = clean_text(text)
    ref_idx, cand_idx = _align(clean_text(source), candidate_words, mode, ngram)
    matched = set(cand_idx)

    words = _word_spans(text, matched)
    segment = segment_span(source, ref_idx)
    differing_text = " ".join(w for k, w in enumerate(candidate_words) if k not in matched)

    return Result(
        text=text,
        source_segment=segment,
        words=words,
        fragments=_fragments(words),
        rouge_l=calculate_LCS_and_rouge_L_score(segment, text),
        matched_ratio=len(matched) / len(candidate_words) if candidate_words else 0.0,
        differing_tokens=counter(differing_text) if differing_text else 0,
        total_tokens=counter(text) if text else 0,
    )


def check_answer(
    answer: str,
    source: str,
    *,
    scope: Scope = "all",
    ngram: int = 3,
    mode: Mode = "contiguous",
    count_tokens: TokenCounter = None,
) -> CheckResult:
    if scope == "all":
        candidates = [answer.strip()] if answer.strip() else []
    elif scope == "quotes":
        candidates = extract_quotes(answer)
    else:
        raise ValueError(f"unknown scope: {scope!r}")
    results = [
        check(c, source, ngram=ngram, mode=mode, count_tokens=count_tokens) for c in candidates
    ]
    return CheckResult(scope=scope, results=results)


_RESET = "\033[0m"
_DIM = "\033[2m"

_PALETTES = {
    "classic": ("\033[32m", "\033[31m"),
    "colorblind": ("\033[34m", "\033[38;5;208m"),
    "neon": ("\033[92m", "\033[95m"),
    "mono": ("\033[1m", "\033[7m"),
}


def _resolve_color(use_color: bool | None, stream: TextIO | None = None) -> bool:
    if use_color is not None:
        return use_color
    stream = stream or sys.stdout
    return stream.isatty() and os.environ.get("NO_COLOR") is None


def _paint(text: str, code: str, use_color: bool) -> str:
    return f"{code}{text}{_RESET}" if use_color and code else text


def render_words(words: list[WordSpan], use_color: bool, palette: str = "classic") -> str:
    matched, differing = _PALETTES[palette]
    out = []
    for span in words:
        if span.verbatim is True:
            out.append(_paint(span.text, matched, use_color))
        elif span.verbatim is False:
            out.append(_paint(span.text, differing, use_color))
        else:
            out.append(span.text)
    return " ".join(out)


def render_result(
    check_result: CheckResult, use_color: bool | None = None, stream=None, palette: str = "classic"
) -> str:
    use_color = _resolve_color(use_color, stream)
    scope = check_result.scope
    if not check_result.results:
        return "No quotations found to check." if scope == "quotes" else "Empty input."

    lines = []
    for i, r in enumerate(check_result.results, 1):
        label = f"[{i}] " if scope == "quotes" else ""
        lines.append(label + render_words(r.words, use_color, palette))
        stats = (
            f"    matched={r.matched_ratio:.0%}  differing_tokens={r.differing_tokens}/{r.total_tokens}"
            f"  longest_run={r.longest_fragment}  rouge_l={r.rouge_l:.3f}"
        )
        lines.append(_paint(stats, _DIM, use_color))
        lines.append("")

    summary = (
        f"{len(check_result.results)} result(s)  "
        f"total_differing_tokens={check_result.total_differing_tokens}  "
        f"mean_rouge_l={check_result.mean_rouge_l:.3f}"
    )
    lines.append(_paint(summary, _DIM, use_color))
    return "\n".join(lines)


class AnnotatedAnswer(str):
    result: CheckResult

    def __new__(cls, value: str, result: CheckResult):
        obj = super().__new__(cls, value)
        obj.result = result
        return obj


class AnnotatedStream:
    result: CheckResult | None

    def __init__(self, chunks: Iterator[str], source: str, **config):
        self._chunks = chunks
        self._source = source
        self._config = config
        self.result = None

    def __iter__(self) -> Iterator[str]:
        cfg = self._config
        live = cfg["print_stats"] and cfg["scope"] == "all" and cfg["mode"] == "contiguous"
        out = cfg["file"] or sys.stdout
        use_color = _resolve_color(cfg["use_color"], out)
        hold = cfg["ngram"] - 1
        answer = ""
        printed = 0
        for chunk in self._chunks:
            answer += chunk
            yield chunk
            head = answer[: answer.rfind(" ") + 1]
            if not live or not head.strip():
                continue
            words = check(
                head, self._source, ngram=cfg["ngram"], count_tokens=cfg["count_tokens"]
            ).words
            clean = [k for k, span in enumerate(words) if span.verbatim is not None]
            boundary = clean[-hold] if len(clean) > hold else 0
            if boundary > printed:
                print(
                    render_words(words[printed:boundary], use_color, cfg["palette"]),
                    end=" ",
                    file=out,
                    flush=True,
                )
                printed = boundary
        self.result = check_answer(
            answer,
            self._source,
            scope=cfg["scope"],
            ngram=cfg["ngram"],
            mode=cfg["mode"],
            count_tokens=cfg["count_tokens"],
        )
        if live:
            words = check(
                answer, self._source, ngram=cfg["ngram"], count_tokens=cfg["count_tokens"]
            ).words
            print(render_words(words[printed:], use_color, cfg["palette"]), file=out)
            for r in self.result.results:
                stats = (
                    f"    matched={r.matched_ratio:.0%}  differing_tokens={r.differing_tokens}/{r.total_tokens}"
                    f"  longest_run={r.longest_fragment}  rouge_l={r.rouge_l:.3f}"
                )
                print(_paint(stats, _DIM, use_color), file=out)
        elif cfg["print_stats"]:
            print(
                render_result(
                    self.result, use_color=cfg["use_color"], stream=out, palette=cfg["palette"]
                ),
                file=out,
            )


def verify(
    source: str | None = None,
    *,
    source_arg: str = "source",
    scope: Scope = "all",
    ngram: int = 3,
    mode: Mode = "contiguous",
    count_tokens: TokenCounter = None,
    use_color: bool | None = None,
    palette: str = "classic",
    print_stats: bool = True,
    file: TextIO | None = None,
):
    def decorator(fn):
        sig = inspect.signature(fn)

        @wraps(fn)
        def wrapper(*args, **kwargs):
            answer = fn(*args, **kwargs)
            arguments = sig.bind(*args, **kwargs).arguments
            resolved = arguments.get(source_arg, kwargs.get(source_arg, source))
            if resolved is None:
                return answer
            if isinstance(answer, Iterator):
                return AnnotatedStream(
                    answer,
                    resolved,
                    scope=scope,
                    ngram=ngram,
                    mode=mode,
                    count_tokens=count_tokens,
                    use_color=use_color,
                    palette=palette,
                    print_stats=print_stats,
                    file=file,
                )
            if not isinstance(answer, str):
                return answer
            result = check_answer(
                answer,
                resolved,
                scope=scope,
                ngram=ngram,
                mode=mode,
                count_tokens=count_tokens,
            )
            if print_stats:
                stream = file or sys.stdout
                print(
                    render_result(result, use_color=use_color, stream=stream, palette=palette),
                    file=stream,
                )
            return AnnotatedAnswer(answer, result)

        return wrapper

    return decorator


def _read(literal: str | None, path: str | None) -> str:
    if literal is not None:
        return literal
    assert path is not None
    if path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="verbatimeter",
        description="Measure how much of a text is reproduced verbatim from a source, "
        "word-for-word, in runs of at least --ngram words.",
    )
    from . import __version__

    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    source_group = p.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--source", help="the source as literal text")
    source_group.add_argument("--source-file", help="path to read the source from (- for stdin)")
    answer_group = p.add_mutually_exclusive_group(required=True)
    answer_group.add_argument("--answer", help="the answer as literal text")
    answer_group.add_argument("--answer-file", help="path to read the answer from (- for stdin)")
    p.add_argument(
        "--quotes",
        action="store_true",
        help='check only the quoted spans ("…", “…”, «…», „…“) instead of the whole text',
    )
    p.add_argument("--subsequence", action="store_true")
    p.add_argument("--ngram", type=int, default=3)
    p.add_argument("--palette", choices=sorted(_PALETTES), default="classic")
    p.add_argument("--no-color", action="store_true")
    p.add_argument("--json", action="store_true")
    p.add_argument(
        "--fail",
        action="store_true",
        help="with --quotes: exit non-zero when any quotation differs or none are found",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    source = _read(args.source, args.source_file)
    answer = _read(args.answer, args.answer_file)

    scope = "quotes" if args.quotes else "all"
    mode = "subsequence" if args.subsequence else "contiguous"
    result = check_answer(answer, source, scope=scope, ngram=args.ngram, mode=mode)

    if args.json:
        payload = asdict(result)
        payload["total_differing_tokens"] = result.total_differing_tokens
        payload["mean_rouge_l"] = result.mean_rouge_l
        for r_dict, r in zip(payload["results"], result.results):
            r_dict["longest_fragment"] = r.longest_fragment
        print(json.dumps(payload, indent=2))
    else:
        print(
            render_result(result, use_color=False if args.no_color else None, palette=args.palette)
        )

    failed = not result.results or result.total_differing_tokens > 0
    gate = scope == "quotes" and args.fail and failed
    return 1 if gate else 0
