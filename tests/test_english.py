from lucytok import english


def test_ws_tokenizer():
    ws_tokenizer = english("NwN->NNN->l->NNN->N")
    assert ws_tokenizer('👍👎') == ['👍👎']
    assert ws_tokenizer('Mary-had a little_lamb') == ['mary-had', 'a', 'little_lamb']


def test_std_tokenizer():
    std_tokenizer = english("NsN->NNN->l->NNN->N")
    assert std_tokenizer('👍👎') == ['👍', '👎']


def test_split_punctuation():
    ws_split_punct_tokenizer = english("NwN->pNN->l->NNN->N")
    assert ws_split_punct_tokenizer('Mary-had a little_lamb') == ['mary', 'had', 'a', 'little', 'lamb']


def test_ascii_fold():
    ascii_fold = english("asN->NNN->l->NNN->N")
    no_ascii_fold = english("NsN->NNN->l->NNN->N")
    assert ascii_fold("René") == ["rene"]
    assert no_ascii_fold("René") == ["rené"]
    assert (ascii_fold("àáâãäåçèéêëìíîïðñòóôõöøùúûüýþÿ")
            == ['aaaaaaceeeeiiiidnoooooouuuuyty'])


def test_split_on_case_change():
    split_on_case_change = english("NsN->NcN->l->NNN->N")
    no_split_on_case_str = english("NsN->NNN->l->NNN->N")
    assert no_split_on_case_str("fooBar") == ["foobar"]
    assert split_on_case_change("fooBar") == ["foo", "bar"]


def test_porter_stemmer():
    porter1 = english("NsN->NNN->l->NNN->1")
    porter2 = english("NsN->NNN->l->NNN->2")
    no_stem = english("NsN->NNN->l->NNN->N")
    assert porter1("1920s") == ["1920"]
    assert porter2("1920s") == ["1920s"]
    assert no_stem("running") == ["running"]


def test_stopwords():
    stopwords = english("NsN->NNN->l->NsN->N")
    no_stopwords = english("NsN->NNN->l->NNN->N")
    assert stopwords("the") == ["_"]
    assert no_stopwords("the") == ["the"]


def test_posessive():
    posessive = english("Nsp->NNN->l->NNN->N")
    no_posessive = english("NsN->NNN->l->NNN->N")
    assert posessive("the's") == ["the"]
    assert no_posessive("the") == ["the"]


def test_lower_case():
    lowercase = english("NsN->NNN->l->NNN->N")
    no_lowercase = english("NsN->NNN->N->NNN->N")
    assert lowercase("The") == ["the"]
    assert no_lowercase("The") == ["The"]


def test_split_on_num():
    split_on_num = english("NsN->NNn->l->NNN->N")
    no_split_on_sum = english("NsN->NNN->l->NNN->N")
    assert split_on_num("foo2thee") == ["foo", "2", "thee"]
    assert no_split_on_sum("foo2thee") == ["foo2thee"]


def test_posessive_std():
    posessive_std = english("Nsp->NNN->l->NNN->N")
    assert posessive_std("cat's pajamas") == ["cat", "pajamas"]


def test_irregular_plurals():
    irreg_plurals = english("Nsp->NNN->l->NNp->N")
    no_irreg_plurals = english("Nsp->NNN->l->NNN->N")
    assert irreg_plurals("people") == ["person"]
    assert no_irreg_plurals("people") == ["people"]


def test_compound_split():
    compound_split = english("Nsp->NNN->l->cNN->N")
    no_compound_split = english("Nsp->NNN->l->NNN->N")
    assert compound_split("airplane") == ["air", "plane"]
    assert compound_split("a big backpack airplane") == ["a", "big", "back", "pack", "air", "plane"]
    assert no_compound_split("airplane") == ["airplane"]


def test_compound_not_flattened():
    compound_split = english("Nsp->NNN->l->cNN->N", flatten=False)
    assert compound_split("a big backpack airplane") == ["a", "big", ["back", "pack"], ["air", "plane"]]


def test_compound_num_not_flattened():
    compound_split = english("Nsp->NNn->l->cNN->N", flatten=False)
    assert compound_split("a big backpack2backpack airplane") == ["a", "big",
                                                                  [["back", "pack"], "2", ["back", "pack"]],
                                                                  ["air", "plane"]]


def test_compound_num_flattened():
    compound_split = english("Nsp->NNn->l->cNN->N", flatten=True)
    assert compound_split("a big backpack2backpack airplane") == ["a", "big",
                                                                  "back", "pack", "2", "back", "pack",
                                                                  "air", "plane"]
