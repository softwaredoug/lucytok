"""List of irregular English plurals plural -> root."""

v_to_f = {
    'selves': 'self',
    'leaves': 'leaf',
    'shelves': 'shelf',
    'thieves': 'thief',
    'wolves': 'wolf',
    'lives': 'life',
    'wives': 'wife',
    'calves': 'calf',
    'halves': 'half',
    'knives': 'knife',
    'leaves': 'leaf',
    'loaves': 'loaf',
    'scarves': 'scarf',
    'wives': 'wife',
    'elves': 'elf',
    'hooves': 'hoof',
    'rooves': 'roof',
    'dwarves': 'dwarf',
}

ends_in_en = {
    'children': 'child',
    'oxen': 'ox',
    'brethren': 'brother',
    'sistren': 'sister'
}

vowel_change = {
    'men': 'man',
    'women': 'woman',
    'feet': 'foot',
    'teeth': 'tooth',
    'geese': 'goose',
    'mice': 'mouse',
    'lice': 'louse'
}


ends_in_i = {
    'cacti': 'cactus',
    'fungi': 'fungus',
    'nuclei': 'nucleus',
    'radii': 'radius',
    'stimuli': 'stimulus',
    'syllabi': 'syllabus',
    'termini': 'terminus',
    'alumni': 'alumnus',
    'foci': 'focus',
    'loci': 'locus',
    'genii': 'genius',
    'octopi': 'octopus',
    'radii': 'radius'
}

just_different_word = {
    'people': 'person',
    'mice': 'mouse'
}


all_plurals_to_root = {**v_to_f, **ends_in_en, **vowel_change,
                       **ends_in_i, **just_different_word}


def plural_to_root(plural):
    """Return the root of a plural noun."""
    return all_plurals_to_root.get(plural, plural)


if __name__ == "__main__":
    print(plural_to_root('people'))
    print(plural_to_root('octopi'))
    print(plural_to_root('radii'))
    print(plural_to_root('wolves'))
    print(plural_to_root('cats'))
