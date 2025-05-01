from typing import List, Tuple
from lucytok import english
from lucytok.tokenizer import TOKEN, START_OFFSET, END_OFFSET
import pytest
import random


def tokens_of(token_list):
    if isinstance(token_list, list):
        return [tokens_of(item) for item in token_list]
    elif isinstance(token_list, tuple):
        return token_list[TOKEN]
    else:
        raise ValueError("Unexpected data type")


def offsets_of(token_list):
    if isinstance(token_list, list):
        return [offsets_of(item) for item in token_list]
    elif isinstance(token_list, tuple):
        return (token_list[START_OFFSET], token_list[END_OFFSET])
    else:
        raise ValueError("Unexpected data type")


def test_ws_tokenizer():
    ws_tokenizer = english("NwN->NNN->l->NNNN->N")
    assert tokens_of(ws_tokenizer('👍👎')) == ['👍👎']
    assert tokens_of(ws_tokenizer('Mary-had a little_lamb')) == ['mary-had', 'a', 'little_lamb']


def test_ws_tokenizer_offsets():
    ws_tokenizer = english("NwN->NNN->l->NNNN->N")
    assert offsets_of(ws_tokenizer('👍👎')) == [(0, 2)]
    mary_text = 'Mary-had a little_lamb'
    offsets = offsets_of(ws_tokenizer('Mary-had a little_lamb'))
    assert mary_text[slice(offsets[0][0], offsets[0][1])] == 'Mary-had'
    assert mary_text[slice(offsets[1][0], offsets[1][1])] == 'a'
    assert mary_text[slice(offsets[2][0], offsets[2][1])] == 'little_lamb'


def test_std_tokenizer_offsets():
    std_tokenizer = english("NsN->NNN->l->NNNN->N")
    mary_text = 'Mary-had a little_lamb'
    offsets = offsets_of(std_tokenizer('Mary-had a little_lamb'))
    assert mary_text[slice(offsets[0][0], offsets[0][1])] == 'Mary'
    assert mary_text[slice(offsets[1][0], offsets[1][1])] == 'had'
    assert mary_text[slice(offsets[2][0], offsets[2][1])] == 'a'
    assert mary_text[slice(offsets[3][0], offsets[3][1])] == 'little_lamb'


def test_std_tokenizer():
    std_tokenizer = english("NsN->NNN->l->NNNN->N")
    assert tokens_of(std_tokenizer('👍👎')) == ['👍', '👎']


def test_split_punctuation():
    ws_split_punct_tokenizer = english("NwN->pNN->l->NNNN->N")
    assert tokens_of(ws_split_punct_tokenizer('Mary-had a little_lamb')) == ['mary', 'had', 'a', 'little', 'lamb']


def test_ascii_fold():
    ascii_fold = english("asN->NNN->l->NNNN->N")
    no_ascii_fold = english("NsN->NNN->l->NNNN->N")
    assert tokens_of(ascii_fold("René")) == ["rene"]
    assert tokens_of(no_ascii_fold("René")) == ["rené"]
    assert (tokens_of(ascii_fold("àáâãäåçèéêëìíîïðñòóôõöøùúûüýþÿ"))
            == ['aaaaaaceeeeiiiidnoooooouuuuyty'])


def test_split_on_case_change():
    split_on_case_change = english("NsN->NcN->l->NNNN->N")
    no_split_on_case_str = english("NsN->NNN->l->NNNN->N")
    assert tokens_of(no_split_on_case_str("fooBar")) == ["foobar"]
    assert tokens_of(split_on_case_change("fooBar")) == ["foo", "bar"]


def test_porter_stemmer():
    porter1 = english("NsN->NNN->l->NNNN->1")
    porter2 = english("NsN->NNN->l->NNNN->2")
    no_stem = english("NsN->NNN->l->NNNN->N")
    assert tokens_of(porter1("1920s")) == ["1920"]
    assert tokens_of(porter2("1920s")) == ["1920s"]
    assert tokens_of(no_stem("running")) == ["running"]


def test_stopwords():
    stopwords = english("NsN->NNN->l->sNNN->N")
    no_stopwords = english("NsN->NNN->l->NNNN->N")
    assert tokens_of(stopwords("the")) == ["_"]
    assert tokens_of(no_stopwords("the")) == ["the"]


def test_posessive():
    posessive = english("Nsp->NNN->l->NNNN->N")
    no_posessive = english("NsN->NNN->l->NNNN->N")
    assert tokens_of(posessive("the's")) == ["the"]
    assert tokens_of(no_posessive("the")) == ["the"]


def test_lower_case():
    lowercase = english("NsN->NNN->l->NNNN->N")
    no_lowercase = english("NsN->NNN->N->NNNN->N")
    assert tokens_of(lowercase("The")) == ["the"]
    assert tokens_of(no_lowercase("The")) == ["The"]


def test_split_on_num():
    split_on_num = english("NsN->NNn->l->NNNN->N")
    no_split_on_sum = english("NsN->NNN->l->NNNN->N")
    assert tokens_of(split_on_num("foo2thee")) == ["foo", "2", "thee"]
    assert tokens_of(no_split_on_sum("foo2thee")) == ["foo2thee"]


def test_posessive_std():
    posessive_std = english("Nsp->NNN->l->NNNN->N")
    assert tokens_of(posessive_std("cat's pajamas")) == ["cat", "pajamas"]


