from typing import List, Optional
import regex as re
import os
import string
import enum
import Stemmer
import logging
from functools import partial, lru_cache
from lucytok.porter import PorterStemmer
from lucytok.asciifold import unicode_to_ascii
from lucytok.plurals import plural_to_root


logger = logging.getLogger(__name__)


stemmer = Stemmer.Stemmer("english")
porterv1 = PorterStemmer()


punct_trans = str.maketrans({key: ' ' for key in string.punctuation})


# get es_url from env
es_url = os.getenv("ES_URL")


def unnest_list(sublist):
    flattened_list = []
    for item in sublist:
        if isinstance(item, list):
            flattened_list.extend(item)
        else:
            flattened_list.append(item)
    return flattened_list


def porter2_stem_word(word):
    return stemmer.stemWord(word)


def remove_posessive(text):
    text_without_posesession = []
    for word in text.split():
        if word.endswith("'s"):
            text_without_posesession.append(word[:-2])
        else:
            text_without_posesession.append(word)
    return " ".join(text_without_posesession)


case_change_re = re.compile(r'.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)')


@lru_cache(maxsize=30000)
def split_on_case_change(s):
    matches = case_change_re.finditer(s)
    return [m.group(0) for m in matches]


char_to_num_change_re = re.compile(r'.+?(?:(?<=\d)(?=\D)|(?<=\D)(?=\d)|$)')


@lru_cache(maxsize=30000)
def split_on_char_num_change(s):
    matches = char_to_num_change_re.finditer(s)
    return [m.group(0) for m in matches]


# a, an, and, are, as, at, be, but, by, for, if, in, into, is, it, no, not, of, on, or, such, that, the, their, then, there, these, they, this, to, was, will, with
elasticsearch_english_stopwords = [
    "a", "an", "and", "as", "at", "be", "but", "by", "for", "if",
    "in", "into", "is", "it", "no", "not", "of", "on", "or", "such", "that",
    "the", "their", "then", "there", "these", "they", "this", "to", "was", "will",
    "with"]


std_pattern = r"\w\p{Extended_Pictographic}\p{WB:RegionalIndicator}"
segment = re.compile(rf"[{std_pattern}](?:\B\S)*", flags=re.WORD)


def standard_tokenizer(text: str) -> List[str]:
    """Tokenize text using a standard tokenizer."""
    # Find all tokens based on the word boundary pattern
    return segment.findall(text)


def ws_tokenizer(text: str) -> str:
    return text.split()


punct_to_ws = str.maketrans(string.punctuation, ' ' * len(string.punctuation))


@lru_cache(maxsize=30000)
def split_punct(token):
    result = token.translate(punct_to_ws).split()
    return result


possessive_suffix_regex = re.compile(r"['’]s$")


@lru_cache(maxsize=30000)
def remove_suffix(token: str) -> str:
    if token.endswith("'s") or token.endswith("’s"):
        return token[:-2]
    return token


def remove_posessive_suffixes(tokens: List[str]) -> List[str]:
    """Remove posessive suffixes from tokens."""

    return [remove_suffix(token) for token in tokens]

# "rebuilt_english": {
#          "tokenizer":  "standard",
#          "filter": [
#            "english_possessive_stemmer",
#            "lowercase",
#            "english_stop",
#            "english_keywords",
#            "english_stemmer"
#          ]
#        }


def fold_to_ascii(input_text):
    return unicode_to_ascii(input_text)


class TokenizerSelection(enum.Enum):
    STARDARD = "s"
    WHITESPACE = "w"
    WS_W_PUNCT = "p"


def tokenizer(text: str,
              ascii_folding: bool,
              std_tokenizer: bool,
              split_on_punct: bool,
              split_on_case: bool,
              split_on_num: bool,
              lowercase: bool,
              remove_possessive: bool,
              stopwords_to_char: Optional[str],
              irregular_plural: bool,
              porter_version: Optional[int]) -> List[str]:
    if ascii_folding:
        text = fold_to_ascii(text)

    if std_tokenizer:
        tokens = standard_tokenizer(text)
    else:
        tokens = ws_tokenizer(text)

    # Strip trailing 's from tokens
    if remove_possessive:
        tokens = remove_posessive_suffixes(tokens)

    # Split on punctuation
    if split_on_punct:
        tokens = unnest_list([split_punct(tok) for tok in tokens])

    # Split on case change FooBar -> Foo Bar
    if split_on_case:
        tokens = unnest_list([split_on_case_change(tok) for tok in tokens])

    # Split on number
    if split_on_num:
        tokens = unnest_list([split_on_char_num_change(tok) for tok in tokens])

    # Lowercase
    if lowercase:
        tokens = [token.lower() for token in tokens]

    # Replace stopwords with a 'blank' character
    if stopwords_to_char:
        tokens = [token if token.lower() not in elasticsearch_english_stopwords
                  else stopwords_to_char for token in tokens]

    if irregular_plural:
        tokens = [plural_to_root(token) for token in tokens]

    # Stem with Porter stemmer version if specified
    if porter_version == 1:
        tokens = [porterv1.stem(token) for token in tokens]
    elif porter_version == 2:
        tokens = [porter2_stem_word(token) for token in tokens]

    return tokens


