import os
import pickle
import heapq
import numpy as np
from sklearn.decomposition import ProjectedGradientNMF
from parsePages import CLEANED_COCKTAILS_FILENAME, CLEANED_INGREDIENTS_FILENAME

AMOUNT_PARSING_GUIDE = 'data/amountParsingMapping'

'''
KEY METHODS:
topNGrams
ingredientsFlavorMatrix
recipeMatrix
'''

'''
Processes the result of parsePages and
returns an ingredients by flavor names matrix (numpy)
'''
def ingredientsFlavorMatrix():
	print "...creating ingredients matrix from file, run parsePages to generate a new version of the file"
	ingredients = pickle.load(open(CLEANED_INGREDIENTS_FILENAME, 'rb'))
	ingredientsFlavorMatrix = np.array(ingredients)
	return ingredientsFlavorMatrix

'''
Processes the result of parsePages and
returns a cocktails by ingredients matrix (numpy)

if exact_amounts, then returns the measurement of each ingredient 
instead of mere presence (i.e. floats instead of [0, 1])
'''
def recipeMatrix(recipe_name_index=None, exact_amounts=True):
	print "Building recipe matrix"
	if os.path.isfile(AMOUNT_PARSING_GUIDE):
		associations = pickle.load(open(AMOUNT_PARSING_GUIDE, 'rb'))
	else:
		print "Couldn't find AMOUNT_PARSING_GUIDE, please run buildAmountParsingMapping first"
		return None
	print "...loading recipe list from file, run parsePages to generate a new version of the file"
	recipes = pickle.load(open(CLEANED_COCKTAILS_FILENAME, 'rb'))
	index = RecipeNameIndex(recipes)
	resulting_matrix = np.zeros(shape=(index.count_cocktails(), index.count_ingreds()))
	for cocktail_name, ingredient_tuples in recipes.iteritems():
		cocktail_idx = index.title_idx(cocktail_name)
		for tup in ingredient_tuples:
			ingred_name = tup[0]
			ingred_idx = index.ingred_idx(ingred_name)
			if exact_amounts:
				ingred_amount = associations[tup[1].strip()+tup[2].strip()]
			else:
				ingred_amount = 1
			resulting_matrix[cocktail_idx, ingred_idx] = ingred_amount
	return resulting_matrix, index


class RecipeNameIndex:
	def __init__(self, recipe_list):
		self.titleToNumber = {}
		self.numberToTitle = {}
		self.ingredToNumber = {}
		self.numberToIngred = {}
		titleIdx = 0
		ingredIdx = 0
		for title, ingredients in recipe_list.iteritems():
			if title not in self.titleToNumber:
				self.titleToNumber[title] = titleIdx
				self.numberToTitle[str(titleIdx)] = title
				titleIdx += 1
			for tup in ingredients:
				ingred_name = tup[0]
				if ingred_name not in self.ingredToNumber:
					self.ingredToNumber[ingred_name] = ingredIdx
					self.numberToIngred[str(ingredIdx)] = ingred_name
					ingredIdx += 1

	def get_name(self, integer_index):
		return self.numberToTitle[str(integer_index)]

	def get_ingred(self, integer_index):
		return self.numberToIngred[str(integer_index)]

	def ingred_idx(self, ingred_name):
		return self.ingredToNumber[ingred_name]

	def title_idx(self, title_string):
		return self.titleToNumber[title_string]

	def count_cocktails(self):
		return len(self.titleToNumber)

	def count_ingreds(self):
		return len(self.ingredToNumber)

			

