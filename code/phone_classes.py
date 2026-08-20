"""Phone inventory for 'The big pig sat on a thick sheet.' and its class labels."""

SENTENCE = "The big pig sat on a thick sheet."

WORDS = ["the", "big", "pig", "sat", "on", "a", "thick", "sheet"]

# phones per word, in order
WORD_PHONES = [
    ["ð", "ə"],
    ["b", "ɪ", "ɡ"],
    ["p", "ɪ", "ɡ"],
    ["s", "æ", "t"],
    ["ɒ", "n"],
    ["ə"],
    ["θ", "ɪ", "k"],
    ["ʃ", "iː", "t"],
]

PHONES = [p for w in WORD_PHONES for p in w]

SIL = "sil"

VOWELS = {"ə", "ɪ", "æ", "ɒ", "iː"}

# voiced in the citation form of this sentence
VOICED = VOWELS | {"ð", "b", "ɡ", "n"}
UNVOICED = {"p", "s", "t", "θ", "k", "ʃ"}

MANNER = {
    "ð": "fricative", "θ": "fricative", "s": "fricative", "ʃ": "fricative",
    "b": "stop", "p": "stop", "ɡ": "stop", "k": "stop", "t": "stop",
    "n": "nasal",
    "ə": "vowel", "ɪ": "vowel", "æ": "vowel", "ɒ": "vowel", "iː": "vowel",
}


def is_vowel(p):
    return p in VOWELS


def is_voiced(p):
    return p in VOICED


def voicing(p):
    if p in VOICED:
        return "voiced"
    if p in UNVOICED:
        return "unvoiced"
    return "n/a"


def vowel_class(p):
    return "vowel" if p in VOWELS else "non-vowel"


def phone_tier_labels():
    """Phone labels including the leading and trailing silence."""
    return [SIL] + PHONES + [SIL]


def word_tier_labels():
    return [SIL] + WORDS + [SIL]
