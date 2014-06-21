import os
import pickle
import numpy as np
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

if exactAmounts, then returns the measurement of each ingredient 
instead of mere presence (i.e. floats instead of [0, 1])
'''
def recipeMatrix():
	print 'TODO'



'''
Creates a map (in AMOUNT_PARSING_GUIDE) that goes from strings -> ingredients. Human generated.
'''
def buildAmountParsingMapping(exactAmounts = False):
	associations = {}
	if os.path.isfile(AMOUNT_PARSING_GUIDE):
		associations = pickle.load(open(AMOUNT_PARSING_GUIDE, 'rb'))
	
	print "...loading recipe list from file, run parsePages to generate a new version of the file"
	recipes = pickle.load(open(CLEANED_COCKTAILS_FILENAME, 'rb'))
	for idx, recipe in enumerate(recipes):
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


if __name__ == '__main__':
	buildAmountParsingMapping()
