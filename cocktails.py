import urllib2
from BeautifulSoup import BeautifulSoup
from threading import Thread
import pickle
import Queue

COCKTAILS_ON_DATABASE = 4758
INTERNET_DB_URL = 'http://www.cocktaildb.com/recipe_detail?id='

def downloadAllPages():
	WORKERS = 20

	urls = []
	for i in range(1, COCKTAILS_ON_DATABASE):
		urls.append(INTERNET_DB_URL+str(i))

	results = [None]*len(urls)
	
	def worker():
		while True:
			i, url = q.get()
			try: 
				results[i] = (urllib2.urlopen(url).read())
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




def loadAllPages():
	return pickle.load(open("savedCocktails", 'rb'))


if __name__ == '__main__':
	data = loadAllPages()
	for page in data:
		soup = BeautifulSoup(page)
	#	title = soup.title.string.split(' | ')[1]
	#	print title
		for thing in soup:
			print thing
			break
		
		print soup
		ingredients = soup.find_all(class_="recipeMeasure")
		#print len(ingredients)
		#print ingredients
		break
	




