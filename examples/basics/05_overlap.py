from verbatimeter import check_answer, render_result
from qa_pairs import SOURCE, print_source

print_source()
print("No quotation marks anywhere. In the default scope, verbatimeter scans the")
print("WHOLE text for runs of >= ngram words copied verbatim from the source.")
print()


def overlap(label, text, ngram=3):
    print(f"##### {label}  (ngram={ngram})")
    result = check_answer(text, SOURCE, ngram=ngram)
    print(render_result(result))
    print(f"    verbatim fragments: {result.results[0].fragments}")
    print()


extractive = (
    "The dominant sequence transduction models are based on complex recurrent or "
    "convolutional neural networks in an encoder-decoder configuration, but the "
    "Transformer is based solely on attention mechanisms, dispensing with recurrence "
    "and convolutions entirely, and it connects the encoder and decoder through an "
    "attention mechanism."
)
abstractive = (
    "Rather than stacking convolutions or recurrent cells, their architecture leans "
    "wholly on attending over positions, which they report trains faster and reaches "
    "higher translation quality than earlier systems on standard benchmarks."
)

overlap("Extractive summary (lifts phrases straight from the paper)", extractive)
overlap("Abstractive summary (paraphrased in the reader's own words)", abstractive)

print("The ngram threshold sets the minimum verbatim run length that counts.")
short_run = "it relies on an attention mechanism throughout the network"
overlap("A borderline 3-word overlap, counted at ngram=3", short_run, ngram=3)
overlap("The same text at ngram=4 - the 3-word run no longer counts", short_run, ngram=4)
