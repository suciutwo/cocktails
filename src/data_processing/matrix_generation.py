"""
If you want to play with a flavor or ingredient matrix, use these methods:
ingredientsFlavorMatrix
recipe_matrix
"""

# To ignore numpy errors:
#     pylint: disable=E1101

import pickle

import os
import numpy as np

from src.data_processing.parse_pages import CLEANED_COCKTAILS_FILENAME
from src.data_processing.parse_pages import CLEANED_INGREDIENTS_FILENAME


AMOUNT_PARSING_GUIDE = 'data/amount_parsing_map'


def ingredients_flavor_matrix():
    """
    Processes the result of parsePages and
    returns an ingredients by flavor names matrix (numpy)
    """
    print "...creating ingredients matrix from file"
    print "run parsePages to generate a new version of the file"
    ingredients = pickle.load(open(CLEANED_INGREDIENTS_FILENAME, 'rb'))
    matrix = np.array(ingredients)
    return matrix


def recipe_matrix(exact_amounts=True):
    """
    Processes the result of parsePages and
    returns a cocktails by ingredients matrix (numpy)

    if exact_amounts, then returns the measurement of each ingredient
    instead of mere presence (i.e. floats instead of [0, 1])
    """
    print "Building recipe matrix"
    if os.path.isfile(AMOUNT_PARSING_GUIDE):
        associations = pickle.load(open(AMOUNT_PARSING_GUIDE, 'rb'))
    else:
        print "No AMOUNT_PARSING_GUIDE, run build_amount_parsing_mapping first"
        return None, None
    print "...loading recipe list from file"
    print "run parsePages to generate a new version of the file"
    recipes = pickle.load(open(CLEANED_COCKTAILS_FILENAME, 'rb'))
    index = RecipeNameIndex(recipes)
    resulting_matrix = np.zeros(
        shape=(index.count_cocktails(), index.count_ingreds()))
    for cocktail_name, ingredient_tuples in recipes.iteritems():
        cocktail_idx = index.title_idx(cocktail_name)
        for tup in ingredient_tuples:
            ingred_name = tup[0]
            ingred_idx = index.ingred_idx(ingred_name)
            if exact_amounts:
                ingred_amount = associations[tup[1].strip()+tup[2].strip()]
            else:
                ingred_amount = 1.0
            resulting_matrix[cocktail_idx, ingred_idx] = ingred_amount
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
        self.title_to_number = {}
        self.number_to_title = {}
        self.ingred_to_number = {}
        self.number_to_ingred = {}
        title_idx = 0
        ingred_idx = 0
        for title, ingredients in recipe_list.iteritems():
            if title not in self.title_to_number:
                self.title_to_number[title] = title_idx
                self.number_to_title[str(title_idx)] = title
                title_idx += 1
            for tup in ingredients:
                ingred_name = tup[0]
                if ingred_name not in self.ingred_to_number:
                    self.ingred_to_number[ingred_name] = ingred_idx
                    self.number_to_ingred[str(ingred_idx)] = ingred_name
                    ingred_idx += 1

    def get_name(self, integer_index):
        """
        Converts a recipe index into its proper name.
        """
        return self.number_to_title[str(integer_index)]

    def get_ingred(self, integer_index):
        """
        Converts an ingredient index into its proper name.
        """
        return self.number_to_ingred[str(integer_index)]

    def ingred_idx(self, ingred_name):
        """
        Converts an ingredient name into the corresponding index.
        """
        return self.ingred_to_number[ingred_name]

    def title_idx(self, title_string):
        """
        Converts a recipe name into the corresponding index.
        """
        return self.title_to_number[title_string]

    def count_cocktails(self):
        """
        Return number of cocktail recipes in the index.
        """
        return len(self.title_to_number)

    def count_ingreds(self):
        """
        Return number of ingredients in the index.
        """
        return len(self.ingred_to_number)


def build_amount_parsing_mapping():
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
    recipes = pickle.load(open(CLEANED_COCKTAILS_FILENAME, 'rb'))
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
    ingredients_flavor_matrix()
    recipe_matrix()
