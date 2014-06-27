"""
Methods that factor and subsequently operate on matrices, as well as
tools to display the factors. For example, NMF, PCA.
"""

# To ignore numpy errors:
#     pylint: disable=E1101

import numpy as np
from sklearn.decomposition import ProjectedGradientNMF
import matplotlib.pyplot as plt

from src.data_processing.matrix_generation import recipe_matrix


BEST_N_COMPONENTS_FOR_EXACT_AMOUNTS = 20
BEST_N_COMPONENTS_FOR_INEXACT_AMOUNTS = 105


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


def print_top_components(components, name_index):
    """
    Prints a summary of the top components from NMF
    """
    for idx, component in enumerate(components):
        print '-----------'
        print 'Component %d' % idx
        parts_to_display = 10
        top_n_indices = np.argsort(-1*component)[0:parts_to_display]
        for i in top_n_indices:
            print '\t %s: %d' % (name_index.get_ingred(i), component[i])


if __name__ == '__main__':
    dirty_test_of_nmf(number_of_components=20, exact_amounts=True)
    #select_component_count_nmf()
