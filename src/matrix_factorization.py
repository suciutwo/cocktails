"""
Methods that factor and subsequently operate on matrices, as well as
tools to display the factors. For example, NMF, PCA.
"""

# To ignore numpy errors:
#     pylint: disable=E1101
import pickle
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.decomposition import ProjectedGradientNMF
from sklearn.feature_extraction.text import TfidfVectorizer
from tsne import bh_sne

from emma.data_formatting import top_ingredient_combinations
from emma.data_formatting import render_ingredient_as_single_word
from src.data_processing.matrix_generation import recipe_matrix
from src.data_processing.parse_pages import CLEANED_COCKTAILS_FILENAME
from src.data_visualization.create_plot import print_top_components
from src.data_visualization.create_plot import emma_matrix_plot

BEST_N_COMPONENTS_FOR_EXACT_AMOUNTS = 20
BEST_N_COMPONENTS_FOR_INEXACT_AMOUNTS = 105


def rough_translation_of_emmas_pca(verbose=True):
    """
    I tried to translate emma's code here.
    """
    # TODO: get rid of this
    recipes = pickle.load(open(CLEANED_COCKTAILS_FILENAME))
    use_tfidf = True
    use_pca = True
    # TODO: remove dangerous file reading outside data gen
    ingredient_pairs = top_ingredient_combinations()
    if use_tfidf:
        tfidf = TfidfVectorizer()
        all_recipes = []
        for name, ingredient_tuples in recipes.iteritems():
            ingredient_string_array = [render_ingredient_as_single_word(ingredient[0]).decode('utf-8') for ingredient in ingredient_tuples]
            recipe_string = ' '.join(ingredient_string_array)
            all_recipes.append(recipe_string)
        matrix = tfidf.fit_transform(all_recipes).toarray()
        ingredients = tfidf.get_feature_names()
    else:
        print "NOT IMPLEMENTED"
        return

    if use_pca:
        n_components = 2
        model = PCA(n_components=n_components, whiten=False)
        # model = SparsePCA(n_components = n_components, alpha = .5)
        small_matrix = model.fit_transform(matrix.transpose())
    else:
        small_matrix = bh_sne(matrix.transpose())

    emma_matrix_plot(small_matrix, ingredients, ingredient_pairs)

    if verbose:
        print small_matrix


def select_component_count_nmf():
    """
    Adjust the range to see reconstruction_err_ at different n_components.
    """
    matrix = recipe_matrix(exact_amounts=True)
    rng = range(10, 200, 10)
    results = []
    for i in rng:
        model = ProjectedGradientNMF(
            n_components=i, init='random', random_state=0)
        model.fit(matrix)
        print i, model.reconstruction_err_
        results.append(model.reconstruction_err_)
    plt.plot(rng, results)
    plt.savefig(open('results/NMF_tradeoff_curve', 'w'))


def dirty_test_of_nmf(number_of_components, exact_amounts):
    """
    First test of NMF
    """
    matrix, index = recipe_matrix(exact_amounts=exact_amounts)
    matrix = np.transpose(matrix).dot(matrix)
    model = ProjectedGradientNMF(
        n_components=number_of_components, init='random', random_state=0)
    model.fit(matrix)
    components = model.components_
    print_top_components(components, index)





if __name__ == '__main__':
    # dirty_test_of_nmf(number_of_components=20, exact_amounts=False)
    # select_component_count_nmf()
    rough_translation_of_emmas_pca()