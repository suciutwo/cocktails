"""
Code to measure similarity between ingredients and between drinks.
"""

import scipy.spatial.distance as dist

from src.data_processing.matrix_generation import recipe_matrix, Normalization
from src.matrix_factorization import reduce_dimensions, ReductionTypes


def generate_ingredient_similarity():
    """
    Builds a matrix that showcases ingredient-ingredient similarity.
    :return:
    """
    recipe_ingredient_matrix, index = recipe_matrix(Normalization.ROW_SUM_ONE)
    ingredient_recipe_matrix = recipe_ingredient_matrix.transpose()
    reduced_matrix = reduce_dimensions(ingredient_recipe_matrix,
                                       ReductionTypes.PCA,
                                       20)
    similarity_array = dist.pdist(reduced_matrix, 'cosine')
    similarity_matrix = dist.squareform(similarity_array)
    return index, similarity_matrix


def print_similar(index, ingredient, similarity_matrix):
    """
    Prints similar ingredients, using:
    :param index: a RecipeNameIndex
    :param ingredient: the string for the similar ingredient
    :param similarity_matrix: created via generate_ingredient_similarity
    :return:
    """
    number = index.ingredient_number(ingredient)
    print "Looking for buddy of " + ingredient + " (no. " + str(number) + ")"
    similarity_values = similarity_matrix[number]
    names = [index.ingredient(i) for i in range(index.ingredients_count())]
    ingredient_counts = zip(names, similarity_values)
    sorted_ingredient_counts = sorted(ingredient_counts, key=lambda x: -x[1])
    for item in sorted_ingredient_counts:
        print item


def ingredient_loop():
    """
    Simple loop, asks for strings and prints similarity.
    :return:
    """
    index, similarity_matrix = generate_ingredient_similarity()

    while True:
        user_ingredient = raw_input("Ingredient: ")
        if user_ingredient == 'q' or user_ingredient == 'quit':
            break
        try:
            print_similar(index, user_ingredient, similarity_matrix)
        except KeyError:
            print "Don't have that ingredient."


if __name__ == '__main__':
    ingredient_loop()

