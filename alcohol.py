from bs4 import BeautifulSoup
import urllib2
from threading import Thread
import pickle
import Queue
from scipy.stats import pearsonr
from sklearn.decomposition import PCA, SparsePCA
from sklearn.feature_extraction.text import TfidfVectorizer
from pylab import *
import numpy as np
import numpy as np
from sklearn.cluster import SpectralClustering
from pylab import *
import json
from copy import deepcopy
from tsne import bh_sne
from itertools import combinations
import string
import random

def makeCorrelationWebpage(C, ns, names, outfile, n_clusters = 5, colors = None):
	n = len(ns)
	
	#Makes a webpage out of correlation matrix. 
	C = np.array(C)
	C = C - C.min()
	S = SpectralClustering(affinity = 'precomputed', n_clusters = n_clusters)
	S.fit(C)
	
	idxs = np.argsort(S.labels_)
	reordered = np.zeros([len(idxs), len(idxs)])
	for i in range(len(C)):
		for j in range(len(C)):
			reordered[i][j] = C[idxs[i]][idxs[j]]
	figure(figsize = [10, 10])		
	imshow(reordered, interpolation = 'nearest')
	yticks([a  for a in range(len(names))], [names[i] for i in idxs])
	xticks(range(len(names)), [names[i] for i in idxs], rotation = 90)
	subplots_adjust(bottom = .3, left = .3)
	colorbar()
	show()
	print 'Making webpage...'
	nodes = []
	links = []
	print S.labels_
	for i in set(S.labels_):
		print 'Cluster size', (S.labels_ == i).sum()
	if colors is None:
		colors = []
		for i in range(n):
			colors.append(1.*S.labels_[i]/max(S.labels_))
	for i in range(len(C)):
		nodes.append({'name':names[i], 'cluster':str(S.labels_[i]), 'size':ns[i], 'color':colors[i]})
		for j in range(i+1, len(C)):
			links.append({"source": i, "target": j, "value": C[i][j]})
	json.dump({'nodes':nodes, 'links':links}, open('%s.json' % outfile, 'w+'))
	f = open('/Users/epierson/Dropbox/base_graph.html').read()
	full_outfile_name = ('%s.html' % outfile)
	
	g = open(full_outfile_name, 'w+')
	g.write(f % ('%s.json' % outfile))
	print 'Saved website as', full_outfile_name
	
def scanRecipe():
	soup=BeautifulSoup(urlopen(url))
	l=soup.findAll('li', {'class':'ingredient'})

COCKTAILS_ON_DATABASE = 4758
INTERNET_DB_URL = 'http://www.cocktaildb.com/recipe_detail?id='
INGREDIENTS_IN_DATABASE = 558
INGREDIENT_DB_URL = 'http://www.cocktaildb.com/ingr_detail?id='

def downloadAllPages():
	WORKERS = 20

	urls = []
	for i in range(1, COCKTAILS_ON_DATABASE):
		urls.append(INTERNET_DB_URL+str(i))

	results = [None]*len(urls)

	def worker():
		n_read = 0
		while True:
			i, url = q.get()
			try: 
				results[i] = (urllib2.urlopen(url).read())
				print i, n_read
				n_read+=1
			except Exception as e:
				print "failed on " + str(i)
				print e


			q.task_done()

	q = Queue.Queue()
	for i in range(WORKERS):
		t = Thread(target=worker)
		t.daemon = True
		t.start()

	for i, url in enumerate(urls):
		q.put((i, url))

	q.join()

	print len(results)
	pickle.dump(results, open("savedCocktails", 'wb'))

def downloadAllIngredients():
	WORKERS = 10

	urls = []
	for i in range(1, INGREDIENTS_IN_DATABASE):
		urls.append(INGREDIENT_DB_URL+str(i))

	results = [None]*len(urls)

	def worker():
		n_read = 0
		while True:
			i, url = q.get()
			try: 
				results[i] = (urllib2.urlopen(url).read())
				print i, n_read
				n_read+=1
			except Exception as e:
				print "failed on " + str(i)
				print e


			q.task_done()

	q = Queue.Queue()
	for i in range(WORKERS):
		t = Thread(target=worker)
		t.daemon = True
		t.start()

	for i, url in enumerate(urls):
		q.put((i, url))

	q.join()

	print len(results)
	pickle.dump(results, open("savedIngredients", 'wb'))
def processRecipes():
	d = pickle.load(open("savedCocktails"))
	all_recipes = []
	for i, d_i in enumerate(d):
		
		try:
			soup=BeautifulSoup(d_i)
			l=soup.findAll('div', {'class':'recipeMeasure'})
			print 'Recipe %i' % (i)
			recipe = []
			for ingredient in l:
				comps = str(ingredient).split('>')
				amount = comps[1].split('<')[0].strip()
				ingredient = comps[2].split('<')[0].strip()
				recipe.append([ingredient, amount])
			all_recipes.append(recipe)
		except:
			continue
	pickle.dump(all_recipes, open("cleanedRecipes", 'wb'))	
