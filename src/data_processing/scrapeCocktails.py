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

MAXIMUM_WORKERS = 10  # number of simultaneous connections

COCKTAILS_FILENAME = 'data/savedCocktails'
INGREDIENTS_FILENAME = 'data/savedIngredients'


def download_all_ingredients():
    print "Downloading all ingredients"
    download_all_pages(
        INGREDIENT_DB_URL, INGREDIENTS_IN_DATABASE, INGREDIENTS_FILENAME)


def download_all_cocktails():
    print "Downloading all cocktails"
    download_all_pages(
        COCKTAIL_DB_URL, COCKTAILS_IN_DATABASE, COCKTAILS_FILENAME)


def download_all_pages(url_prefix, number_of_items, output_filename):
    """
    With MAXIMUM_WORKERS parallel connections, tries to download pages
    prints failures instead of retrying
    :param url_prefix:
    :param number_of_items:
    :param output_filename:
    :return:
    """
    urls = []
    for i in range(1, number_of_items+1):
        urls.append(url_prefix+str(i))

    results = [None]*len(urls)

    def worker():
        while True:
            idx, url = q.get()
            try:
                results[idx] = (urllib2.urlopen(url).read())
                if idx % 1000 == 0:
                    print "FINISHED " + str(idx)
            except Exception as e:
                print e
                print "failed to scrape " + url
            q.task_done()

    q = Queue.Queue()
    for i in range(MAXIMUM_WORKERS):
        t = Thread(target=worker)
        t.daemon = True
        t.start()
    for i, url_to_scrape in enumerate(urls):
        q.put((i, url_to_scrape))
    q.join()

    print "SCRAPED " + str(
        len(results)) + " PAGES, SAVING AS: " + output_filename
    pickle.dump(results, open(output_filename, 'wb'))

if __name__ == '__main__':
    download_all_ingredients()
    download_all_cocktails()