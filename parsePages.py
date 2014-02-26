'''
For parsing (scraped) raw html with BeautifulSoup
'''

from BeautifulSoup import BeautifulSoup
import pickle

from scrapeCocktails import COCKTAILS_FILENAME, INGREDIENTS_FILENAME

CLEANED_COCKTAILS_FILENAME = 'cleanedRecipes'
CLEANED_INGREDIENTS_FILENAME = 'cleanedIngredients'


def processRecipes():
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
				#alternativeAmount = comps[4].split('<')[0].strip()
				recipe.append([ingredient, amount])
			allRecipes.append(recipe)
		except Exception as e:
			print e
			print "FAILED TO SCRAPE THIS PAGE EARLIER IN THE PIPELINE"
			continue

	pickle.dump(all_recipes, open(CLEANED_COCKTAILS_FILENAME, 'wb'))


def processIngredientsFile():
	d = pickle.load(open(INGREDIENTS_FILENAME))
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
		except Exception as e:
			print e
			continue
	#print all_ingredients
	pickle.dump(all_ingredients, open(CLEANED_INGREDIENTS_FILENAME, 'wb'))	


if __name__ == '__main__':
	processRecipes()
	processIngredientsFile()