def processIngredFile():
	d = pickle.load(open("savedIngredients"))
	all_ingredients = {}
	for i, d_i in enumerate(d):
		
		try:
			l=d_i.split('flavor">')
			print 'Ingredient %i' % (i)
			flavors = []
			for flavor in l[1:]:
				flavors.append(flavor.split('<')[0].replace(',', '').replace(' ', '_').lower())
			name = d_i.split('<div id="wellTitle">')[1].split('<h2>')[1].split('<')[0]
			#print l[1][:50]
			print name, flavors
			all_ingredients[name] = flavors
		except:
			continue
	print all_ingredients
	pickle.dump(all_ingredients, open("cleanedIngredients", 'wb'))	
def processIngred(s):
	s = s.replace('fresh', '').strip()
	s = s.translate(string.maketrans("",""), string.punctuation)
	s = s.lower().replace(' ', '_')
	return s
def pca():
	d = pickle.load(open("cleanedRecipes"))	
	tf_idf = True
	use_pca = False
	plot_rank = False
	threshold = 10
	two_grams = topNGrams(k = 2, normalize = False)
	if not tf_idf:
		ingredients = list(set([processIngred(ingred[0]) for recipe in d for ingred in recipe ]))
		ingredient_map = dict(zip(ingredients, range(len(ingredients))))
		m = np.zeros([len(d), len(ingredients)])
		C = []
		for i, recipe in enumerate(d):
			for ingredient in recipe:
				m[i][ingredient_map[processIngred(ingredient[0])]] = 1
		ns = m.sum(axis = 0)
		idxs = np.argsort(ns)[::-1]
		for i in idxs[:100]:
			print ingredients[i], ns[i]
		good_ns = (ns>=5) & (ns<=500)
		ns = ns[good_ns]
		C = np.corrcoef(m[:, good_ns].transpose())
		print C.shape
		ingredients = [ingredients[i] for i in range(len(ingredients)) if good_ns[i]]
		m = m[:, good_ns]
		makeCorrelationWebpage(C, ns, ingredients, 'alcohol', n_clusters = 30, colors = None)
	else:
		tfidf = TfidfVectorizer()
		all_strings = []
		for i, recipe in enumerate(d):
			s = ' '.join([processIngred(ingredient[0]).decode('utf-8') for ingredient in recipe])
			print s
			all_strings.append(s)
		m = tfidf.fit_transform(all_strings).toarray()
		ingredients = tfidf.get_feature_names()
		
	if use_pca:
		n_components = 2
		model = PCA(n_components = n_components, whiten = False)#SparsePCA(n_components = n_components, alpha = .5)
		small_m = model.fit_transform(m.transpose())
		#for i in range(n_components):
		#	idxs = np.argsort(abs(model.components_[i, :]))[::-1]
		#	print 'Component %i has %i nonzero components' % (i+1, (model.components_[i, :]!=0).sum())
		#	#print len(model.components_[i, :])
		#	for j in idxs:
		#		if model.components_[i, j]!=0:
		#			print model.components_[i, j], ingredients[j]
		#print model.components_.shape
		#print 
	else:
		small_m = bh_sne(m.transpose())
		
	figure(figsize = [50, 50])
	small_m[:, 0] = small_m[:, 0] - (small_m[:, 0].min()-.001)
	small_m[:, 1] = small_m[:, 1] - (small_m[:, 1].min()-.001)
	if plot_rank:
		for i in range(len(small_m[0])):
			idxs = np.argsort(small_m[:, i])[::-1]
			for rank, j in enumerate(idxs):
				small_m[j, i] = rank
				
	ingredient_dict = dict(zip(ingredients, range(len(ingredients))))
	ax = subplot(111)
	for i in range(len(small_m)):
		if tf_idf:
			annotate(ingredients[i], [small_m[i, 0], small_m[i, 1]])
		else:
			annotate(ingredients[i].decode('utf-8'), [small_m[i, 0], small_m[i, 1]])
	n_lines_plotted = 0
	for k in two_grams:
		if two_grams[k] > threshold:
			try:
				a1, a2 = k.split('/')
				p1 = small_m[ingredient_dict[a1]]
				p2 = small_m[ingredient_dict[a2]]
				plot([p1[0], p2[0]], [p1[1], p2[1]], color = 'red')
				n_lines_plotted += 1
			except:
				continue
	print 'Number of connections passing threshold', n_lines_plotted
	scatter(small_m[:, 0], small_m[:, 1])
	xlim([min(small_m[:, 0]), max(small_m[:, 0])*1.1])
	ylim([min(small_m[:, 0]), max(small_m[:, 0])*1.1])
	#show()
	if tf_idf:
		savefig('PCA_tf_idf.png')
	else:
		savefig('PCA_no_tf_idf.png')
	print small_m
