import json

from scipy.stats import pearsonr
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import SpectralClustering
from pylab import *

from data_formatting import render_ingredient_as_single_word


def make_correlation_webpage(correlation_matrix, item_frequency, names, outfile, n_clusters=5, colors=None):
    n_items = len(item_frequency)

    #Makes a webpage out of correlation matrix.
    correlation_matrix = np.array(correlation_matrix)
    correlation_matrix = correlation_matrix - correlation_matrix.min()
    model = SpectralClustering(affinity='precomputed', n_clusters=n_clusters)
    model.fit(correlation_matrix)

    idxs = np.argsort(model.labels_)
    reordered = np.zeros([len(idxs), len(idxs)])
    for i in range(len(correlation_matrix)):
        for j in range(len(correlation_matrix)):
            reordered[i][j] = correlation_matrix[idxs[i]][idxs[j]]

    figure(figsize=[10, 10])
    imshow(reordered, interpolation='nearest')
    yticks([a for a in range(len(names))], [names[i] for i in idxs])
    xticks(range(len(names)), [names[i] for i in idxs], rotation=90)
    subplots_adjust(bottom=.3, left=.3)
    colorbar()
    # then save figure

    print 'Making webpage...'
    nodes = []
    links = []
    print model.labels_
    for i in set(model.labels_):
        print 'Cluster size', (model.labels_ == i).sum()
    if colors is None:
        colors = []
        for i in range(n_items):
            colors.append(1.*model.labels_[i]/max(model.labels_))
    for i in range(len(correlation_matrix)):
        nodes.append({'name':names[i], 'cluster':str(model.labels_[i]), 'size':item_frequency[i], 'color':colors[i]})
        for j in range(i+1, len(correlation_matrix)):
            links.append({"source": i, "target": j, "value": correlation_matrix[i][j]})
    json.dump({'nodes':nodes, 'links':links}, open('%s.json' % outfile, 'w+'))
    f = open('/Users/epierson/Dropbox/base_graph.html').read()
    full_outfile_name = ('%s.html' % outfile)

    g = open(full_outfile_name, 'w+')
    g.write(f % ('%s.json' % outfile))
    print 'Saved website as', full_outfile_name


def correlation_webpage_wrapper():
    d = pickle.load(open("cleaned_recipes"))
    ingredients = list(set([render_ingredient_as_single_word(ingred[0]) for recipe in d for ingred in recipe ]))
    ingredient_map = dict(zip(ingredients, range(len(ingredients))))
    m = np.zeros([len(d), len(ingredients)])
    for i, recipe in enumerate(d):
        for ingredient in recipe:
            m[i][ingredient_map[render_ingredient_as_single_word(ingredient[0])]] = 1
    ingredient_frequency = m.sum(axis=0)
    idxs = np.argsort(ingredient_frequency)[::-1]
    for i in idxs[:100]:
        print ingredients[i], ingredient_frequency[i]
    ## Good means not too common, not too rare.
    good_ns = (ingredient_frequency >= 5) & (ingredient_frequency <= 500)
    ingredient_frequency = ingredient_frequency[good_ns]
    correlation_matrix = np.corrcoef(m[:, good_ns].transpose())
    ingredients = [ingredients[i] for i in range(len(ingredients)) if good_ns[i]]
    m = m[:, good_ns]
    make_correlation_webpage(correlation_matrix, ingredient_frequency,
                             ingredients, 'alcohol', n_clusters=30)


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


def generative_model1(seed_flavor, ingredient_flavor, conditional_flavor_probs, flavors, ingredient_frequencies, ingredients):
    alpha = .3
    n_ingredients, n_flavors = ingredient_flavor.shape

    ## Get some flavors to use
    flavor_idxs = [flavors.index(seed_flavor)]
    while True:
        flavor_probs = np.ones([n_flavors, ])
        if random.uniform(0, 1) < alpha:
            # don't put too many things in the drink
            break
        for j in range(len(flavor_idxs)):
            flavor_probs = np.multiply(flavor_probs, conditional_flavor_probs[flavor_idxs[j], :])
        if flavor_probs.sum() < 1e-8:
            # if this is a rare thing, give up
            break
        flavor_probs = flavor_probs/(flavor_probs.sum()+1e-10)
        draw = np.nonzero(np.random.multinomial(1, flavor_probs))[0][0]
        flavor_idxs.append(draw)
    flavor_idxs = list(set(flavor_idxs))

    ## now find ingredients
    ingredient_names = []
    for i in flavor_idxs:
        candidate_ingredients = np.nonzero(ingredient_flavor[:, i])[0]
        candidate_ingredient_names = [ingredients[i] for i in candidate_ingredients]
        candidate_frequencies = ingredient_frequencies[candidate_ingredients]
        candidate_frequencies = candidate_frequencies/(candidate_frequencies.sum() + 1e-10)
        draw = np.nonzero(np.random.multinomial(1, candidate_frequencies))[0][0]
        ingredient_names.append(candidate_ingredient_names[draw])

    print 'Recipe:'
    flavor_names = [flavors[i] for i in flavor_idxs]
    for i in range(len(flavor_names)):
        print flavor_names[i], 'generated', ingredient_names[i]
    print


def use_generative_model():
    analyze_ingredients()
    d = pickle.load(open('cleaned_matrices'))
    ingredient_flavor = np.array(d['ingredient_flavor'])  # ingredient -> flavor
    ingredient_recipe = np.array(d['ingredient_recipe'])  # ingredient -> recipes
    flavor_recipe = np.dot(ingredient_flavor.transpose(), ingredient_recipe) # flavor -> recipe
    conditional_flavor_probs = np.dot(flavor_recipe, flavor_recipe.transpose()) # m[i][j] is probs of seeing j given that you saw i, maybe
    flavor_frequency = flavor_recipe.sum(axis=1)
    ingredient_frequency = ingredient_recipe.sum(axis=1)
    for i in range(len(conditional_flavor_probs)):
        conditional_flavor_probs[i, i] = 0
        conditional_flavor_probs[i, :] = conditional_flavor_probs[i, :]/conditional_flavor_probs[i, :].sum()
    for j, seed_flavor in enumerate(d['flavors']):
        if flavor_frequency[j] < 30:
            continue
        print '\nGenerating flavors using seed', seed_flavor
        for i in range(5):
            generative_model1(seed_flavor, ingredient_flavor,
                              conditional_flavor_probs, d['flavors'],
                              ingredient_frequency, d['ingredients'])


if __name__ == '__main__':
    use_generative_model()