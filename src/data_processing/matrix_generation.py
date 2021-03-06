"""
If you want to play with a flavor or ingredient matrix, use these methods:
ingredients_flavor_matrix
recipe_matrix
"""

# To ignore numpy errors:
#     pylint: disable=E1101
import pickle
import regex as re

from enum import Enum
import numpy as np
import os
import pandas as pd
import scipy.sparse as sp
from src import constants
import pkg_resources


AMOUNT_PARSING_GUIDE = 'amount_parsing_map'
INGREDIENT_MERGING_GUIDE = 'ingredient_merging_map'


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
    document_frequency = boolean_matrix.sum(0)

    ## Smooth
    document_frequency += 1
    n_samples += 1

    ## Calculate IDF
    idf = np.log(float(n_samples) / document_frequency) + 1.0
    idf_diag = sp.spdiags(idf, diags=0, m=n_features, n=n_features)

    ## Transform matrix according to IDF
    weighted_matrix = boolean_matrix * idf_diag
    norms = (weighted_matrix * weighted_matrix).sum(axis=1)
    norms = np.sqrt(norms.values, norms.values)
    norms[norms == 0.0] = 1.0
    return weighted_matrix.div(norms, axis=0)


def safe_pickle_load(filename, suggestion):
    """
    Helper function to reconstitute an object from a pickled file.
    :param filename: Path name of file to open, relative to /cocktails/.
    :param suggestion: String to print on failure,
    informs user how to make the file if it cannot be found.
    :return: The object stored in the file.
    """
    print "trying to load", filename
    print "Debug version."
    print pkg_resources.resource_filename('data', filename)

    if os.path.isfile(pkg_resources.resource_filename('data', filename)):
        try:
            return pickle.load(open(pkg_resources.resource_filename('data', filename), 'rb'))
        except Exception as e:
            print e.message
            print e
    else:
        print "Could not open " + filename
        print suggestion
        raise IOError


def recipe_data(normalization, minimum_occurrences=0):
    """
    Processes the result of parsePages and
    returns a cocktails by ingredients matrix (numpy)
    """
    print "Building recipe_data object with matrix_generation.py"
    print "Requiring ingredients appear in", minimum_occurrences, "recipes"
    amount_associations = safe_pickle_load(AMOUNT_PARSING_GUIDE,
                                           "run build_amount_parsing_guide")
    recipes = safe_pickle_load(constants.CLEANED_COCKTAILS_FILENAME,
                               "run parsePages to remake this file")

    recipe_dict = {}
    for cocktail_name, ingredient_tuples in recipes.iteritems():
        recipe = {}
        for ingredient_tuple in ingredient_tuples:
            name = ingredient_tuple[0]
            name = canonical_ingredient_name(name)
            amount = amount_associations[ingredient_tuple[1]]
            if amount == 0:
                continue
            if name in recipe:
                recipe[name] += amount
            else:
                recipe[name] = amount
        recipe_dict[cocktail_name] = recipe
    dataframe = pd.DataFrame(recipe_dict).fillna(0).transpose()

    if minimum_occurrences > 0:
        ingredients_with_support = (dataframe > 0).sum(0) >= minimum_occurrences
        dataframe = dataframe.loc[:, ingredients_with_support]
        recipes_with_items = (dataframe > 0).sum(1) > 0
        dataframe = dataframe.loc[recipes_with_items, :]

    if normalization is Normalization.EXACT_AMOUNTS:
        pass
    elif normalization is Normalization.BOOLEAN:
        dataframe[dataframe > 0] = 1.0
    elif normalization is Normalization.ROW_SUM_ONE:
        dataframe = dataframe.div(dataframe.sum(axis=1), axis=0)
    elif normalization is Normalization.TFIDF:
        dataframe[dataframe > 0] = 1.0
        dataframe = tfidf_recipe_matrix(dataframe)

    return dataframe


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
    idx = 0
    for title, recipe in recipes.iteritems():
        print "-------" + str(idx + 1) + "-------"
        print title
        for tup in recipe:
            print tup
        for tup in recipe:
            key = tup[1]
            if key not in associations:
                if tup[0] == 'cherry' \
                        or tup[0] == 'Maraschino cherry' \
                        or tup[0] == 'black cherry' \
                        or tup[0] == 'green cherry' \
                        or tup[0] == 'red cherry':
                    associations[key] = .5
                    continue
                if tup[0] == 'olive':
                    associations[key] = .5
                    continue
                if tup[0] == 'lemon twist':
                    associations[key] = .5
                    continue
                if tup[0] == 'lemon wedge' \
                        or tup[0] == 'lemon slice' \
                        or tup[0] == 'slice of lemon':
                    associations[key] = 1.0
                    continue
                if tup[0] == 'pineapple slice':
                    associations[key] = 1.5
                    continue
                if tup[0] == 'pineapple spear':
                    associations[key] = 3
                    continue
                if tup[0] == 'orange slice' or tup[0] == 'slice of orange':
                    associations[key] = 1.5
                    continue
                if tup[0] == 'lime wheel':
                    associations[key] = 1.0
                    continue
                if tup[0] == 'nutmeg' or tup[0] == 'cinnamon':
                    associations[key] = 0.03125
                    continue
                if tup[0] == 'garnish':
                    associations[key] = 0
                    continue
                if key.find('Substitute:') >= 0:
                    associations[key] = 0
                    continue

                print "Give amount for: " + tup[0]
                print tup[1]
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
            print "***%f done***" % (idx*1.0/len(recipes))
        idx += 1
    pickle.dump(associations, open(AMOUNT_PARSING_GUIDE, 'wb'))