def topNGrams(k = 2, normalize = False, verbose = False):
	d = pickle.load(open("cleanedRecipes"))	
	n_grams = {}
	one_gram_counts = {}
	for recipe in d:
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
def topConditional(k = 2, verbose = True, normalize = False):
	d = pickle.load(open("cleanedRecipes"))
	n_recipes = len(d)
	n_grams = topNGrams(k = k, normalize = False)
	one_grams = topNGrams(k = 1, normalize = False)
	n_gram_map = {}
	for k in n_grams:
		l = k.split('/')
		l = sorted(l)
		for i in range(len(l)):
			key = '/'.join(l[:i]+l[(i+1):])
			if key not in n_gram_map:
				n_gram_map[key] = [[], []]
			n_gram_map[key][0].append(n_grams[k])
			
			n_gram_map[key][1].append(l[i])
	if verbose:
		reverse = True
		print 'Top completions'
		ks = sorted(n_gram_map.keys(), key = lambda x:sum(n_gram_map[x][0]))[::-1]
		for i, k in enumerate(ks[:50]):
			z = 1.*sum(n_gram_map[k][0])
			print '\nCombo %i: %s, %i appearances. Final ingredient:' % (i+1, k, z)
			
			if not normalize:
				idxs = np.argsort(n_gram_map[k][0])[::-1]
				for j in idxs[:10]:
					print '%-50s %i %2.1f%%' % (n_gram_map[k][1][j], n_gram_map[k][0][j], 100*n_gram_map[k][0][j]/z)
			else:
				if not reverse:
					idxs = sorted(range(len(n_gram_map[k][0])), key = lambda x:(n_gram_map[k][0][x]/z)/(1.*one_grams[n_gram_map[k][1][x]]/n_recipes) if one_grams[n_gram_map[k][1][x]]>5 else 0)[::-1]
				else:
					idxs = sorted(range(len(n_gram_map[k][0])), key = lambda x:(n_gram_map[k][0][x]/z)/(1.*one_grams[n_gram_map[k][1][x]]/n_recipes) if one_grams[n_gram_map[k][1][x]]>20 else 9999)
				for j in idxs[:10]:
					print '%-50s %2.1fx more likely' % (n_gram_map[k][1][j], (n_gram_map[k][0][j]/z)/(1.*one_grams[n_gram_map[k][1][j]]/n_recipes))
