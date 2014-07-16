"""
Call these functions to make pretty displays.
"""

# To ignore numpy errors:
#     pylint: disable=E1101

import src.constants as constants
import matplotlib.pyplot as plt
import numpy as np

from emma.data_formatting import top_ingredient_combinations


def print_top_components(components, name_index, flavor_index):
    """
    Prints out a summary of the top components of a matrix factorization.
    :param components: a matrix with dimensions (components)x(features).
    Each row is a single component and contains information about which
    features make up that component. This is most typically generated
    as the components_ element of a scikit decomposition model.
    :param name_index: the RecipeNameIndex corresponding to the matrix
    that was used to generate these components. It's on you to make sure you're
    using the right RecipeNameIndex. If not, the mapping between items and
    names will be wonky and you'll be in tears.
    :param flavor_index: mapping from ingredient names to flavors.
    """
    for idx, component in enumerate(components):
        print '-----------'
        print 'Component %d' % (idx + 1)
        n_ingredients_to_display = min(10, len(component))
        top_n_indices = np.argsort(-1 * component)[0:n_ingredients_to_display]
        for i in top_n_indices:
            ingredient_name = name_index.get_ingred(i)
            weight = component[i]
            flavors = ''
            if ingredient_name in flavor_index:
                flavors = '(%s)' % flavor_index[ingredient_name]
            print '\t %s: %.2f %s' % (ingredient_name, weight, flavors)


def plot_2d_points(two_component_matrix, name_index, output_filename,
                   replace_values_with_rank=True,
                   add_lines_connecting_pairs=False):
    """
    Saves a pretty plot of items in two dimensions. Adds their names, and
    optionally does some data manipulation so that you can see a prettier graph

    :param two_component_matrix: (items)x(2) matrix
    :param name_index: RecipeNameIndex object used to generate matrix
    :param output_filename: name of figure (typically .png), will get stomped
    :param replace_values_with_rank: boolean that forces values of each
     component to be replaced with their relative rank (descending).
    :param add_lines_connecting_pairs: adds a bunch of red lines connecting
    ingredient pairs. Twiddle threshold variable if there are too many
    """
    two_component_matrix = shift_column_values(two_component_matrix, .001)
    if replace_values_with_rank:
        two_component_matrix = replace_values_with_ranking(two_component_matrix)

    plt.figure(figsize=[50, 50])
    for i in range(two_component_matrix.shape[0]):
        point = two_component_matrix[i, :]
        plt.annotate(name_index.get_ingred(i), point)

    if add_lines_connecting_pairs:
        ingredient_pairs = top_ingredient_combinations()
        n_lines_plotted = 0
        threshold = 10
        for pair in ingredient_pairs:
            if ingredient_pairs[pair] > threshold:
                ingred_one, ingred_two = pair.split('/')
                ingred_one_idx = name_index.ingred_idx(ingred_one)
                ingred_two_idx = name_index.ingred_idx(ingred_two)
                point = two_component_matrix[ingred_one_idx]
                endpoint = two_component_matrix[ingred_two_idx]
                plt.plot([point[0], endpoint[0]],
                         [point[1], endpoint[1]],
                         color='red')
                n_lines_plotted += 1
        print 'Threshold for adding lines', threshold
        print 'Number of connections passing threshold', n_lines_plotted

    plt.scatter(two_component_matrix[:, 0], two_component_matrix[:, 1])
    plt.xlim([min(two_component_matrix[:, 0]),
              max(two_component_matrix[:, 0]) * 1.1])
    plt.ylim([min(two_component_matrix[:, 0]),
              max(two_component_matrix[:, 0]) * 1.1])

    plt.savefig(constants.RESULT_DIRECTORY + output_filename + '.png')


def shift_column_values(matrix, minimum_value):
    """
    Utility function to take in a matrix and spit back out a translated
    version where each column has been translated (up or down) by the same
    amount so as to have a minimum_value matching the one specified.
    :param matrix: matrix to operate on
    :param minimum_value: desired minimum value
    :return: matrix with translated columns
    """
    shifted_matrix = matrix
    for column_index in range(matrix.shape[1]):
        smallest_value = shifted_matrix[:, column_index].min()
        shifted_matrix[:, column_index] -= (smallest_value-minimum_value)
    return shifted_matrix


def replace_values_with_ranking(matrix):
    """
    Changes each column of a matrix of floats into a integer ranking of those
    values, in descending order (i.e. 1 is highest float value)
    :param matrix: typically (items)x(components) matrix
    :return: matrix where each column is an ordinal rank from 1:number of rows
    """
    ranking_matrix = matrix
    for component in range(matrix.shape[1]):
        component_values_to_sort = matrix[:, component]
        indices_for_sorting_asc = np.argsort(component_values_to_sort)
        indices_for_sorting_dsc = indices_for_sorting_asc[::-1]
        for rank, item in enumerate(indices_for_sorting_dsc):
            ranking_matrix[item, component] = rank
    return ranking_matrix
