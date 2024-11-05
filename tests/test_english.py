from lucytok import english


def test_ws_tokenizer():
    ws_tokenizer = english("NwN|NNN|lNNN")
    assert ws_tokenizer('👍👎') == ['👍👎']
    assert ws_tokenizer('Mary-had a little_lamb') == ['mary-had', 'a', 'little_lamb']


def test_std_tokenizer():
    std_tokenizer = english("NsN|NNN|lNNN")
    assert std_tokenizer('👍👎') == ['👍', '👎']


def test_split_punctuation():
    ws_split_punct_tokenizer = english("NwN|pNN|lNNN")
    assert ws_split_punct_tokenizer('Mary-had a little_lamb') == ['mary', 'had', 'a', 'little', 'lamb']


def test_ascii_fold():
    ascii_fold = english("asN|NNN|lNNN")
    no_ascii_fold = english("NsN|NNN|lNNN")
    assert ascii_fold("René") == ["rene"]
    assert no_ascii_fold("René") == ["rené"]
    assert (ascii_fold("àáâãäåçèéêëìíîïðñòóôõöøùúûüýþÿ")
            == ['aaaaaaceeeeiiiidnoooooouuuuyty'])


def test_split_on_case_change():
    split_on_case_change = english("NsN|NcN|lNNN")
    no_split_on_case_str = english("NsN|NNN|lNNN")
    assert no_split_on_case_str("fooBar") == ["foobar"]
    assert split_on_case_change("fooBar") == ["foo", "bar"]


def test_porter_stemmer():
    porter1 = english("NsN|NNN|lNN1")
    porter2 = english("NsN|NNN|lNN2")
    no_stem = english("NsN|NNN|lNNN")
    assert porter1("1920s") == ["1920"]
    assert porter2("1920s") == ["1920s"]
    assert no_stem("running") == ["running"]


def test_stopwords():
    stopwords = english("NsN|NNN|lsNN")
    no_stopwords = english("NsN|NNN|lNNN")
    assert stopwords("the") == ["_"]
    assert no_stopwords("the") == ["the"]


def test_posessive():
    posessive = english("Nsp|NNN|lNNN")
    no_possessive = english("NsN|NNN|lNNN")
    assert posessive("the's") == ["the"]
    assert no_possessive("the") == ["the"]


def test_lower_case():
    lowercase = english("NsN|NNN|lNNN")
    no_lowercase = english("NsN|NNN|NNNN")
    assert lowercase("The") == ["the"]
    assert no_lowercase("The") == ["The"]


def test_split_on_num():
    split_on_num = english("NsN|NNn|lNNN")
    no_split_on_sum = english("NsN|NNN|lNNN")
    assert split_on_num("foo2thee") == ["foo", "2", "thee"]
    assert no_split_on_sum("foo2thee") == ["foo2thee"]


def test_posessive_std():
    posessive_std = english("Nsp|NNN|lNNN")
    assert posessive_std("cat's pajamas") == ["cat", "pajamas"]


def test_irregular_plurals():
    irreg_plurals = english("Nsp|NNN|lNpN")
    no_irreg_plurals = english("Nsp|NNN|lNNN")
    assert irreg_plurals("people") == ["person"]
    assert no_irreg_plurals("people") == ["people"]
