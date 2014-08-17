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
        soup = BeautifulSoup(cocktail_page)
        title = soup.findAll('h2')[0].string.strip()
        recipe = []
        measurements = soup.findAll('div', {'class': 'recipeMeasure'})
        for measure in measurements:
            amount = measure.contents[0].strip()
            ingredient = unicode(measure.a.string)
            if measure.span:
                alternative_amount = measure.span.string.strip()
                amount += ' ' + alternative_amount
            recipe.append([ingredient, amount])
        additional_steps = soup.findAll('div', {'class': 'recipeDirection'})
        glass_size = get_glass_size_string(additional_steps)
        for step in additional_steps:
            instructions = ''.join([elem.string for elem in step.contents])
            if glass_size:
                instructions += ' (' + glass_size.strip() + ')'
            anchors = step.findAll('a')
            for anchor in anchors:
                is_ingredient = anchor['href'].find('ingr_detail') >= 0
                not_a_cocktail_shaker = anchor['href'].find('id=322') == -1
                not_a_chaser = anchor['href'].find('id=383') == -1
                if is_ingredient and not_a_cocktail_shaker and not_a_chaser:
                    ingredient = unicode(anchor.string)
                    recipe.append([ingredient, instructions])
        all_recipes[title] = recipe
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


def get_glass_size_string(additional_steps):
    """
    Extracts a string that explains the size of of the intended glass.
    """
    for step in additional_steps:
        anchors = step.findAll('a')
        for anchor in anchors:
            is_barware = anchor['href'].find('barwr_detail') >= 0
            if is_barware:
                is_glassware = anchor['href'] in ["barwr_detail?id=54",
                                                  "barwr_detail?id=54",
                                                  "barwr_detail?id=57",
                                                  "barwr_detail?id=57",
                                                  "barwr_detail?id=40",
                                                  "barwr_detail?id=40",
                                                  "barwr_detail?id=58",
                                                  "barwr_detail?id=58",
                                                  "barwr_detail?id=59",
                                                  "barwr_detail?id=59",
                                                  "barwr_detail?id=106",
                                                  "barwr_detail?id=106",
                                                  "barwr_detail?id=113",
                                                  "barwr_detail?id=113",
                                                  "barwr_detail?id=61",
                                                  "barwr_detail?id=61",
                                                  "barwr_detail?id=37",
                                                  "barwr_detail?id=37",
                                                  "barwr_detail?id=2",
                                                  "barwr_detail?id=2",
                                                  "barwr_detail?id=3",
                                                  "barwr_detail?id=3",
                                                  "barwr_detail?id=36",
                                                  "barwr_detail?id=36",
                                                  "barwr_detail?id=4",
                                                  "barwr_detail?id=4",
                                                  "barwr_detail?id=5",
                                                  "barwr_detail?id=5",
                                                  "barwr_detail?id=62",
                                                  "barwr_detail?id=62",
                                                  "barwr_detail?id=43",
                                                  "barwr_detail?id=43",
                                                  "barwr_detail?id=6",
                                                  "barwr_detail?id=6",
                                                  "barwr_detail?id=114",
                                                  "barwr_detail?id=114",
                                                  "barwr_detail?id=8",
                                                  "barwr_detail?id=8",
                                                  "barwr_detail?id=9",
                                                  "barwr_detail?id=9",
                                                  "barwr_detail?id=10",
                                                  "barwr_detail?id=10",
                                                  "barwr_detail?id=12",
                                                  "barwr_detail?id=12",
                                                  "barwr_detail?id=48",
                                                  "barwr_detail?id=48",
                                                  "barwr_detail?id=14",
                                                  "barwr_detail?id=14",
                                                  "barwr_detail?id=72",
                                                  "barwr_detail?id=72",
                                                  "barwr_detail?id=15",
                                                  "barwr_detail?id=15",
                                                  "barwr_detail?id=17",
                                                  "barwr_detail?id=17",
                                                  "barwr_detail?id=50",
                                                  "barwr_detail?id=50",
                                                  "barwr_detail?id=41",
                                                  "barwr_detail?id=41",
                                                  "barwr_detail?id=39",
                                                  "barwr_detail?id=39",
                                                  "barwr_detail?id=53",
                                                  "barwr_detail?id=53",
                                                  "barwr_detail?id=105",
                                                  "barwr_detail?id=105",
                                                  "barwr_detail?id=35",
                                                  "barwr_detail?id=35",
                                                  "barwr_detail?id=115",
                                                  "barwr_detail?id=115",
                                                  "barwr_detail?id=18",
                                                  "barwr_detail?id=18",
                                                  "barwr_detail?id=65",
                                                  "barwr_detail?id=65",
                                                  "barwr_detail?id=55",
                                                  "barwr_detail?id=55",
                                                  "barwr_detail?id=19",
                                                  "barwr_detail?id=19",
                                                  "barwr_detail?id=51",
                                                  "barwr_detail?id=51",
                                                  "barwr_detail?id=21",
                                                  "barwr_detail?id=21",
                                                  "barwr_detail?id=110",
                                                  "barwr_detail?id=110",
                                                  "barwr_detail?id=34",
                                                  "barwr_detail?id=34",
                                                  "barwr_detail?id=23",
                                                  "barwr_detail?id=23",
                                                  "barwr_detail?id=44",
                                                  "barwr_detail?id=44",
                                                  "barwr_detail?id=38",
                                                  "barwr_detail?id=38",
                                                  "barwr_detail?id=66",
                                                  "barwr_detail?id=66",
                                                  "barwr_detail?id=116",
                                                  "barwr_detail?id=116",
                                                  "barwr_detail?id=25",
                                                  "barwr_detail?id=25",
                                                  "barwr_detail?id=73",
                                                  "barwr_detail?id=73",
                                                  "barwr_detail?id=45",
                                                  "barwr_detail?id=45",
                                                  "barwr_detail?id=109",
                                                  "barwr_detail?id=109",
                                                  "barwr_detail?id=74",
                                                  "barwr_detail?id=74",
                                                  "barwr_detail?id=75",
                                                  "barwr_detail?id=75",
                                                  "barwr_detail?id=107",
                                                  "barwr_detail?id=107",
                                                  "barwr_detail?id=26",
                                                  "barwr_detail?id=26",
                                                  "barwr_detail?id=27",
                                                  "barwr_detail?id=27",
                                                  "barwr_detail?id=29",
                                                  "barwr_detail?id=29",
                                                  "barwr_detail?id=30",
                                                  "barwr_detail?id=30",
                                                  "barwr_detail?id=52",
                                                  "barwr_detail?id=52",
                                                  "barwr_detail?id=68",
                                                  "barwr_detail?id=68",
                                                  "barwr_detail?id=111",
                                                  "barwr_detail?id=111",
                                                  "barwr_detail?id=28",
                                                  "barwr_detail?id=28",
                                                  "barwr_detail?id=69",
                                                  "barwr_detail?id=69",
                                                  "barwr_detail?id=70",
                                                  "barwr_detail?id=70",
                                                  "barwr_detail?id=112",
                                                  "barwr_detail?id=112",
                                                  "barwr_detail?id=42",
                                                  "barwr_detail?id=42",
                                                  "barwr_detail?id=47",
                                                  "barwr_detail?id=47",
                                                  "barwr_detail?id=108",
                                                  "barwr_detail?id=108",
                                                  "barwr_detail?id=49",
                                                  "barwr_detail?id=49",
                                                  "barwr_detail?id=33",
                                                  "barwr_detail?id=33"]
                if is_glassware:
                    return ''.join([elem.string for elem in step.contents])
    return None


if __name__ == '__main__':
    process_recipes_file()
    # process_ingredients_file()
