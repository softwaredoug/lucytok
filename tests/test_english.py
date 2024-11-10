from lucytok import english


def test_ws_tokenizer():
    ws_tokenizer = english("NwN->NNN->l->NNNN->N")
    assert ws_tokenizer('👍👎') == ['👍👎']
    assert ws_tokenizer('Mary-had a little_lamb') == ['mary-had', 'a', 'little_lamb']


def test_std_tokenizer():
    std_tokenizer = english("NsN->NNN->l->NNNN->N")
    assert std_tokenizer('👍👎') == ['👍', '👎']


def test_split_punctuation():
    ws_split_punct_tokenizer = english("NwN->pNN->l->NNNN->N")
    assert ws_split_punct_tokenizer('Mary-had a little_lamb') == ['mary', 'had', 'a', 'little', 'lamb']


def test_ascii_fold():
    ascii_fold = english("asN->NNN->l->NNNN->N")
    no_ascii_fold = english("NsN->NNN->l->NNNN->N")
    assert ascii_fold("René") == ["rene"]
    assert no_ascii_fold("René") == ["rené"]
    assert (ascii_fold("àáâãäåçèéêëìíîïðñòóôõöøùúûüýþÿ")
            == ['aaaaaaceeeeiiiidnoooooouuuuyty'])


def test_split_on_case_change():
    split_on_case_change = english("NsN->NcN->l->NNNN->N")
    no_split_on_case_str = english("NsN->NNN->l->NNNN->N")
    assert no_split_on_case_str("fooBar") == ["foobar"]
    assert split_on_case_change("fooBar") == ["foo", "bar"]


def test_porter_stemmer():
    porter1 = english("NsN->NNN->l->NNNN->1")
    porter2 = english("NsN->NNN->l->NNNN->2")
    no_stem = english("NsN->NNN->l->NNNN->N")
    assert porter1("1920s") == ["1920"]
    assert porter2("1920s") == ["1920s"]
    assert no_stem("running") == ["running"]


def test_stopwords():
    stopwords = english("NsN->NNN->l->sNNN->N")
    no_stopwords = english("NsN->NNN->l->NNNN->N")
    assert stopwords("the") == ["_"]
    assert no_stopwords("the") == ["the"]


def test_posessive():
    posessive = english("Nsp->NNN->l->NNNN->N")
    no_posessive = english("NsN->NNN->l->NNNN->N")
    assert posessive("the's") == ["the"]
    assert no_posessive("the") == ["the"]


def test_lower_case():
    lowercase = english("NsN->NNN->l->NNNN->N")
    no_lowercase = english("NsN->NNN->N->NNNN->N")
    assert lowercase("The") == ["the"]
    assert no_lowercase("The") == ["The"]


def test_split_on_num():
    split_on_num = english("NsN->NNn->l->NNNN->N")
    no_split_on_sum = english("NsN->NNN->l->NNNN->N")
    assert split_on_num("foo2thee") == ["foo", "2", "thee"]
    assert no_split_on_sum("foo2thee") == ["foo2thee"]


def test_posessive_std():
    posessive_std = english("Nsp->NNN->l->NNNN->N")
    assert posessive_std("cat's pajamas") == ["cat", "pajamas"]


def test_irregular_plurals():
    irreg_plurals = english("Nsp->NNN->l->NNNp->N")
    no_irreg_plurals = english("Nsp->NNN->l->NNNN->N")
    assert irreg_plurals("people") == ["person"]
    assert no_irreg_plurals("people") == ["people"]


def test_compound_split():
    compound_split = english("Nsp->NNN->l->NcNN->N")
    no_compound_split = english("Nsp->NNN->l->NNNN->N")
    assert compound_split("airplane") == ["air", "plane"]
    assert compound_split("a big backpack airplane") == ["a", "big", "back", "pack", "air", "plane"]
    assert no_compound_split("airplane") == ["airplane"]


def test_british_english():
    british = english("Nsp->NNN->l->NNbN->N")
    no_british = english("Nsp->NNN->l->NNNN->N")
    assert british("aeroplane") == ["airplane"]
    assert no_british("aeroplane") == ["aeroplane"]


def test_compound_not_flattened():
    compound_split = english("Nsp->NNN->l->NcNN->N", flatten=False)
    assert compound_split("a big backpack airplane") == ["a", "big", ["back", "pack"], ["air", "plane"]]


def test_compound_num_not_flattened():
    compound_split = english("Nsp->NNn->l->NcNN->N", flatten=False)
    assert compound_split("a big backpack2backpack airplane") == ["a", "big",
                                                                  [["back", "pack"], "2", ["back", "pack"]],
                                                                  ["air", "plane"]]


def test_british_compound_num_not_flattened():
    compound_split = english("Nsp->NNn->l->NcbN->N", flatten=False)
    assert compound_split("a big watercolour2backpack airplane") == ["a", "big",
                                                                     [["water", "color"], "2", ["back", "pack"]],
                                                                     ["air", "plane"]]


def test_compound_num_flattened():
    compound_split = english("Nsp->NNn->l->NcNN->N", flatten=True)
    assert compound_split("a big backpack2backpack airplane") == ["a", "big",
                                                                  "back", "pack", "2", "back", "pack",
                                                                  "air", "plane"]


def test_everything_on():
    everything = english("asp->pcn->l->scbp->1")
    tokenized = everything("How many years did William Bradford serve as Governor of the Plymouth Colony?")
    assert tokenized == ['how', 'mani', 'year', 'did', 'william', 'bradford', 'serv', '_',
                         'governor', '_', '_', 'plymouth', 'coloni']


def test_everything_on_flattened_no_expansions():
    everything = english("asp->pcn->l->scbp->1", flatten=False)
    tokenized = everything("How many years did William Bradford serve as Governor of the Plymouth Colony?")
    assert tokenized == ['how', 'mani', 'year', 'did', 'william', 'bradford', 'serv', '_', 'governor',
                         '_', '_', 'plymouth', 'coloni']


def test_everything_on_unflattened_blanks_no_empty_lists():
    everything = english("asp->pcn->l->scbp->1", flatten=False)
    tokenized = everything("____________________ is considered the father of modern medicine.")
    for token in tokenized:
        assert token != []


def test_compounds_with_stopwords():
    everything = english("asp->pcn->l->scbp->1", flatten=False)
    tokenized = everything("another name for delzicol")
    assert tokenized[0] == ['an', 'other']
