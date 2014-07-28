"""
If you want to play with a flavor or ingredient matrix, use these methods:
ingredients_flavor_matrix
recipe_matrix
"""

# To ignore numpy errors:
#     pylint: disable=E1101

from enum import Enum
import numpy as np
import os
import pickle
import scipy.sparse as sp
from sklearn.preprocessing import normalize

from emma.data_formatting import render_ingredient_as_single_word
import src.constants as constants


AMOUNT_PARSING_GUIDE = constants.DATA_DIRECTORY+'amount_parsing_map'


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
        clean_name = render_ingredient_as_single_word(ingredient_name)
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


def recipe_matrix(normalization):
    """
    Processes the result of parsePages and
    returns a cocktails by ingredients matrix (numpy)
    """
    print "Building recipe matrix"
    if os.path.isfile(AMOUNT_PARSING_GUIDE):
        associations = pickle.load(open(AMOUNT_PARSING_GUIDE, 'rb'))
    else:
        print "No AMOUNT_PARSING_GUIDE, run build_amount_parsing_guide first"
        return None, None
    print "...loading recipe list from file"
    print "run parsePages if you want a new version of the file"
    recipes = pickle.load(open(constants.CLEANED_COCKTAILS_FILENAME, 'rb'))
    index = RecipeNameIndex(recipes)
    resulting_matrix = np.zeros(
        shape=(index.count_cocktails(), index.count_ingreds()))
    for cocktail_name, ingredient_tuples in recipes.iteritems():
        cocktail_idx = index.title_idx(cocktail_name)
        for tup in ingredient_tuples:
            ingred_name = tup[0]
            ingred_name = render_ingredient_as_single_word(ingred_name)
            ingred_idx = index.ingred_idx(ingred_name)
            ingred_amount = associations[tup[1].strip()+tup[2].strip()]
            resulting_matrix[cocktail_idx, ingred_idx] = ingred_amount

    if normalization is Normalization.EXACT_AMOUNTS:
        pass
    elif normalization is Normalization.BOOLEAN:
        resulting_matrix[resulting_matrix!=0] = 1.0
    elif normalization is Normalization.ROW_SUM_ONE:
        resulting_matrix = normalize(resulting_matrix, axis=1, norm='l1')
    elif normalization is Normalization.TFIDF:
        resulting_matrix[resulting_matrix!=0] = 1.0
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
        self._ingred_to_number = {}
        self._number_to_ingred = {}
        title_idx = 0
        ingred_idx = 0
        for title, ingredients in recipe_list.iteritems():
            if title not in self._title_to_number:
                self._title_to_number[title] = title_idx
                self._number_to_title[str(title_idx)] = title
                title_idx += 1
            for tup in ingredients:
                ingred_name = tup[0]
                ingred_name = render_ingredient_as_single_word(ingred_name)
                if ingred_name not in self._ingred_to_number:
                    self._ingred_to_number[ingred_name] = ingred_idx
                    self._number_to_ingred[str(ingred_idx)] = ingred_name
                    ingred_idx += 1

    def get_name(self, integer_index):
        """
        Converts a recipe index into its proper name.
        """
        return self._number_to_title[str(integer_index)]

    def get_ingred(self, integer_index):
        """
        Converts an ingredient index into its proper name.
        """
        return self._number_to_ingred[str(integer_index)]

    def ingred_idx(self, ingred_name):
        """
        Converts an ingredient name into the corresponding index.
        """
        return self._ingred_to_number[ingred_name]

    def title_idx(self, title_string):
        """
        Converts a recipe name into the corresponding index.
        """
        return self._title_to_number[title_string]

    def count_cocktails(self):
        """
        Return number of cocktail recipes in the index.
        """
        return len(self._title_to_number)

    def count_ingreds(self):
        """
        Return number of ingredients in the index.
        """
        return len(self._ingred_to_number)


def build_amount_parsing_guide():
    """
    Creates a map (in AMOUNT_PARSING_GUIDE) that goes from
    strings -> ingredients. Human generated.
    Relies on the result of parsePages
    """
    associations = {}
    if os.path.isfile(AMOUNT_PARSING_GUIDE):
        associations = pickle.load(open(AMOUNT_PARSING_GUIDE, 'rb'))

    print "...loading recipe list from file"
    print "run parsePages to generate a new version of the file"
    recipes = pickle.load(open(constants.CLEANED_COCKTAILS_FILENAME, 'rb'))
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


if __name__ == '__main__':
    print "The only reason you should be running this is for testing purposes."
    ingredients_flavor_dict()