def test_irregular_plurals():
    irreg_plurals = english("Nsp->NNN->l->NNNp->N")
    no_irreg_plurals = english("Nsp->NNN->l->NNNN->N")
    assert tokens_of(irreg_plurals("people")) == ["person"]
    assert tokens_of(no_irreg_plurals("people")) == ["people"]


def test_compound_split():
    compound_split = english("Nsp->NNN->l->NcNN->N")
    no_compound_split = english("Nsp->NNN->l->NNNN->N")
    assert tokens_of(compound_split("airplane")) == ["air", "plane"]
    assert tokens_of(compound_split("a big backpack airplane")) == ["a", "big", "back", "pack", "air", "plane"]
    assert tokens_of(no_compound_split("airplane")) == ["airplane"]


def test_british_english():
    british = english("Nsp->NNN->l->NNbN->N")
    no_british = english("Nsp->NNN->l->NNNN->N")
    assert tokens_of(british("aeroplane")) == ["airplane"]
    assert tokens_of(no_british("aeroplane")) == ["aeroplane"]


def test_compound_not_flattened():
    compound_split = english("Nsp->NNN->l->NcNN->N", flatten=False)
    assert tokens_of(compound_split("a big backpack airplane")) ==\
        ["a", "big", ["back", "pack"], ["air", "plane"]]


def test_compound_num_not_flattened():
    compound_split = english("Nsp->NNn->l->NcNN->N", flatten=False)
    assert (tokens_of(compound_split("a big backpack2backpack airplane"))
            == ["a", "big", [["back", "pack"], "2", ["back", "pack"]], ["air", "plane"]])


def test_british_compound_num_not_flattened():
    compound_split = english("Nsp->NNn->l->NcbN->N", flatten=False)
    assert (tokens_of(
        compound_split("a big watercolour2backpack airplane"))
        == ["a", "big", [["water", "color"], "2", ["back", "pack"]], ["air", "plane"]])


def test_compound_num_flattened():
    compound_split = english("Nsp->NNn->l->NcNN->N", flatten=True)
    assert (tokens_of(compound_split("a big backpack2backpack airplane"))
            == ["a", "big", "back", "pack", "2", "back", "pack", "air", "plane"])


def test_everything_on():
    everything = english("asp->pcn->l->scbp->1")
    tokenized = everything("How many years did William Bradford serve as Governor of the Plymouth Colony?")
    assert tokens_of(tokenized) == ['how', 'mani', 'year', 'did', 'william', 'bradford', 'serv', '_',
                                    'governor', '_', '_', 'plymouth', 'coloni']


def test_everything_on_flattened_no_expansions():
    everything = english("asp->pcn->l->scbp->1", flatten=False)
    tokenized = everything("How many years did William Bradford serve as Governor of the Plymouth Colony?")
    assert tokens_of(tokenized) == ['how', 'mani', 'year', 'did', 'william', 'bradford', 'serv', '_', 'governor', '_', '_', 'plymouth', 'coloni']


def test_everything_on_unflattened_blanks_no_empty_lists():
    everything = english("asp->pcn->l->scbp->1", flatten=False)
    tokenized = tokens_of(everything("____________________ is considered the father of modern medicine."))
    for token in tokenized:
        assert token != []


def test_compounds_with_stopwords():
    everything = english("asp->pcn->l->scbp->1", flatten=False)
    tokenized = everything("another name for delzicol")
    assert tokens_of(tokenized[0]) == ['an', 'other']


def test_compounds_gathers_phrases():
    compounds = english("asp->pcn->l->Ncbp->1", flatten=False)
    tokenized = tokens_of(compounds("an other back pack on an air plane"))
    assert tokenized == [['an', 'other'], ['back', 'pack'], 'on', 'an', ['air', 'plane']]


def test_compounds_does_not_gather_phrases_when_flattening():
    compounds = english("asp->pcn->l->Ncbp->1", flatten=True)
    tokenized = tokens_of(compounds("an other back pack on an air plane"))
    assert tokenized == ['an', 'other', 'back', 'pack', 'on', 'an', 'air', 'plane']


def test_single_char_not_consumed():
    everything = english("asp->pcn->l->scbp->1", flatten=False)
    tokenized = tokens_of(everything("what me2 fart"))
    assert tokenized == ['what', ['me', '2'], 'fart']


def test_single_char_stopword_not_consumed():
    everything = english("asp->pcn->l->scbp->1", flatten=False)
    tokenized = tokens_of(everything("what a2 fart"))
    assert tokenized == ['what', ['_', '2'], 'fart']

    everything_no_stop = english("asp->pcn->l->Ncbp->1", flatten=False)
    tokenized = tokens_of(everything_no_stop("what a2 fart"))
    assert tokenized == ['what', ['a', '2'], 'fart']

    everything_no_stop = english("asp->pcn->l->Ncbp->1", flatten=False)
    tokenized = tokens_of(everything_no_stop("what the2 fart"))
    assert tokenized == ['what', ['the', '2'], 'fart']


@pytest.mark.parametrize("seed", [0, 1, 2, 3, 4, 5])
def test_random_strings(seed):
    random.seed(seed)
    everything = english("asp->pcn->l->scbp->1", flatten=False)
    tokenized = everything("".join(random.choices("abcdefghijklmnopqrstuvwxyz ", k=1000))
                           + " ".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=1000)))
    assert isinstance(tokenized, list)
    for token in tokens_of(tokenized):
        assert token != []
