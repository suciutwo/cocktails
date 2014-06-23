import heapq
import numpy as np
from sklearn.decomposition import ProjectedGradientNMF
from matrixGeneration import recipeMatrix
import matplotlib.pyplot as plt


BEST_N_COMPONENTS_FOR_EXACT_AMOUNTS = 155
BEST_N_COMPONENTS_FOR_INEXACT_AMOUNTS = 105

'''
Adjust the range to see reconstruction_err_ at different n_components.
'''
def select_component_count_NMF():
	m, inex = recipeMatrix(exact_amounts=True)
	ing_by_ing = np.transpose(m).dot(m)
	rng = range(80, 200, 25)
	results = []
	for i in rng:
		model = ProjectedGradientNMF(n_components=i, init='random', random_state=0)
		model.fit(ing_by_ing)	
		print i, model.reconstruction_err_
		results.append(model.reconstruction_err_)
	plt.plot(rng, results)
	plt.savefig(open('results/NMF_tradeoff_curve', 'w'))


'''
First test of NMF
'''
def dirty_test_of_NMF(number_of_components, exact_amounts):
	m, index = recipeMatrix(exact_amounts=exact_amounts)
	ing_by_ing = np.transpose(m).dot(m)
	model = ProjectedGradientNMF(n_components=number_of_components, init='random', random_state=0)
	model.fit(ing_by_ing)
	print_top_components(model.components_, index)	
	
'''
Prints a summary of the top components from NMF
'''
def print_top_components(components, name_index):
	for idx, component in enumerate(components):
		print '-----------'
		print 'Component %d' % idx
		n = 10
		top_n_indices = np.argsort(-1*component)[0:n]
		for i in top_n_indices:
			print '\t %s: %d' % (name_index.get_ingred(i), component[i])
	

if __name__ == '__main__':
	dirty_test_of_NMF(BEST_N_COMPONENTS_FOR_EXACT_AMOUNTS, False)
	#select_component_count_NMF()