def tokenizer_factory(ascii_folding: bool,
                      std_tokenizer: bool,
                      split_on_punct: bool,
                      split_on_case: bool,
                      split_on_num: bool,
                      remove_possessive: bool,
                      lowercase: bool,
                      stopwords_to_char: Optional[str],
                      irregular_plural: bool,
                      porter_version: Optional[int]) -> partial:

    logger.info("***")
    logger.info("Creating tokenizer with settings")
    logger.info(f"ASCIIFolding:{ascii_folding}")
    logger.info(f"StandardTokenizer:{std_tokenizer}")
    logger.info(f"RemovePossessive:{remove_possessive}")
    logger.info(f"SplitOnPunct:{split_on_punct}")
    logger.info(f"SplitOnCase:{split_on_case}")
    logger.info(f"SplitOnNum:{split_on_num}")
    logger.info(f"Lowercase:{lowercase}")
    logger.info(f"StopwordsToChar:{stopwords_to_char}")
    logger.info(f"IrregularPlural:{irregular_plural}")
    logger.info(f"PorterVersion:{porter_version}")
    tok_func = partial(tokenizer,
                       ascii_folding=ascii_folding,
                       std_tokenizer=std_tokenizer,
                       split_on_punct=split_on_punct,
                       split_on_case=split_on_case,
                       split_on_num=split_on_num,
                       lowercase=lowercase,
                       remove_possessive=remove_possessive,
                       stopwords_to_char=stopwords_to_char,
                       irregular_plural=irregular_plural,
                       porter_version=porter_version)

    test_string = "MaryHad a little_lamb whose 1920s 12fleeceYards was supposedly white. The lamb's fleece was actually black..."
    logger.info(f"Testing tokenizer with test string: {test_string}")
    logger.info(f"Tokenizer output: {tok_func(test_string)}")
    return tok_func


def tokenizer_from_str(tok_str):
    """
    Each char corresponds to a different tokenizer setting.
    """
    # Validate args
    if tok_str.count('|') != 2:
        raise ValueError("Tokenizer string must have 2 '|' characters separiting ascii folding,tokenizer,posessive|punc,case,letter->num|lowercase,stopowords,stemmer")
    tok_str = tok_str.replace("|", "")
    if len(tok_str) != 10:
        raise ValueError("Tokenizer string must be 10 characters long")
    else:
        if tok_str[0] not in 'aN':
            raise ValueError(f"0th character must be either 'a' (ascii folding) or 'N' (no ascii folding) -- you passed {tok_str[0]}")
        if tok_str[1] not in 'sw':
            raise ValueError(f"1st character must be either 's' (standard tokenizer) or 'w' (whitespace tokenizer) -- you passed {tok_str[1]}")
        if tok_str[2] not in 'pN':
            raise ValueError(f"2nd character must be either 'p' (remove possessive) or 'N' (don't remove possessive) -- you passed {tok_str[2]}")
        if tok_str[3] not in 'pN':
            raise ValueError(f"3rd character must be either 'p' (split on punctuation) or 'N' (don't split on punctuation) -- you passed {tok_str[3]}")
        if tok_str[4] not in 'cN':
            raise ValueError(f"4th character must be either 'c' (split on case) or 'N' (don't split on case) -- you passed {tok_str[4]}")
        if tok_str[5] not in 'nN':
            raise ValueError(f"5th character must be either 'n' (split on letter->number) or 'N' (don't split on number) -- you passed {tok_str[5]}")
        if tok_str[6] not in 'lN':
            raise ValueError(f"6th character must be either 'l' (lowercase) or 'N' (don't lowercase) -- you passed {tok_str[6]}")
        if tok_str[7] not in 'sN':
            raise ValueError(f"7th character must be either 's' (stopwords to char) or 'N' (don't stopwords to char) -- you passed {tok_str[7]}")
        if tok_str[8] not in 'pN':
            raise ValueError("8th character must be either 'p' normalize irregular plurals , 'N' (do nothing) -- you passed {tok_str[8]}")
        if tok_str[9] not in '12N':
            raise ValueError("8th character must be either '1' (porter version 1), '2' (porter version 2), or 'N' (no stemming) -- you passed {tok_str[9]}")
        porter_version = int(tok_str[9]) if tok_str[9] != 'N' else None

        return tokenizer_factory(
            tok_str[0] == 'a',
            std_tokenizer=tok_str[1] == 's',
            remove_possessive=tok_str[2] == 'p',
            split_on_punct=tok_str[3] == 'p',
            split_on_case=tok_str[4] == 'c',
            split_on_num=tok_str[5] == 'n',
            lowercase=tok_str[6] == 'l',
            stopwords_to_char='_' if tok_str[7] == 's' else None,
            irregular_plural=tok_str[8] == 'p',
            porter_version=porter_version
        )


def every_tokenizer_str():
    case = 'N'
    num = 'N'
    punctuation = 'p'
    lowercase = 'l'
    for ascii_fold in ['a', 'N']:
        for tok in ['s', 'w']:
            for punctuation in ['p', 'N']:
                for case in ['c', 'N']:
                    for num in ['n', 'N']:
                        for poss in ['p', 'N']:
                            for lowercase in ['l', 'N']:
                                for stop in ['s', 'N']:
                                    for irreg in ['p', 'N']:
                                        for stem in ['1', '2', 'N']:
                                            yield f"{ascii_fold}{tok}{poss}|{punctuation}{case}{num}|{lowercase}{stop}{irreg}{stem}"


def every_tokenizer():
    for tok_str in every_tokenizer_str():
        yield tokenizer_from_str(tok_str), tok_str
#
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
