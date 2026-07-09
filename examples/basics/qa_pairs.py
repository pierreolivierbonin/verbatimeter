from pathlib import Path

SOURCE = (Path(__file__).resolve().parent / "source.txt").read_text(encoding="utf-8")


def print_source():
    print('Source: the abstract of "Attention Is All You Need" (source.txt)')
    print()


def success(pair):
    return f'{pair["before"]}"{pair["verbatim"]}"{pair["after"]}'


def failure(pair):
    return f'{pair["before"]}"{pair["altered"]}"{pair["after"]}'


pairs = [
    {
        "question": "What architecture do the authors propose, and what does it dispense with? Quote the paper.",
        "before": "The paper leads with its thesis. The abstract states: ",
        "verbatim": "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely",
        "altered": "We propose a new simple network architecture, the Transformer, based partly on attention mechanisms, dispensing with recurrence and convolutions entirely",
        "after": ", a clean break from the recurrent and convolutional models that came before.",
    },
    {
        "question": "What does the abstract claim about the Transformer's quality, parallelism, and training time? Quote it.",
        "before": "On results, the abstract reports: ",
        "verbatim": "Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train",
        "altered": "Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring considerably less time to train",
        "after": ", a combination the paper emphasizes throughout.",
    },
    {
        "question": "What English-to-German result did the model achieve? Quote the abstract exactly.",
        "before": "For the German benchmark, the abstract states: ",
        "verbatim": "Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles, by over 2 BLEU",
        "altered": "Our model achieves 28.7 BLEU on the WMT 2014 English-to-German translation task, improving over the existing best results, including ensembles, by over 2 BLEU",
        "after": ", a headline number the paper is remembered for.",
    },
    {
        "question": "What English-to-French BLEU score and training cost does the abstract report? Quote it.",
        "before": "For the French benchmark, the abstract reports that ",
        "verbatim": "our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs",
        "altered": "our model establishes a new single-model state-of-the-art BLEU score of 51.8 after training for 3.5 days on eight GPUs",
        "after": ", far below the training cost of prior systems.",
    },
    {
        "question": "Why do the authors scale the dot products? Quote the explanation.",
        "before": "Explaining the scaling factor, the authors write: ",
        "verbatim": "We suspect that for large values of d_k, the dot products grow large in magnitude, pushing the softmax function into regions where it has extremely small gradients",
        "altered": "We suspect that for large values of d_k, the dot products grow large in amplitude, pushing the softmax function into regions where it has extremely small gradients",
        "after": ", which is why they divide by the square root of the key dimension.",
    },
    {
        "question": "Why use more than one attention head? Quote the paper.",
        "before": "On the benefit of multiple heads, the paper states: ",
        "verbatim": "Multi-head attention allows the model to jointly attend to information from different representation subspaces at different positions",
        "altered": "Multi-head attention allows the model to separately attend to information from different representation dimensions at different positions",
        "after": ", something a single averaged head cannot do.",
    },
]
