from .align import contiguous_alignment, lcs_alignment
from .core import (
    AnnotatedAnswer,
    AnnotatedStream,
    CheckResult,
    Result,
    WordSpan,
    check,
    check_answer,
    extract_quotes,
    main,
    render_result,
    render_words,
    verify,
)

__version__ = "0.1.2.post1"

__all__ = [
    "check",
    "check_answer",
    "verify",
    "render_result",
    "render_words",
    "extract_quotes",
    "lcs_alignment",
    "contiguous_alignment",
    "CheckResult",
    "Result",
    "WordSpan",
    "AnnotatedAnswer",
    "AnnotatedStream",
    "main",
]
