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
from src.data_processing.matrix_generation import recipe_matrix
from src.data_processing.matrix_generation import tfidf_recipe_matrix
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
                                     init='random',
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
                                     init='random',
                                     random_state=0)
        components = model.fit(matrix).components_
    return components


def visualize_reduced_dimensions(reduction_type, use_tfidf=True):
    """
    Reduces the (drink)x(ingredient) matrix to 2 dimensions
    and makes a plot of the ingredients projected into that space.
    2d only because higher dimensions are harder to visualize.
    :param reduction_type: the way you will reduce dimensionality.
    :param use_tfidf: normalize ingredients by frequency
    Saves the visualisation as an image file.
    """
    if use_tfidf:
        matrix, name_index = tfidf_recipe_matrix()
        output_filename = reduction_type.name+'-tfidf'
    else:
        matrix, name_index = recipe_matrix(exact_amounts=False)
        output_filename = reduction_type.name
    two_component_matrix = reduce_dimensions(matrix.transpose(),
                                             reduction_type, 2)
    plot_2d_points(two_component_matrix, name_index, output_filename)


def inspect_components(reduction_type, use_exact_amounts=False):
    """
    Allows the user to interacted with a saved list of matrix components.
    :param reduction_type: The type of decomposition to use
    Asks user to enter queries to see components
    """
    dump_filename = COMPONENTS_FILENAME_PREFIX+reduction_type.name
    if use_exact_amounts:
        dump_filename += '_exact_amounts'
    components = pickle.load(open(dump_filename, 'r'))
    name_index = components[0]
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
        print_top_components(components[n_components], name_index, flavor_index)


def generate_all_components(reduction_type, n_components=200,
                            use_exact_amounts=False):
    """
    Carries out a dimensionality reduction using 1:n_components components.
    All results are saved in a list so that they can be easily inspected later.
    :param reduction_type: The kind of reduction to use.
    :param n_components: The highest number of components to calculate.
    AFTER A VERY LONG TIME this pickles a dictionary of components.
    """
    matrix, name_index = recipe_matrix(exact_amounts=use_exact_amounts)
    components = [name_index]
    print 'Calculating all components for %s' % reduction_type.name
    for number in range(1, n_components+1):
        print 'Calculating component %d' % number
        components.append(calculate_components(matrix, reduction_type, number))
    dump_filename = COMPONENTS_FILENAME_PREFIX + reduction_type.name
    if use_exact_amounts:
        dump_filename += '_exact_amounts'
    pickle.dump(components, open(dump_filename, 'w'))


if __name__ == '__main__':
    # for reduction in ReductionTypes:
    #     visualize_reduced_dimensions(reduction, use_tfidf=False)
    #
    # for reduction in ReductionTypes:
    #     if reduction is not ReductionTypes.T_SNE:
    #         generate_all_components(reduction)
    inspect_components(ReductionTypes.NMF)
