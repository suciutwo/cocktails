"""
This code is concerned with downloading pages from the website,
not processing them. For processing your download, see parse_pages.
"""

import urllib2
from threading import Thread
import pickle
import Queue

import src.constants as constants


COCKTAILS_IN_DATABASE = 4758
COCKTAIL_DB_URL = 'http://www.cocktaildb.com/recipe_detail?id='
INGREDIENTS_IN_DATABASE = 558
INGREDIENT_DB_URL = 'http://www.cocktaildb.com/ingr_detail?id='

MAXIMUM_WORKERS = 10  # number of simultaneous connections


def download_all_ingredients():
    """
    Downloads all ingredient html from the cocktaildb and
    overwrites your old downloads if they exist.
    """
    print "Downloading all ingredients"
    download_all_pages(
        INGREDIENT_DB_URL,
        INGREDIENTS_IN_DATABASE,
        constants.INGREDIENTS_FILENAME)


def download_all_cocktails():
    """
    Downloads all cocktail html from the cocktaildb and
    overwrites your old downloads if they exist.
    """
    print "Downloading all cocktails"
    download_all_pages(
        COCKTAIL_DB_URL, COCKTAILS_IN_DATABASE, constants.COCKTAILS_FILENAME)


def download_all_pages(url_prefix, number_of_items, output_filename):
    """
    With MAXIMUM_WORKERS parallel connections, tries to download pages
    prints failures instead of retrying
    """
    urls = []
    for i in range(1, number_of_items+1):
        urls.append(url_prefix+str(i))

    results = [None]*len(urls)

    def worker():
        """
        Scrapes urls it takes from the queue.
        """
        while True:
            idx, url = queue.get()
            try:
                results[idx] = (urllib2.urlopen(url).read())
                if idx % 1000 == 0:
                    print "FINISHED " + str(idx)
            except Exception as exception:  # pylint: disable=W0703
                print exception
                print "failed to scrape " + url
            queue.task_done()

    queue = Queue.Queue()
    for i in range(MAXIMUM_WORKERS):
        thread = Thread(target=worker)
        thread.daemon = True
        thread.start()
    for i, url_to_scrape in enumerate(urls):
        queue.put((i, url_to_scrape))
    queue.join()

    print "SCRAPED " + str(
        len(results)) + " PAGES, SAVING AS: " + output_filename
    pickle.dump(results, open(output_filename, 'wb'))

if __name__ == '__main__':
    download_all_ingredients()
    download_all_cocktails()
