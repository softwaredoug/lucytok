from lucytok.tokenizer import tokenizer_from_str


def english(spec: str):
    return tokenizer_from_str(spec)
