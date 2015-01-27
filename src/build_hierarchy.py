"""
Constructs a tree that classifies drinks
"""


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
        self.answers = []
        self.drinks = None
     
        
class Answer:
    """
    Data that points to the next node and names it.
    """
    def __init__(self):
        self.title = None
        self.node = None


def is_too_small(matrix):
    return len(matrix) < 20
#Tocheck


def nmf_factors(matrix, n_factors):
    return calculate_components(matrix, ReductionTypes.NMF, n_factors)


def get_all_drinks(frame):
    return [name for name in frame.index]


def split_matrix_into_nodes(frame, depth, parent_answers):
    print "NEW CALL TO SPLIT", frame.shape
    if is_too_small(frame) or depth > 2:
        terminal_node = HierarchyNode()
        terminal_node.is_terminal = True
        terminal_node.question = parent_answers[-1]
        terminal_node.drinks = get_all_drinks(frame)
        return terminal_node
    
    root = HierarchyNode()
    factors = nmf_factors(frame, 5)
    print_top_components(factors, frame.columns, {})
    root.question = raw_input("Overall name for question? (" + ' '.join(parent_answers) + ") ")

    final_factors = []
    for index, factor in enumerate(factors):
        print_component(factor, frame.columns, {}, index)
        factor_label = raw_input("Name for factor " + str(index+1) + ": ")
        if factor_label:
            print "factor", index+1, "named", factor_label
            factor_data = {'label': factor_label, 
                           'factor': factor, 
                           'indices': []}
            final_factors.append(factor_data)
    
    for row_number in range(frame.shape[0]):
        row = frame.ix[row_number, :]
        print row.name
        maximum_product = 0
        maximum_label = None
        for data in final_factors:
            factor = data['factor']
            result = row.dot(factor)
            print result
            if result > maximum_product:
                maximum_product = result
                maximum_label = data['label']
        for data in final_factors:
            if maximum_label == data['label']:
                data['indices'].append(row_number)
                break

    for data in final_factors:
        answer = Answer()
        answer.title = data['label']
        relevant_rows = frame.ix[data['indices'], :]
        print "RECURSIVE CALL FOR", relevant_rows.shape
        current_answers = list(parent_answers)
        current_answers.append(root.question)
        current_answers.append(answer.title)
        answer.node = split_matrix_into_nodes(relevant_rows, depth + 1, current_answers)
    
    return root
        
        
matrix = generator.recipe_data(Normalization.EXACT_AMOUNTS)
tree = split_matrix_into_nodes(matrix, 0, [])
