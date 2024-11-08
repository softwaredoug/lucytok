## Lucytok

Lucene's boring English tokenizers recreated for Python. Compatible with [SearchArray](http://github.com/softwaredoug/searcharray).

Lets you configure a handful of normal tokenization rules like ascii folding, posessive removal, both types of 
porter stemming, English stopwords, etc.


### Usage

Creating a tokenizer close to Elasticsearch's default english analyzer

```
from lucytok import english
es_english = english("Nsp->NNN->l->NsNN->1")
tokenized = es_english("The quick brown fox jumps over the lazy døg")
print(tokenized)
```

Outputs

```
['_', 'quick', 'brown', 'fox', 'jump', 'over', '_', 'lazi', 'døg']
```

Make a tokenizer with ASCII folding...

```
from lucytok import english
es_english_folded = english("asp->NNN->l->NsNN->1")
print(es_english_folded("The quick brown fox jumps over the lazy døg"))
```

```
['_', 'quick', 'brown', 'fox', 'jump', 'over', '_', 'lazi', 'dog']
```

Split compounds and convert British to American spelling...

```
from lucytok import english
es_british = english("asp->NNN->l->cbsN->1")
print(es_british("The watercolour fox jumps over the lazy døg"))
```

```
['_', 'water', 'color', 'fox', 'jump', 'over', '_', 'lazi', 'dog']
```
### Spec

Create a tokenizer using the following settings (these concepts
correspond to their [Elasticsearch counterparts](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis.html)):

```

#  |- ASCII fold (a) or not (N)
#  ||- Standard (s) or WS tokenizer (w)
#  ||- Remove possessive suffixes (p) or not (N)
#  |||
# "NsN->NNN->N->NNNN->N"
#       |||  |  ||||  |
#       |||  |  ||||  |- Porter stem version (1) or version (2) vs N/0 for none
#       |||  |  ||||- Manually convert irregular plurals (p) or not (N)
#       |||  |  |||- Blank out stopwords (s) or not (N)
#       |||  |  ||- Convert british to american spelling (b) or not (N)
#       |||  |  |- Split Compounds (c) or not (N)
#       |||  |- Lowercase (l) or not (N)
#       |||- Split on letter/number transitions (n) or not (N)
#       ||- Split on case changes (c) or not (N)
#       |- Split on punctuation (p) or not (N)


# "NsN->NNN->N->NNN->N"
#  ---
#  (tokenization)

# "NsN->NNN->N->NNNN->N"
#       ---
#       (word splitting on rules, like WordDelimeterFilter in Lucene)

# "NsN->NNN->N->NNNN->N"
#            -
#            (lowercasing or not)

# "NsN->NNN->N->NNNN->N"
#               ----
#               (dictionary based edits: synonyms, stopwords, etc)

# "NsN->NNN->N->NNNN->N"
#                     - stemming (porter)

