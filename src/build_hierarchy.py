"""
Constructs a tree that classifies drinks, saves it as JSON
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
        self.title = None
        self.children = []
        self.drinks = None


def is_too_small(matrix):
    return len(matrix) < 20
# to be reconsidered


def nmf_factors(matrix, n_factors):
    return calculate_components(matrix, ReductionTypes.NMF, n_factors)


def get_all_drinks(frame):
    return [name for name in frame.index]


def split_matrix_into_nodes(frame, depth, parent_answers):
    print "NEW CALL TO SPLIT", frame.shape
    if is_too_small(frame) or depth > 1:
        return None
    
    root = HierarchyNode()
    n_factors = 5
    while True:
        factors = nmf_factors(frame, n_factors)
        print_top_components(factors, frame.columns, {})
        root.question = raw_input("Overall name for question? (" + ' '.join(parent_answers) + ") ")
        if root.question.isdigit():
            n_factors = int(root.question)
            print "RERUNNING WITH", n_factors, "FACTORS INSTEAD"
        else:
            break
            

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
        child = HierarchyNode()
        child.title = data['label']
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
        tree = split_matrix_into_nodes(matrix, 0, [])
        pickle.dump(tree, open('tree.pickle', 'wb'))
    
    # Save it as JSON
    import jsonpickle
    jsonpickle.set_encoder_options('simplejson', sort_keys=True, indent=2)
    f = open('tree.json', 'wb')
    f.write(jsonpickle.encode(tree))
    
if __name__ == '__main__':
    run()