'''
Creates a map (in AMOUNT_PARSING_GUIDE) that goes from strings -> ingredients. Human generated.
Relies on the result of parsePages
'''
def buildAmountParsingMapping():
	associations = {}
	if os.path.isfile(AMOUNT_PARSING_GUIDE):
		associations = pickle.load(open(AMOUNT_PARSING_GUIDE, 'rb'))
	
	print "...loading recipe list from file, run parsePages to generate a new version of the file"
	recipes = pickle.load(open(CLEANED_COCKTAILS_FILENAME, 'rb'))
	for idx, recipe in enumerate(recipes.values()):
		for tup in recipe:
			print tup
			print " number: " + str(idx+1)
			key = tup[1].strip() + tup[2].strip()
			if not (key in associations):
				print tup[1] + tup[2]
				user_input = raw_input()
				if user_input == 'pass':
					continue
				if user_input == 'quit':
					pickle.dump(associations, open(AMOUNT_PARSING_GUIDE, 'wb'))
					return	
				if user_input == 'err':
					return
				if user_input[0] == 'd': #dash
					associations[key] = len(user_input)*03125 
				elif user_input[0] == 't': #teaspoon
					associations[key] = len(user_input)*0.125
				elif user_input[0] == 'T': #tablespoon
					associations[key] = len(user_input)*0.5
				else:
					associations[key] = float(user_input)
		if (idx % 10 == 0):
			pickle.dump(associations, open(AMOUNT_PARSING_GUIDE, 'wb'))
			print "***%f done***" % (idx*1.0/len(recipes))
	pickle.dump(associations, open(AMOUNT_PARSING_GUIDE, 'wb'))
	

def processIngred(s):
	s = s.replace('fresh', '').strip()
	s = s.translate(string.maketrans("",""), string.punctuation)
	s = s.lower().replace(' ', '_')
	return s


def topNGrams(k = 2, normalize = False, verbose = False):
	recipes = pickle.load(open(CLEANED_COCKTAILS_FILENAME))	
	n_grams = {}
	one_gram_counts = {}
	for recipe in recipes:
		ingredients = [processIngred(ingred[0]) for ingred in recipe]
		for ingred in ingredients:
			if ingred not in one_gram_counts:
				one_gram_counts[ingred] = 0
			one_gram_counts[ingred] += 1
		these_n_grams = list(combinations(ingredients, k))
		for combo in these_n_grams:
			combo = '/'.join(sorted(combo))
			if combo not in n_grams:
				n_grams[combo] = 0
			n_grams[combo] += 1
	n = 1.*len(d)
	unnormalized_n_grams = deepcopy(n_grams)
	normalized_n_grams = {}
	for n_gram in n_grams:
		n_grams[n_gram] /= n
	for n_gram in one_gram_counts:
		one_gram_counts[n_gram] /= n
	if verbose:
		print 'Top %i-grams' % (k)
	if not normalize:
		for k in sorted(n_grams.keys(), key = lambda x:n_grams[x])[::-1]:
			if verbose:
				print '%-100s %5i' % (k, n_grams[k])
		return unnormalized_n_grams
	else:
		for k in sorted(n_grams.keys(), key = lambda x:normalizeByOneGrams(x, n_grams, one_gram_counts))[::-1]:
			if verbose:
				print '%-100s %2.3f %5i' % (k, normalizeByOneGrams(k, n_grams, one_gram_counts), n_grams[k]*n)
			normalized_n_grams[k] = normalizeByOneGrams(k, n_grams, one_gram_counts)
		return normalized_n_grams

def normalizeByOneGrams(x, n_grams, one_gram_counts):
	terms = x.split('/')
	original_val = 1.*n_grams[x]
	if original_val < .001:
		return 0
	for t in terms:
		original_val = original_val/one_gram_counts[t]
		if one_gram_counts[t] < .001:
			return 0
	return original_val

def dirty_test_of_NMF():
	print 'this is a small demo of the new matrix generation code'
	m, index = recipeMatrix(exact_amounts=True)
	ing_by_ing = np.transpose(m).dot(m)
	model = ProjectedGradientNMF(n_components=8, init='random', random_state=0)
	model.fit(ing_by_ing)
	for idx, component in enumerate(model.components_):
		print '-----------'
		print 'Component %d' % idx
		n = 10
		top_n_indices = np.argsort(-1*component)[0:n]
		for i in top_n_indices:
			print '\t %s: %d' % (index.get_ingred(i), component[i])
		


if __name__ == '__main__':
	i = ingredientsFlavorMatrix()
	m = recipeMatrix()
	dirty_test_of_NMF()

