from lucytok.tokenizer import tokenizer_from_str


#  |- ASCII fold (a) or not (N)
#  ||- Standard (s) or WS tokenizer (w)
#  ||- Remove possessive suffixes (p) or not (N)
#  |||
# "NsN|NNN|NNN"
#      ||| |||
#      ||| |||- Porter stem vs (1) vs (2) vs N/0 for none
#      ||| ||- Blank out stopwords (s) or not (N)
#      ||| |- Lowercase (l) or not (N)
#      |||- Split on letter/number transitions (n) or not (N)
#      ||- Split on case changes (c) or not (N)
#      |- Split on punctuation (p) or not (N)
def tokenizer(spec: str):
    return tokenizer_from_str(spec)
