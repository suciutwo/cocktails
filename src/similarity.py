"""
Code to measure similarity between ingredients and between drinks.
"""

import scipy.spatial.distance as dist

from src.data_processing.matrix_generation import recipe_data, Normalization
from src.matrix_factorization import reduce_dimensions, ReductionTypes


def generate_ingredient_similarity():
    """
    Builds a matrix that showcases ingredient-ingredient similarity.
    :return:
    """
    recipe_ingredient = recipe_data(Normalization.EXACT_AMOUNTS, 2)
    names = list(recipe_ingredient.columns)
    ingredient_recipe = recipe_ingredient.transpose()
    reduced_matrix = reduce_dimensions(ingredient_recipe,
                                       ReductionTypes.PCA,
                                       20)
    similarity_array = dist.pdist(reduced_matrix, 'cosine')
    similarity_matrix = dist.squareform(similarity_array)
    return similarity_matrix, names


def print_similar(ingredient, similarity_matrix, names):
    """
    Prints similar ingredients, using:
    :param ingredient: the string for the similar ingredient
    :param similarity_matrix: created via generate_ingredient_similarity
    :param names: list of ingredient names
    :return:
    """
    print "Looking for things similar to", ingredient
    number = names.index(ingredient)
    similarity_values = similarity_matrix[number]
    ingredient_counts = zip(names, similarity_values)
    sorted_ingredient_counts = sorted(ingredient_counts, key=lambda x: -x[1])
    for item in sorted_ingredient_counts:
        print item


def ingredient_loop():
    """
    Simple loop, asks for strings and prints similarity.
    :return:
    """
    similarity_matrix, names = generate_ingredient_similarity()

    while True:
        user_ingredient = raw_input("Ingredient: ")
        if user_ingredient == 'q' or user_ingredient == 'quit':
            break
        try:
            print_similar(user_ingredient, similarity_matrix, names)
        except ValueError:
            print "Don't have that ingredient."


if __name__ == '__main__':
    ingredient_loop()

