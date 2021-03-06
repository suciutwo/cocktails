"""
Methods that factor and subsequently operate on matrices, as well as
tools to display the factors. For example, NMF, PCA.
"""

# To ignore numpy errors:
#     pylint: disable=E1101

from enum import Enum
import pickle
from sklearn.decomposition import PCA
from sklearn.decomposition import ProjectedGradientNMF
from sklearn.decomposition import SparsePCA
from tsne import bh_sne

import src.constants as constants
from src.data_processing.matrix_generation import ingredients_flavor_dict
from src.data_processing.matrix_generation import recipe_data
from src.data_processing.matrix_generation import Normalization
from src.data_visualization.create_plot import print_top_components
from src.data_visualization.create_plot import plot_2d_points


COMPONENTS_FILENAME_PREFIX = constants.DATA_DIRECTORY + 'components_'


class ReductionTypes(Enum):
    """
    Types of dimensionality reduction that are possible.
    Not all can be played with in the same fashion.
    """
    PCA = 1
    sPCA = 2
    T_SNE = 3
    NMF = 4


def reduce_dimensions(matrix, reduction_type, n_components):
    """
    Reduces the dimensionality of a matrix and returns it.
    :param matrix: The matrix to reduce.
    :param reduction_type: The style of reduction to carry out.
    :param n_components: The number of components to allow.
    :return: A matrix whose dimensionality has been reduced.
    """
    reduced_matrix = None
    if reduction_type is ReductionTypes.PCA:
        model = PCA(n_components=n_components, whiten=False)
        reduced_matrix = model.fit_transform(matrix)
    elif reduction_type is ReductionTypes.sPCA:
        model = SparsePCA(n_components=n_components, alpha=.5)
        reduced_matrix = model.fit_transform(matrix)
    elif reduction_type is ReductionTypes.T_SNE:
        reduced_matrix = bh_sne(matrix.transpose())
    elif reduction_type is ReductionTypes.NMF:
        model = ProjectedGradientNMF(n_components=n_components,
                                     init='nndsvd',
                                     random_state=0)
        reduced_matrix = model.fit_transform(matrix)
    return reduced_matrix


def calculate_components(matrix, reduction_type, n_components):
    """
    Returns the components that make up a decomposition.
    :param matrix: The matrix to reduce.
    :param reduction_type: The style of reduction to carry out.
    :param n_components: The number of components to allow.
    :return: A components_ object that describes how the reduction
    conceives of the matrix.
    """
    components = None
    if reduction_type is ReductionTypes.PCA:
        model = PCA(n_components=n_components, whiten=False)
        components = model.fit(matrix).components_
    elif reduction_type is ReductionTypes.sPCA:
        model = SparsePCA(n_components=n_components, alpha=.5)
        components = model.fit(matrix).components_
    elif reduction_type is ReductionTypes.T_SNE:
        raise Exception('Components not implemented for T_SNE.')
    elif reduction_type is ReductionTypes.NMF:
        model = ProjectedGradientNMF(n_components=n_components,
                                     init='nndsvd',
                                     random_state=0)
        components = model.fit(matrix).components_
    return components


def visualize_reduced_dimensions(reduction_type,
                                 normalization,
                                 minimum_occurrences=0):
    """
    Reduces the (drink)x(ingredient) matrix to 2 dimensions
    and makes a plot of the ingredients projected into that space.
    2d only because higher dimensions are harder to visualize.
    :param reduction_type: the way you will reduce dimensionality.
    :param normalization: method to normalize matrix
    :param minimum_occurrences: minimum required number of ingredient occurrence
    Saves the visualisation as an image file.
    """
    drink_ingredient = recipe_data(normalization, minimum_occurrences)
    ingredients = list(drink_ingredient.columns)
    ingredient_drink = drink_ingredient.transpose()
    output_filename = reduction_type.name+'-'+normalization.name
    two_component_matrix = reduce_dimensions(ingredient_drink,
                                             reduction_type, 2)
    plot_2d_points(two_component_matrix, ingredients, output_filename)


def inspect_components(reduction_type, normalization):
    """
    Allows the user to interacted with a saved list of matrix components.
    :param reduction_type: The type of decomposition to use
    Asks user to enter queries to see components
    """
    dump_filename = COMPONENTS_FILENAME_PREFIX+reduction_type.name + \
        '-' + normalization.name
    components = pickle.load(open(dump_filename, 'r'))
    names = components[0]
    flavor_index = ingredients_flavor_dict()
    n_components = 1
    while True:
        user_input = raw_input('Jump to: ')
        if user_input is 'q':
            break
        elif user_input is 'j':
            if n_components > 1:
                n_components -= 1
        elif user_input is 'k':
            if n_components < len(components) - 1:
                n_components += 1
        else:
            try:
                desired_component = int(user_input)
                if 1 <= desired_component <= len(components) - 1:
                    n_components = desired_component
            except ValueError:
                print "Please enter a number or j/k."
                continue
        print '\n\n\n'
        print 'Result for %d components' % n_components
        print_top_components(components[n_components], names, flavor_index)


def generate_all_components(reduction_type, normalization, values_to_generate,
                            minimum_occurrences=0):
    """
    Carries out a dimensionality reduction using 1:n_components components.
    All results are saved in a list so that they can be easily inspected later.
    :param reduction_type: The kind of reduction to use.
    :param normalization: How to normalize the matrix before finding components.
    :param values_to_generate: numbers of components to calculate.
    :param minimum_occurrences: number of times an ingredient must be found.
    AFTER A VERY LONG TIME this pickles a dictionary of components.
    """
    data = recipe_data(normalization, minimum_occurrences)
    names = list(data.columns)
    components = [names]
    print 'Calculating all components for %s' % reduction_type.name
    for number in values_to_generate:
        print 'Calculating components for %d dimensions' % number
        components.append(calculate_components(data, reduction_type, number))
    dump_filename = COMPONENTS_FILENAME_PREFIX + reduction_type.name + \
        '-' + normalization.name
    pickle.dump(components, open(dump_filename, 'w'))


if __name__ == '__main__':
    numbers = [1, 3, 5, 10, 20, 50, 100]

    # generate_all_components(ReductionTypes.NMF,
    #                         Normalization.ROW_SUM_ONE,
    #                         numbers,
    #                         10)

    # for reduction in ReductionTypes:
    #     if reduction is ReductionTypes.T_SNE:
    #         continue
    #     visualize_reduced_dimensions(reduction,
    #                                  Normalization.ROW_SUM_ONE,
    #                                  10)
    #
    # for reduction in ReductionTypes:
    #     if reduction is not ReductionTypes.T_SNE:
    #         generate_all_components(reduction)
    inspect_components(ReductionTypes.NMF, Normalization.EXACT_AMOUNTS)
