'''
This code is concerned with downloading pages from the website, not processing them.
'''

import urllib2
from threading import Thread
import pickle
import Queue

COCKTAILS_IN_DATABASE = 4758
COCKTAIL_DB_URL = 'http://www.cocktaildb.com/recipe_detail?id='
INGREDIENTS_IN_DATABASE = 558
INGREDIENT_DB_URL = 'http://www.cocktaildb.com/ingr_detail?id='

MAXIMUM_WORKERS = 10 #number of simultaneous connections

COCKTAILS_FILENAME = 'data/savedCocktails'
INGREDIENTS_FILENAME = 'data/savedIngredients'



def downloadAllIngredients():
	print "Downloading all ingredients"
	downloadAllPages(INGREDIENT_DB_URL, INGREDIENTS_IN_DATABASE, INGREDIENTS_FILENAME)

def downloadAllCocktails():
	print "Downloading all cocktails"
	downloadAllPages(COCKTAIL_DB_URL, COCKTAILS_IN_DATABASE, COCKTAILS_FILENAME)	

##With MAXIMUM_WORKERS parallel connections, tries to download pages 
## prints failures instead of retrying
def downloadAllPages(urlPrefix, numberOfItems, outputFilename):

	urls = []
	for i in range(1, numberOfItems+1):
		urls.append(urlPrefix+str(i))

	results = [None]*len(urls)

	def worker():
		n_read = 0
		while True:
			i, url = q.get()
			try: 
				results[i] = (urllib2.urlopen(url).read())
				if (i % 1000 == 0): print "FINISHED " + str(i)
			except Exception as e:
				print e
				print "failed to scrape " + url
			q.task_done()

	q = Queue.Queue()
	for i in range(MAXIMUM_WORKERS):
		t = Thread(target=worker)
		t.daemon = True
		t.start()

	for i, url in enumerate(urls):
		q.put((i, url))

	q.join()

	print "SCRAPED " + str(len(results)) + " PAGES, SEE ABOVE FOR ERRORS CORRESPONDING TO MISSING DATA... SAVING AS: " + outputFilename 
	pickle.dump(results, open(outputFilename, 'wb'))

if __name__ == '__main__':
	downloadAllIngredients()
	downloadAllCocktails()