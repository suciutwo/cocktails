"""
If you want to play with a flavor or ingredient matrix, use these methods:
ingredients_flavor_matrix
recipe_matrix
"""

# To ignore numpy errors:
#     pylint: disable=E1101
import string

from enum import Enum
import numpy as np
import os
import pickle
import scipy.sparse as sp
from sklearn.preprocessing import normalize

import src.constants as constants


AMOUNT_PARSING_GUIDE = constants.DATA_DIRECTORY+'amount_parsing_map'
INGREDIENT_MERGING_GUIDE = constants.DATA_DIRECTORY+'ingredient_merging_map'


class Normalization(Enum):
    """
    Types of normalization that can be performed on a matrix.
    """
    EXACT_AMOUNTS = 1
    BOOLEAN = 2
    ROW_SUM_ONE = 3
    TFIDF = 4


def ingredients_flavor_matrix():
    """
    Processes the result of parsePages and
    returns an ingredients by flavor names matrix (numpy)
    """
    print "...creating ingredients matrix from file"
    print "run parsePages to generate a new version of the file"
    ingredient_dict = pickle.load(
        open(constants.CLEANED_INGREDIENTS_FILENAME, 'rb'))
    matrix = np.array(ingredient_dict)
    return matrix


def ingredients_flavor_dict():
    """
    Uses output of parsePages and creates a mapping from ingredients to flavors.
    """
    clean_ingredient_dict = {}
    original_ingredient_dict = pickle.load(
        open(constants.CLEANED_INGREDIENTS_FILENAME, 'rb'))
    for ingredient_name, flavors in original_ingredient_dict.iteritems():
        clean_name = canonical_ingredient_name(ingredient_name)
        clean_flavors = ', '.join(flavors)
        if not clean_flavors:
            continue
        clean_ingredient_dict[clean_name] = clean_flavors
    return clean_ingredient_dict


def tfidf_recipe_matrix(boolean_matrix):
    """
    Given a boolean recipe matrix, normalizes the recipes using TFIDF
    """
    n_samples, n_features = boolean_matrix.shape
    document_frequency = np.sum(boolean_matrix, axis=0)

    ## Smooth
    document_frequency += 1
    n_samples += 1

    ## Calculate IDF
    idf = np.log(float(n_samples) / document_frequency) + 1.0
    idf_diag = sp.spdiags(idf, diags=0, m=n_features, n=n_features)

    ## Transform matrix according to IDF
    weighted_matrix = boolean_matrix * idf_diag
    norms = (weighted_matrix * weighted_matrix).sum(axis=1)
    norms = np.sqrt(norms, norms)
    norms[norms == 0.0] = 1.0
    weighted_matrix /= norms[:, np.newaxis]
    return weighted_matrix


def safe_pickle_load(filename, suggestion):
    """
    Helper function to reconstitute an object from a pickled file.
    :param filename: Path name of file to open, relative to /cocktails/.
    :param suggestion: String to print on failure,
    informs user how to make the file if it cannot be found.
    :return: The object stored in the file.
    """
    if os.path.isfile(filename):
        return pickle.load(open(filename, 'rb'))
    else:
        print "Could not open " + filename
        print suggestion
        raise IOError


def recipe_matrix(normalization):
    #TODO: walk through this
    """
    Processes the result of parsePages and
    returns a cocktails by ingredients matrix (numpy)
    """
    print "Building recipe_matrix with matrix_generation.py"
    amount_associations = safe_pickle_load(AMOUNT_PARSING_GUIDE,
                                           "run build_amount_parsing_guide")
    recipes = safe_pickle_load(constants.CLEANED_COCKTAILS_FILENAME,
                               "run parsePages to remake this file")
    index = RecipeNameIndex(recipes)
    resulting_matrix = np.zeros(
        shape=(index.cocktails_count(), index.ingredients_count()))
    for cocktail_name, ingredient_triples in recipes.iteritems():
        cocktail_number = index.recipe_title_number(cocktail_name)
        for triple in ingredient_triples:
            name = triple[0]
            name = canonical_ingredient_name(name)
            number = index.ingredient_number(name)
            amount = amount_associations[triple[1].strip()+triple[2].strip()]
            resulting_matrix[cocktail_number, number] = amount

    if normalization is Normalization.EXACT_AMOUNTS:
        pass
    elif normalization is Normalization.BOOLEAN:
        resulting_matrix[resulting_matrix != 0] = 1.0
    elif normalization is Normalization.ROW_SUM_ONE:
        resulting_matrix = normalize(resulting_matrix, axis=1, norm='l1')
    elif normalization is Normalization.TFIDF:
        resulting_matrix[resulting_matrix != 0] = 1.0
        resulting_matrix = tfidf_recipe_matrix(resulting_matrix)

    return resulting_matrix, index


