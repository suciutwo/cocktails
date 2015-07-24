"""
Constructs a tree that classifies drinks, saves it as JSON
"""

from scipy.spatial.distance import cosine

import src.data_processing.matrix_generation as generator
from src.data_processing.matrix_generation import Normalization
from src.matrix_factorization import calculate_components, ReductionTypes
from src.data_visualization.create_plot import print_top_components, print_component


class HierarchyNode:
    """
    Building blocks of the tree.
    """

    def __init__(self):
        self.question = None
        self.title = None
        self.children = []
        self.drinks = None


def is_too_small(matrix):
    return len(matrix) < 50


# to be reconsidered


def nmf_factors(matrix, n_factors):
    return calculate_components(matrix, ReductionTypes.NMF, n_factors)


def get_all_drinks(frame):
    return [name for name in frame.index]


def any_are_substring(target, options):
    for option in options:
        if option in target:
            return True
    return False


def get_ingredient_indices(frame, using_words, without_words):
    indices = []
    for index, ingredient in enumerate(list(frame.columns)):
        if any_are_substring(ingredient, using_words):
            if any_are_substring(ingredient, without_words):
                continue
            indices.append(index)
    return indices


def build_hierarchy(matrix):
    root = HierarchyNode()
    top_elements = [['gin'], 
                    ['rum'],
                    ['whiskey', 'whiskey', 'bourbon', 'scotch'],
                    ['tequila'],
                    ['wine']
                    
    ]
    root.question = "Base?"
    for search_terms in top_elements:
        gin_indices = get_ingredient_indices(matrix, search_terms, [])
        has_gin = (matrix.ix[:, gin_indices] > 0).sum(1) > 0
        gin_only_recipes = matrix.loc[has_gin, :]
        child = HierarchyNode()
        child.title = search_terms[0]
        current_answers = [root.question, child.title]
        grandchild = split_matrix_into_nodes(gin_only_recipes, 0, current_answers)
        if grandchild:
            child.children.append(grandchild)
        else:
            child.drinks = get_all_drinks(gin_only_recipes)
        root.children.append(child)
    return root


def split_matrix_into_nodes(frame, depth, parent_answers):
    print "NEW CALL TO SPLIT", frame.shape
    if is_too_small(frame) or depth > 3:
        return None

    root = HierarchyNode()
    n_factors = 5
    factors = None
    while True:
        factors = nmf_factors(frame, n_factors)
        print_top_components(factors, frame.columns, {})
        root.question = raw_input("Overall name for question? (%d drinks here) (%s)) " 
                                  % (len(frame), ' '.join(parent_answers)))
        if not root.question:
            return None
        if root.question.isdigit():
            n_factors = int(root.question)
            print "RERUNNING WITH", n_factors, "FACTORS INSTEAD"
        else:
            break

    final_factors = {}
    for index, factor in enumerate(factors):
        print_component(factor, frame.columns, {}, index)
        factor_label = raw_input("Name for factor %d: " % (index + 1))
        if factor_label:
            print "factor", index + 1, "named", factor_label
            if factor_label in final_factors:
                final_factors[factor_label]['factors'].append(factor)
            else:
                final_factors[factor_label] = {
                    'factors': [factor],
                    'indices': []}
    if not final_factors:
        return None

    for row_number in range(frame.shape[0]):
        row = frame.ix[row_number, :]
        print row.name
        minimum_distance = None
        minimum_label = None
        for label, data in final_factors.iteritems():
            factors = data['factors']
            for factor in factors:
                distance = cosine(row, factor)
                print distance
                if not minimum_distance or distance < minimum_distance:
                    minimum_distance = distance
                    minimum_label = label
        for label, data in final_factors.iteritems():
            if minimum_label == label:
                data['indices'].append(row_number)
                break

    final_factors = {label: data for label, data in final_factors.iteritems()
                     if data['indices']}

    for label, data in final_factors.iteritems():
        child = HierarchyNode()
        child.title = label
        relevant_rows = frame.ix[data['indices'], :]
        print "RECURSIVE CALL FOR", relevant_rows.shape
        current_answers = list(parent_answers)
        current_answers.append(root.question)
        current_answers.append(child.title)
        grandchild = split_matrix_into_nodes(relevant_rows, depth + 1, current_answers)
        if grandchild:
            child.children.append(grandchild)
        else:
            child.drinks = get_all_drinks(relevant_rows)
        root.children.append(child)

    return root


def run():
    # Safely load tree from disk (or recreate)
    import pickle

    try:
        tree = pickle.load(open('tree.pickle', 'rb'))
    except:
        matrix = generator.recipe_data(Normalization.EXACT_AMOUNTS)
        tree = build_hierarchy(matrix)
        pickle.dump(tree, open('tree.pickle', 'wb'))

    # Save it as JSON
    import jsonpickle

    jsonpickle.set_encoder_options('simplejson', sort_keys=True, indent=2)
    f = open('tree.json', 'wb')
    f.write(jsonpickle.encode(tree))


if __name__ == '__main__':
    run()


