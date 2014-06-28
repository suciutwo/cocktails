"""
KEY METHODS:
topNGrams
"""
import pickle
import string
import numpy as np
import unicodedata
from itertools import combinations
from collections import Counter
from copy import deepcopy
from src.data_processing.parse_pages import CLEANED_COCKTAILS_FILENAME


def render_ingredient_as_single_word(string_):
    string_ = string_.replace('fresh', '').strip()
    string_ = string_.translate(string.maketrans("", ""), string.punctuation)
    string_ = string_.lower().replace(' ', '_')
    string_ = string_.decode('utf-8')
    return string_

def top_ingredient_combinations(combination_size=2, normalize=False, verbose=False):
    recipes = pickle.load(open(CLEANED_COCKTAILS_FILENAME))
    n_gram_counts = Counter()
    one_gram_counts = Counter()
    for name, recipe in recipes.iteritems():
        ingredients = [render_ingredient_as_single_word(ingredient_tuple[0])
                       for ingredient_tuple in recipe]
        for ingredient in ingredients:
            one_gram_counts[ingredient] += 1
        these_n_grams = list(combinations(ingredients, combination_size))
        for combination in these_n_grams:
            combination = '/'.join(sorted(combination))
            n_gram_counts[combination] += 1
    total_recipes = 1.*len(recipes)
    unnormalized_n_grams = deepcopy(n_gram_counts)
    normalized_n_grams = {}
    for n_gram in n_gram_counts:
        n_gram_counts[n_gram] /= total_recipes
    for n_gram in one_gram_counts:
        one_gram_counts[n_gram] /= total_recipes
    if verbose:
        print 'Top %i-grams' % (combination_size)
    if not normalize:
        for n_gram in sorted(n_gram_counts.keys(),
                             key=lambda x: n_gram_counts[x])[::-1]:
            if verbose:
                print '%-100s %5i' % (n_gram, n_gram_counts[n_gram])
        return unnormalized_n_grams
    else:
        for n_gram in sorted(n_gram_counts.keys(), key=lambda x: normalize_by_onegrams(x, n_gram_counts, one_gram_counts))[::-1]:
            if verbose:
                print '%-100s %2.3f %5i' % (
                    n_gram, normalize_by_onegrams(
                        combination_size, n_gram_counts, one_gram_counts),
                    n_gram_counts[n_gram]*total_recipes)
            normalized_n_grams[n_gram] = normalize_by_onegrams(
                combination_size, n_gram_counts, one_gram_counts)
        return normalized_n_grams


def normalize_by_onegrams(x, n_grams, one_gram_counts):
    terms = x.split('/')
    original_val = 1.*n_grams[x]
    if original_val < .001:
        return 0
    for t in terms:
        original_val = original_val/one_gram_counts[t]
        if one_gram_counts[t] < .001:
            return 0
    return original_val


def most_likely_third_ingredient(verbose=True, normalize=False):
    k = 2
    d = pickle.load(open("cleaned_recipes"))
    n_recipes = len(d)
    n_grams = top_ingredient_combinations(combination_size=k, normalize=False)
    one_grams = top_ingredient_combinations(combination_size=1, normalize=False)
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

            if not normalize:  # prints ingredient most likely to follow
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



if __name__ == '__main__':
    pass