def canonical_ingredient_name(string_):
    """
    Converts a raw string from the ingredient file into its canonical name.
    This step also merges what we judge to be identical ingredients into a
    single name.
    """
    correction_map = {u'tabasco_sauce': u'tabasco',
                      u'muscatel_wine': u'muscat',
                      u'rhine_wine': u'red_wine',
                      u'wine': u'red_wine',
                      u'muscatel': u'muscat',
                      u'rye_whiskey': u'rye',
                      u'yolk_of_egg': u'egg_yolk',
                      u'yolk_of_an_egg': u'egg_yolk',
                      u'yolk_of__egg': u'egg_yolk',
                      u'whole_egg': u'egg',
                      u'eggs': u'egg',
                      u'white_of_an_egg': u'egg_white',
                      u'mint_sprigs': u'mint',
                      u'mint_leaves': u'mint',
                      u'mint_leaf': u'mint',
                      u'mint_sprig': u'mint',
                      u'peppermint': u'mint',
                      u'sprigs_of_mint': u'mint',
                      u'roses_lime_juice': u'lime_cordial',
                      u'lime_syrup': u'lime_cordial',
                      u'lime_wedges': u'lime',
                      u'limes': u'lime',
                      u'lime_wedge': u'lime',
                      u'lime_shell': u'lime',
                      u'lime_or_lemon_juice': u'lemon_or_lime_juice',
                      u'twist_of_lemon': u'lemon_twist',
                      u'slice_of_lemon': u'lemon',
                      u'lemon_wedge': u'lemon',
                      u'vat_69': u'scotch',
                      u'scotch_whisky': u'scotch',
                      u'johnny_walker': u'scotch',
                      u'johnnie_walker_red_label': u'scotch',
                      u'whisky': u'scotch',
                      u'black_and_white_whisky': u'scotch',
                      u'white_horse_whisky': u'scotch',
                      u'king_george_iv_whisky': u'scotch',
                      u'bourbon_whisky': u'bourbon',
                      u'canadian_whiskey': u'canadian_whisky',
                      u'canadian_club_whisky': u'canadian_whisky',
                      u'canadian_club': u'canadian_whisky',
                      u'seagrams_vo': u'canadian_whisky',
                      u'vo': u'canadian_whisky',
                      u'blended_whiskey': u'whiskey',
                      u'tennessee_whiskey': u'whiskey',
                      u'pat_of_butter': u'butter',
                      u'tomato_catsup': u'catsup',
                      u'gomme': u'gomme_syrup',
                      u'gum_syrup': u'gomme_syrup',
                      u'cream_of_coconut': u'coconut_cream',
                      u'cr\xe8me_de_cacao': u'creme_de_cacao',
                      u'cassis': u'creme_de_cassis',
                      u'batavia_arrack': u'arrack',
                      u'courvoisier': u'cognac',
                      u'spanish_brandy': u'brandy',
                      u'cape_of_good_hope_brandy': u'brandy',
                      u'ginger_flavored_brandy': u'ginger_brandy',
                      u'blackberry_flavored_brandy': u'blackberry_brandy',
                      u'peach_flavored_brandy': u'peach_brandy',
                      u'cherry_flavored_brandy': u'cherry_brandy',
                      u'apricot_flavored_brandy': u'apricot_brandy',
                      u'coffee_flavored_brandy': u'coffee_brandy',
                      u'hot_coffee': u'coffee',
                      u'simple_syrup': u'syrup',
                      u'sugar_syrup': u'syrup',
                      u'sugar_lump': u'sugar',
                      u'pimms_cup': u'pimms',
                      u'bitters': u'angostura_bitters',
                      u'angostura': u'angostura_bitters',
                      u'peychaud':u'peychaud_bitters',
                      u'pernod': u'pastis',
                      u'half_amp_half': u'half_and_half',
                      u'worcester_sauce': u'worcestershire',
                      u'worcestershire_sauce': u'worcestershire',
                      u'kirschwasser': u'cherry_brandy',
                      u'vanilla': u'vanilla_extract',
                      u'wild_turkey_101': u'bourbon',
                      u'cinzano_vermouth': u'sweet_vermouth',
                      u'noilly_prat': u'dry_vermouth',
                      u'bianco_vermouth': u'sweet_vermouth',
                      u'vermouth_sweet': u'sweet_vermouth',
                      u'vermouth_dry': u'dry_vermouth',
                      u'italian_vermouth': u'sweet_vermouth',
                      u'french_vermouth': u'dry_vermouth',
                      u'pineapple_chunks': u'pineapple',
                      u'pineapple_spear': u'pineapple',
                      u'pineapple_chunk': u'pineapple',
                      u'pineapple_slices': u'pineapple',
                      u'slice_of_pineapple': u'pineapple',
                      u'slices_of_pineapple': u'pineapple',
                      u'pineapple_slice': u'pineapple',
                      u'piece_of_pineapple': u'pineapple',
                      u'port_wine': u'port',
                      u'kirsch': u'cherry_brandy',
                      u'tia_maria': u'coffee_liqueur',
                      u'khalua': u'coffee_liqueur',
                      u'slivovitz': u'plum_brandy',
                      u'gordons_gin': u'dry_gin',
                      u'orange_flavored_gin': u'orange_gin',
                      u'bombay_gin': u'dry_gin',
                      u'london_dry_gin': u'dry_gin',
                      u'seagrams_gin': u'dry_gin',
                      u'english_gin': u'dry_gin',
                      u'geneva_gin': u'genever_gin',
                      u'hollands_gin': u'genever_gin',
                      u'jamaican_ginger_extract': u'jamaica_ginger',
                      u'bacardi_rum_light': u'light_rum',
                      u'bacardi_light_rum': u'light_rum',
                      u'myerss_rum': u'dark_rum',
                      u'rum_pampero': u'dark_rum',
                      u'appleton_special_rum': u'jamaican_rum',
                      u'white_rum': u'light_rum',
                      u'dagger_rum': u'jamaican_rum',
                      u'jamaica_rum': u'jamaican_rum',
                      u'st_james_rum': u'martinique_rum',
                      u'golden_rum': u'gold_rum',
                      u'aurum_liqueur': u'aurum',
                      u'bacardi_151': u'151_rum',
                      u'151_proof_rum': u'151_rum',
                      u'malibu_rum': u'coconut_liqueur',
                      u'mount_gay_barbados_rum': u'barbados_rum'}
    string_ = string_.replace('fresh', '').strip()
    string_ = re.sub(ur"\p{P}+", "", string_)
    string_ = string_.lower().replace(' ', '_')
    if string_ in correction_map:
        return correction_map[string_]
    return string_


def print_ingredient_counts():
    """
    This is a debugging function that prints out counts of each ingredient.
    It was created to help give me a better idea about how much progress
    was being made on merging similar ingredients.
    """
    bool_matrix = recipe_data(Normalization.BOOLEAN)
    names = list(bool_matrix.columns)
    ingredient_sums = np.sum(bool_matrix, axis=0)
    ingredient_counts = zip(names, ingredient_sums)
    sorted_ingredient_counts = sorted(ingredient_counts, key=lambda x: x[1])
    for item in sorted_ingredient_counts:
        if 'rose' in item[0]:
            print item


if __name__ == '__main__':
    print "The only reason you should be running this is for testing purposes."
    #build_amount_parsing_guide()
    #ingredients_flavor_dict()
    print_ingredient_counts()
