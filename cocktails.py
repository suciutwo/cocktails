from bs4 import BeautifulSoup
import urllib2
from threading import Thread
import pickle
import Queue
def scanRecipe():
	soup=BeautifulSoup(urlopen(url))
	l=soup.findAll('li', {'class':'ingredient'})

COCKTAILS_ON_DATABASE = 4758
INTERNET_DB_URL = 'http://www.cocktaildb.com/recipe_detail?id='

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
def processRecipes():
	d = pickle.load(open("savedCocktails"))
	all_recipes = []
	for i, d_i in enumerate(d):
		soup=BeautifulSoup(d_i)
		l=soup.findAll('div', {'class':'recipeMeasure'})
		print 'Recipe %i' % (i)
		recipe = []
		try:
			for ingredient in l:
				comps = str(ingredient).split('>')
				amount = comps[1].split('<')[0].strip()
				ingredient = comps[2].split('<')[0].strip()
				recipe.append([ingredient, amount])
			all_recipes.append(recipe)
		except:
			continue
	pickle.dump(all_recipes, open("cleanedRecipes", 'wb'))	
if __name__ == '__main__':
	download = 0
	if download:
		downloadAllPages()
	else:
		processRecipes()	




