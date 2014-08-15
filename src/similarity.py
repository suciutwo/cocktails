"""
Code to measure similarity between ingredients and between drinks.
"""

import scipy.spatial.distance as dist

from src.data_processing.matrix_generation import recipe_matrix, Normalization
from src.matrix_factorization import reduce_dimensions, ReductionTypes


def similar_ingredients(ingredient):
    """
    First pass prototype of finding similar ingredients.
    :return:
    """
    recipe_ingredient_matrix, index = recipe_matrix(Normalization.EXACT_AMOUNTS)
    ingredient_recipe_matrix = recipe_ingredient_matrix.transpose()
    reduced_matrix = reduce_dimensions(ingredient_recipe_matrix,
                                       ReductionTypes.PCA,
                                       20)
    similarity_array = dist.pdist(reduced_matrix, 'cosine')
    similarity_matrix = dist.squareform(similarity_array)

    number = index.ingredient_number(ingredient)
    print "Looking for buddy of " + ingredient + " (no. " + str(number) + ")"
    similarity_values = similarity_matrix[number]
    names = [index.ingredient(i) for i in range(index.ingredients_count())]
    ingredient_counts = zip(names, similarity_values)
    sorted_ingredient_counts = sorted(ingredient_counts, key=lambda x: -x[1])
    for item in sorted_ingredient_counts:
        print item