def analyzeIngredients():
	#Produce ingredient-flavor matrix and 
	ingredients_to_flavors = pickle.load(open("cleanedIngredients"))
	for i in ingredients_to_flavors.keys():
		ingredients_to_flavors[processIngred(i).decode('utf-8')] = ingredients_to_flavors[i]
		del ingredients_to_flavors[i]
	recipes = pickle.load(open("cleanedRecipes"))
	tfidf = TfidfVectorizer()
	all_strings = []
	for i, recipe in enumerate(recipes):
		s = ' '.join([processIngred(ingredient[0]).decode('utf-8') for ingredient in recipe])
		all_strings.append(s)
	ingredient_recipe = (tfidf.fit_transform(all_strings).toarray()>0).transpose()
	ingredients = tfidf.get_feature_names()
	ingredient_map = dict(zip(ingredients, range(len(ingredients))))
	print 'Have ingredient data for', len([a for a in ingredients_to_flavors if  len(ingredients_to_flavors[a])>0]), 'ingredients'
	counts = {}
	
	for ingred in ingredients_to_flavors:
		for f in ingredients_to_flavors[ingred]:
			if f not in counts:
				counts[f] = 0
			counts[f] += 1
	flavor_map = dict(zip(counts.keys(), range(len(counts.keys()))))
	ingredient_flavor = np.zeros([len(ingredients), len(counts)])
	n_errors = n_successes = 0
	for ingred in ingredients_to_flavors:
		if len(ingredients_to_flavors[ingred]) == 0:
			continue
		if ingred not in ingredient_map:
			n_errors += 1
			continue
		else:
			n_successes += 1
		for f in ingredients_to_flavors[ingred]:
			ingredient_flavor[ingredient_map[ingred], flavor_map[f]] = 1
	print 'Number of errors', n_errors, 'number of successes', n_successes
	good_ingredients = (ingredient_flavor.sum(axis = 1) > 0) & (ingredient_recipe.sum(axis = 1) > 0)
	ingredient_flavor = ingredient_flavor[good_ingredients, :]
	ingredient_recipe = ingredient_recipe[good_ingredients, :]
	good_flavors = ingredient_flavor.sum(axis = 0) > 0
	ingredient_flavor = ingredient_flavor[:, good_flavors]
	flavor_labels = [counts.keys()[i] for i in range(len(counts.keys())) if good_flavors[i]]
	ingredient_labels = [ingredients[i] for i in range(len(ingredients)) if good_ingredients[i]]
	
	flavor_recipe = np.dot(ingredient_flavor.transpose(), ingredient_recipe)
	flavor_C = np.corrcoef(flavor_recipe)
	flavor_ns = flavor_recipe.sum(axis = 1)
	#makeCorrelationWebpage(flavor_C, flavor_ns, flavor_labels, 'flavors', n_clusters = 40, colors = None)
	idxs = np.argsort(flavor_ns)[::-1]
	ingredient_C_flavor = np.corrcoef(ingredient_flavor)
	ingredient_C_recipe = np.corrcoef(ingredient_recipe)
	x = []
	y = []
	for i in range(len(ingredient_C_flavor)):
		for j in range(i+1, len(ingredient_C_flavor)):
			x.append(ingredient_C_flavor[i][j])
			y.append(ingredient_C_recipe[i][j])
	scatter(x, y)
	xlabel('Flavor Correlation')
	ylabel('Ingredient Correlation')
	print pearsonr(x, y)
	show()
	d = {'flavors':flavor_labels, 'ingredients':ingredient_labels, 'ingredient_flavor':[list(a) for a in ingredient_flavor], 'ingredient_recipe':[list(a) for a in ingredient_recipe]}
	pickle.dump(d, open('cleanedMatrices', 'wb'))
		
	print 'Flavor ingredient assocations', sum(counts.values())
	
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
def generativeModel1(seed_flavor, ingredient_flavor, ingredient_recipe, flavor_recipe, conditional_flavor_probs, flavors, ingredient_frequencies, ingredients):
	alpha = .3
	flavors_in_recipe = [seed_flavor]
	n_ingredients, n_flavors = ingredient_flavor.shape
	n_ingredients, n_recipes = ingredient_recipe.shape	
	flavor_idxs = [flavors.index(seed_flavor)]
	while 1:
		flavor_probs = np.ones([n_flavors,])
		if random.uniform(0, 1)<alpha:
			break
		for j in range(len(flavor_idxs)):
			flavor_probs = np.multiply(flavor_probs, conditional_flavor_probs[flavor_idxs[j], :])
		if flavor_probs.sum() < 1e-8:
			break
		flavor_probs = flavor_probs/(flavor_probs.sum()+1e-10)
		draw = np.nonzero(np.random.multinomial(1, flavor_probs))[0][0]
		flavor_idxs.append(draw)
	flavor_idxs = list(set(flavor_idxs))
	flavor_names = [flavors[i] for i in flavor_idxs]
	ingredient_names = []
	for i in flavor_idxs:
		candidate_ingredients = np.nonzero(ingredient_flavor[:, i])[0]
		candidate_ingredient_names = [ingredients[i] for i in candidate_ingredients]
		candidate_frequencies = ingredient_frequencies[candidate_ingredients]
		candidate_frequencies = candidate_frequencies/(candidate_frequencies.sum() + 1e-10)
		draw = np.nonzero(np.random.multinomial(1, candidate_frequencies))[0][0]
		ingredient_names.append(candidate_ingredient_names[draw])
	print 'Recipe:'
	for i in range(len(flavor_names)):
		print flavor_names[i], 'generated', ingredient_names[i]
	print
if __name__ == '__main__':
	download = 0
	if download:
		#downloadAllIngredients()
		#downloadAllPages()
		#processIngredFile()
		processRecipes()
	else:
		d = pickle.load(open('cleanedMatrices'))
		ingredient_flavor = np.array(d['ingredient_flavor'])
		ingredient_recipe = np.array(d['ingredient_recipe'])
		flavor_recipe = np.dot(ingredient_flavor.transpose(), ingredient_recipe)
		conditional_flavor_probs= np.dot(flavor_recipe, flavor_recipe.transpose()) # m[i][j] is probs of seeing j given that you saw i
		flavor_frequency = flavor_recipe.sum(axis = 1)
		ingredient_frequency = ingredient_recipe.sum(axis = 1)
		for i in range(len(conditional_flavor_probs)):
			conditional_flavor_probs[i, i] = 0
			conditional_flavor_probs[i, :] = conditional_flavor_probs[i, :]/conditional_flavor_probs[i, :].sum()
		for j, seed_flavor in enumerate(d['flavors']):
			if flavor_frequency[j] < 30:
				continue
			print '\nGenerating flavors using seed', seed_flavor
			for i in range(5):
				generativeModel1(seed_flavor, ingredient_flavor, ingredient_recipe, flavor_recipe, conditional_flavor_probs, d['flavors'], ingredient_frequency, d['ingredients'])
		#analyzeIngredients()
		#sdflkj
		
		
		#processRecipes()