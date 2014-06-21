'''
For parsing (scraped) raw html with BeautifulSoup
'''

from BeautifulSoup import BeautifulSoup
import pickle

from scrapeCocktails import COCKTAILS_FILENAME, INGREDIENTS_FILENAME

CLEANED_COCKTAILS_FILENAME = 'data/cleanedRecipes'
CLEANED_INGREDIENTS_FILENAME = 'data/cleanedIngredients'


'''
Creates a list of lists that contain the (ingredient, amount) 
tuples that compose a recipe; pickles the list.
'''
def processRecipesFile():
	cocktailPages = pickle.load(open(COCKTAILS_FILENAME))
	allRecipes = []
	for i, cocktailPage in enumerate(cocktailPages):
		try:
			soup = BeautifulSoup(cocktailPage)
			measurements = soup.findAll('div', {'class':'recipeMeasure'})
			if (i % 1000 == 0): print 'Parsing recipe ' + str(i)
			recipe = []
			for ingredient in measurements:
				comps = str(ingredient).split('>')
				amount = comps[1].split('<')[0].strip()
				ingredient = comps[2].split('<')[0].strip()
				alternativeAmount = comps[4].split('<')[0].strip()
				recipe.append([ingredient, amount, alternativeAmount])
			allRecipes.append(recipe)
		except Exception as e:
			print e
			print "FAILED TO SCRAPE THIS PAGE EARLIER IN THE PIPELINE"
			continue

	pickle.dump(allRecipes, open(CLEANED_COCKTAILS_FILENAME, 'wb'))


'''
Creates a dictionary where the key is the ingredient and the
value is a list of all the flavors that describe it; pickles the 
dictionary.
'''
def processIngredientsFile():
	ingredientPages = pickle.load(open(INGREDIENTS_FILENAME))
	all_ingredients = {}
	for i, ingredientPage in enumerate(ingredientPages):
		
		try:
			rawText = ingredientPage.split('flavor">')
			if (i % 1000 == 0): print 'Parsing ingredient ' + str(i)
			flavors = []
			for flavor in rawText[1:]:
				flavors.append(flavor.split('<')[0].replace(',', '').replace(' ', '_').lower())
			name = ingredientPage.split('<div id="wellTitle">')[1].split('<h2>')[1].split('<')[0]
			print name, flavors
			all_ingredients[name] = flavors
		except Exception as e:
			print e
			continue
	pickle.dump(all_ingredients, open(CLEANED_INGREDIENTS_FILENAME, 'wb'))	


if __name__ == '__main__':
	processRecipesFile()
	processIngredientsFile()