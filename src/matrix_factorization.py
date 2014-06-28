"""
Methods that factor and subsequently operate on matrices, as well as
tools to display the factors. For example, NMF, PCA.
"""

# To ignore numpy errors:
#     pylint: disable=E1101

import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.decomposition import ProjectedGradientNMF
from sklearn.decomposition import SparsePCA
from tsne import bh_sne

from src.data_processing.matrix_generation import recipe_matrix
from src.data_processing.matrix_generation import tfidf_recipe_matrix
from src.data_visualization.create_plot import print_top_components
from src.data_visualization.create_plot import plot_2d_points

BEST_N_COMPONENTS_FOR_EXACT_AMOUNTS = 20
BEST_N_COMPONENTS_FOR_INEXACT_AMOUNTS = 105


def visualize_reduced_dimensions(reduction_type, use_tfidf=True):
    """
    Reduces the (drink)x(ingredient) matrix to two dimensions
    and makes a plot of the ingredients projected into that space.
    """
    if use_tfidf:
        matrix, name_index = tfidf_recipe_matrix()
        filename = reduction_type+'-tfidf'
    else:
        matrix, name_index = recipe_matrix(exact_amounts=False)
        filename = reduction_type

    if reduction_type == 'PCA':
        model = PCA(n_components=2, whiten=False)
        two_component_matrix = model.fit_transform(matrix.transpose())
    elif reduction_type == 'sPCA':
        model = SparsePCA(n_components=2, alpha=.5)
        two_component_matrix = model.fit_transform(matrix.transpose())
    elif reduction_type == 'TSNE':
        two_component_matrix = bh_sne(matrix.transpose())
    elif reduction_type == 'NMF':
        model = ProjectedGradientNMF(n_components=2, init='random',
                                     random_state=0)
        two_component_matrix = model.fit_transform(matrix.transpose())

    plot_2d_points(two_component_matrix, name_index, filename)


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
    visualize_reduced_dimensions("PCA", use_tfidf=False)
    visualize_reduced_dimensions("TSNE", use_tfidf=False)
    visualize_reduced_dimensions("sPCA", use_tfidf=False)
    visualize_reduced_dimensions("NMF", use_tfidf=False)
