"""
For parsing (scraped) raw html with BeautifulSoup
"""

import pickle

from BeautifulSoup import BeautifulSoup

import src.constants as constants


def process_recipes_file():
    """
    Creates a list of lists that contain the (ingredient, amount)
    tuples that compose a recipe; pickles the list.
    """
    cocktail_pages = pickle.load(open(constants.COCKTAILS_FILENAME))
    all_recipes = {}
    for i, cocktail_page in enumerate(cocktail_pages):
        if not cocktail_page:
            print "ERROR: NO PAGE. FAILED TO SCRAPE IT EARLIER."
            continue
        if i % 1000 == 0:
                print 'Parsing recipe ' + str(i)
        try:
            soup = BeautifulSoup(cocktail_page)
            title = soup.findAll('h2')[0].string.strip()
            recipe = []
            measurements = soup.findAll('div', {'class': 'recipeMeasure'})
            for measure in measurements:
                amount = measure.contents[0]
                ingredient = measure.a.string
                alternative_amount = ''
                if measure.span:
                    alternative_amount = measure.span.string
                recipe.append([ingredient, amount.strip()+alternative_amount.strip()])
            additional_steps = soup.findAll('div', {'class': 'recipeDirection'})
            for step in additional_steps:
                instructions = ''.join([elem.string for elem in step.contents])
                anchors = step.findAll('a')
                for anchor in anchors:
                    is_ingredient = anchor['href'].find('ingr_detail') >= 0
                    not_a_cocktail_shaker = anchor['href'].find('id=322') == -1
                    not_a_chaser = anchor['href'].find('id=383') == -1
                    if is_ingredient and not_a_cocktail_shaker and not_a_chaser:
                        ingredient = anchor.string
                        amount = instructions
                        recipe.append([ingredient, amount])
            all_recipes[title] = recipe
        except Exception as exception:  # pylint: disable=W0703
            print exception
            print cocktail_page
            continue
    pickle.dump(all_recipes, open(constants.CLEANED_COCKTAILS_FILENAME, 'wb'))


def process_ingredients_file():
    """
    Creates a dictionary where the key is the ingredient and the
    value is a list of all the flavors that describe it; pickles the
    dictionary.
    """
    ingredient_pages = pickle.load(open(constants.INGREDIENTS_FILENAME))
    all_ingredients = {}
    for i, ingredient_page in enumerate(ingredient_pages):

        try:
            raw_text = ingredient_page.split('flavor">')
            if i % 1000 == 0:
                print 'Parsing ingredient ' + str(i)
            flavors = []
            for flavor in raw_text[1:]:
                flavor = flavor.split('<')[0]
                flavor = flavor.replace(',', '').replace(' ', '_').lower()
                flavors.append(flavor)
            name = ingredient_page.split('<div id="wellTitle">')[1]
            name = name.split('<h2>')[1].split('<')[0]
            print name, flavors
            all_ingredients[name] = flavors
        except Exception as exception:  # pylint: disable=W0703
            print exception
            continue
    pickle.dump(all_ingredients,
                open(constants.CLEANED_INGREDIENTS_FILENAME, 'wb'))


if __name__ == '__main__':
    process_recipes_file()
    # process_ingredients_file()
