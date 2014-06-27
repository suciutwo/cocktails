"""
Call these functions to make pretty displays.
"""

import matplotlib.pyplot as plt
import numpy as np

RESULT_DIRECTORY = 'results/'


def print_top_components(components, name_index):
    """
    Prints a summary of the top components of a matrix factorization.
    :param components: a matrix with dimensions (components)x(features).
    Each row is a single component and contains information about which
    features make up that component. This is most typically generated
    as the components_ element of a scikit decomposition model.
    :param name_index: the RecipeNameIndex corresponding to the matrix
    that was used to generate these components. It's on you to make sure you're
    using the right RecipeNameIndex. If not, the mapping between items and
    names will be wonky and you'll be in tears.
    """
    for idx, component in enumerate(components):
        print '-----------'
        print 'Component %d' % idx
        parts_to_display = 10
        top_n_indices = np.argsort(-1*component)[0:parts_to_display]
        for i in top_n_indices:
            print '\t %s: %d' % (name_index.get_ingred(i), component[i])




def emma_matrix_plot(two_component_matrix, ingredients, ingredient_pairs,
                     threshold=10, replace_values_with_rank=True, use_tfidf=True):
    """

    :param two_component_matrix:
    :param ingredients:
    :param ingredient_pairs:
    :param threshold:
    :param replace_values_with_rank: boolean that forces values of each
     component to be replaced with their relative rank (descending).
    :param use_tfidf:
    """
    [number_of_items, number_of_components] = two_component_matrix.shape

    two_component_matrix = shift_column_values(two_component_matrix, .001)
    if replace_values_with_rank:
        two_component_matrix = replace_values_with_ranking(two_component_matrix)

    print len(ingredients)
    print number_of_items

    ingredient_dict = dict(zip(ingredients, range(len(ingredients))))

    plt.figure(figsize=[50, 50])
    for i in range(number_of_items):
        point = [two_component_matrix[i, :]]
        plt.annotate(ingredients[i], point)

    n_lines_plotted = 0
    for pair in ingredient_pairs:
        if ingredient_pairs[pair] > threshold:
            try:
                a1, a2 = pair.split('/')
                p1 = two_component_matrix[ingredient_dict[a1]]
                p2 = two_component_matrix[ingredient_dict[a2]]
                plt.plot([p1[0], p2[0]], [p1[1], p2[1]], color = 'red')
                n_lines_plotted += 1
            except:
                continue
    print 'Number of connections passing threshold', n_lines_plotted
    plt.scatter(two_component_matrix[:, 0], two_component_matrix[:, 1])
    plt.xlim([min(two_component_matrix[:, 0]), max(two_component_matrix[:, 0])*1.1])
    plt.ylim([min(two_component_matrix[:, 0]), max(two_component_matrix[:, 0])*1.1])


    if use_tfidf:
        filename = 'PCA_tf_idf-beforehack.png'
    else:
        filename = 'impossible.png'

    plt.savefig(RESULT_DIRECTORY + filename)


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