class RecipeNameIndex(object):
    """
    Allows you to look up recipe names and ingredient names from numbers
    so that you can understand the data you're working on while not relying
    on column names.
    """
    def __init__(self, recipe_list):
        """
        The list of recipes and their ingredients will be used to
        set the assignment of index numbers.
        """
        self._title_to_number = {}
        self._number_to_title = {}
        self._ingredient_to_number = {}
        self._number_to_ingredient = {}
        title_idx = 0
        ingredient_idx = 0
        for title, ingredient_triples in recipe_list.iteritems():
            if title not in self._title_to_number:
                self._title_to_number[title] = title_idx
                self._number_to_title[str(title_idx)] = title
                title_idx += 1
            for tup in ingredient_triples:
                name = tup[0]
                name = canonical_ingredient_name(name)
                if name not in self._ingredient_to_number:
                    self._ingredient_to_number[name] = ingredient_idx
                    self._number_to_ingredient[str(ingredient_idx)] = name
                    ingredient_idx += 1

    def recipe_title(self, integer_index):
        """
        Converts a recipe index into its proper name.
        """
        return self._number_to_title[str(integer_index)]

    def ingredient(self, integer_index):
        """
        Converts an ingredient index into its proper name.
        """
        return self._number_to_ingredient[str(integer_index)]

    def ingredient_number(self, ingred_name):
        """
        Converts an ingredient name into the corresponding index.
        """
        return self._ingredient_to_number[ingred_name]

    def recipe_title_number(self, title_string):
        """
        Converts a recipe name into the corresponding index.
        """
        return self._title_to_number[title_string]

    def cocktails_count(self):
        """
        Return number of cocktail recipes in the index.
        """
        return len(self._title_to_number)

    def ingredients_count(self):
        """
        Return number of ingredients in the index.
        """
        return len(self._ingredient_to_number)


def build_amount_parsing_guide():
    """
    Creates a map (in AMOUNT_PARSING_GUIDE) that goes from
    strings -> ingredients. Human generated.
    Relies on the result of parsePages
    """
    associations = {}
    if os.path.isfile(AMOUNT_PARSING_GUIDE):
        associations = pickle.load(open(AMOUNT_PARSING_GUIDE, 'rb'))

    recipes = safe_pickle_load(constants.CLEANED_COCKTAILS_FILENAME,
                               "run parsePages to remake this file")
    for idx, recipe in enumerate(recipes.values()):
        for tup in recipe:
            print tup
            print " number: " + str(idx+1)
            key = tup[1].strip() + tup[2].strip()
            if key not in associations:
                print tup[1] + tup[2]
                user_input = raw_input()
                if user_input == 'pass':
                    continue
                if user_input == 'quit':
                    pickle.dump(associations, open(AMOUNT_PARSING_GUIDE, 'wb'))
                    return
                if user_input == 'err':
                    return
                if user_input[0] == 'd':  # dash
                    associations[key] = len(user_input)*0.03125
                elif user_input[0] == 't':  # teaspoon
                    associations[key] = len(user_input)*0.125
                elif user_input[0] == 'T':  # tablespoon
                    associations[key] = len(user_input)*0.5
                else:
                    associations[key] = float(user_input)
        if idx % 10 == 0:
            pickle.dump(associations, open(AMOUNT_PARSING_GUIDE, 'wb'))
            print "***%f done***" % (idx*1.0/len(recipes))
    pickle.dump(associations, open(AMOUNT_PARSING_GUIDE, 'wb'))


def canonical_ingredient_name(string_):
    """
    Converts a raw string from the ingredient file into its canonical name.
    This step also merges what we judge to be identical ingredients into a
    single name.
    """
    correction_map = {'tabasco_sauce': 'tabasco',
                      'muscatel_wine': 'muscat',
                      'rye_whiskey': 'rye',
                      'yolk_of_egg': 'egg_yolk',
                      'yolk_of__egg': 'egg_yolk'}
    string_ = string_.replace('fresh', '').strip()
    string_ = string_.translate(string.maketrans("", ""), string.punctuation)
    string_ = string_.lower().replace(' ', '_')
    string_ = string_.decode('utf-8')
    if string_ in correction_map:
        return correction_map[string_]
    return string_


def print_ingredient_counts():
    """
    This is a debugging function that prints out counts of each ingredient.
    It was created to help give me a better idea about how much progress
    was being made on merging similar ingredients.
    """
    bool_matrix, index = recipe_matrix(Normalization.BOOLEAN)
    tst = [index.ingredient(i) for i in range(index.ingredients_count())]
    ingredient_sums = np.sum(bool_matrix, axis=0)
    ingredient_counts = zip(tst, ingredient_sums)
    sorted_ingredient_counts = sorted(ingredient_counts, key=lambda x: x[1])
    for item in sorted_ingredient_counts:
        print item

if __name__ == '__main__':
    print "The only reason you should be running this is for testing purposes."
    #ingredients_flavor_dict()
    print_ingredient_counts()
