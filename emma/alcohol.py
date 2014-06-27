import json
import random

from scipy.stats import pearsonr
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import SpectralClustering
from pylab import *

from tsne import bh_sne
from data_formatting import top_ingredient_combinations
from data_formatting import render_ingredient_as_single_word


def make_correlation_webpage(C, ns, names, outfile, n_clusters = 5, colors = None):
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



def pca():
    d = pickle.load(open("cleaned_recipes"))
    tf_idf = True
    use_pca = False
    plot_rank = False
    threshold = 10
    two_grams = top_ingredient_combinations(combination_size=2, normalize=False)
    if not tf_idf:
        ingredients = list(set([render_ingredient_as_single_word(ingred[0]) for recipe in d for ingred in recipe ]))
        ingredient_map = dict(zip(ingredients, range(len(ingredients))))
        m = np.zeros([len(d), len(ingredients)])
        C = []
        for i, recipe in enumerate(d):
            for ingredient in recipe:
                m[i][ingredient_map[render_ingredient_as_single_word(ingredient[0])]] = 1
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
        make_correlation_webpage(C, ns, ingredients, 'alcohol', n_clusters = 30, colors = None)
    else:
        tfidf = TfidfVectorizer()
        all_strings = []
        for i, recipe in enumerate(d):
            s = ' '.join([render_ingredient_as_single_word(ingredient[0]).decode('utf-8') for ingredient in recipe])
            print s
            all_strings.append(s)
        m = tfidf.fit_transform(all_strings).toarray()
        ingredients = tfidf.get_feature_names()

    if use_pca:
        n_components = 2
        model = PCA(n_components=n_components, whiten=False)#SparsePCA(n_components = n_components, alpha = .5)
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

    figure(figsize=[50, 50])
    small_m[:, 0] = small_m[:, 0] - (small_m[:, 0].min()-.001)
    small_m[:, 1] = small_m[:, 1] - (small_m[:, 1].min()-.001)
    if plot_rank:
        for i in range(len(small_m[0])):
            idxs = np.argsort(small_m[:, i])[::-1]
            for rank, j in enumerate(idxs):
                small_m[j, i] = rank

    ingredient_dict = dict(zip(ingredients, range(len(ingredients))))
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




def analyze_ingredients():
    #Produce ingredient-flavor matrix and
    ingredients_to_flavors = pickle.load(open("cleaned_ingredients"))
    for i in ingredients_to_flavors.keys():
        ingredients_to_flavors[render_ingredient_as_single_word(i).decode('utf-8')] = ingredients_to_flavors[i]
        del ingredients_to_flavors[i]
    recipes = pickle.load(open("cleaned_recipes"))
    tfidf = TfidfVectorizer()
    all_strings = []
    for i, recipe in enumerate(recipes):
        s = ' '.join([render_ingredient_as_single_word(ingredient[0]).decode('utf-8') for ingredient in recipe])
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
    pickle.dump(d, open('cleaned_matrices', 'wb'))

    print 'Flavor ingredient assocations', sum(counts.values())


def generative_model1(seed_flavor, ingredient_flavor, ingredient_recipe, flavor_recipe, conditional_flavor_probs, flavors, ingredient_frequencies, ingredients):
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
    d = pickle.load(open('cleaned_matrices'))
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
            generative_model1(seed_flavor, ingredient_flavor, ingredient_recipe, flavor_recipe, conditional_flavor_probs, d['flavors'], ingredient_frequency, d['ingredients'])
