from lucytok.tokenizer import tokenizer_from_str


def english(spec: str, flatten: bool = True):
    return tokenizer_from_str(spec, flatten=flatten)
