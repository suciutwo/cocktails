'''
For parsing (scraped) raw html with BeautifulSoup
'''

import pickle

from BeautifulSoup import BeautifulSoup

from src.data_processing.scrapeCocktails import COCKTAILS_FILENAME
from src.data_processing.scrapeCocktails import INGREDIENTS_FILENAME


CLEANED_COCKTAILS_FILENAME = 'data/cleanedRecipes'
CLEANED_INGREDIENTS_FILENAME = 'data/cleanedIngredients'


def process_recipes_file():
    """
    Creates a list of lists that contain the (ingredient, amount)
    tuples that compose a recipe; pickles the list.
    """
    cocktail_pages = pickle.load(open(COCKTAILS_FILENAME))
    all_recipes = {}
    for i, cocktail_page in enumerate(cocktail_pages):
        try:
            soup = BeautifulSoup(cocktail_page)
            title = soup.findAll('h2')[0].string.strip()
            measurements = soup.findAll('div', {'class': 'recipeMeasure'})
            if i % 1000 == 0:
                print 'Parsing recipe ' + str(i)
            recipe = []
            for ingredient in measurements:
                comps = str(ingredient).split('>')
                amount = comps[1].split('<')[0].strip()
                ingredient = comps[2].split('<')[0].strip()
                alternative_amount = comps[4].split('<')[0].strip()
                recipe.append([ingredient, amount, alternative_amount])
            all_recipes[title] = recipe
        except Exception as e:
            print e
            print "FAILED TO SCRAPE THIS PAGE EARLIER IN THE PIPELINE"
            continue
    pickle.dump(all_recipes, open(CLEANED_COCKTAILS_FILENAME, 'wb'))


def process_ingredients_file():
    """
    Creates a dictionary where the key is the ingredient and the
    value is a list of all the flavors that describe it; pickles the
    dictionary.
    """
    ingredient_pages = pickle.load(open(INGREDIENTS_FILENAME))
    all_ingredients = {}
    for i, ingredientPage in enumerate(ingredient_pages):

        try:
            raw_text = ingredientPage.split('flavor">')
            if i % 1000 == 0: print 'Parsing ingredient ' + str(i)
            flavors = []
            for flavor in raw_text[1:]:
                flavor = flavor.split('<')[0]
                flavor = flavor.replace(',', '').replace(' ', '_').lower()
                flavors.append(flavor)
            name = ingredientPage.split('<div id="wellTitle">')[1]
            name = name.split('<h2>')[1].split('<')[0]
            print name, flavors
            all_ingredients[name] = flavors
        except Exception as e:
            print e
            continue
    pickle.dump(all_ingredients, open(CLEANED_INGREDIENTS_FILENAME, 'wb'))


if __name__ == '__main__':
    process_recipes_file()
    #process_ingredients_file()