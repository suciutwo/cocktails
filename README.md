Directory Structure:

	data - coctail/ingredient data
	src - source code
	results - algorithm output


Data Collection Pipeline:
Gets data from the website and parses that into accessible data

	Steps:
	1) run scrapeCocktails: script for downloading raw html from the website
	2) run parsePages: script for parsing downloaded raw html

	This results in:
		"savedCocktails" --all cocktail html
		"savedIngredients" --all ingredient html

		"cleanedCocktails" --result of parsing cocktails
		"cleanedIngredients"  --result of parsing ingredients


Data Formatting Pipeline:
Puts data in a matrix so you can have fun with numpy

	Steps:
	1) You need a dictionary that maps strings like "2 dashes" to floats.
	This should exist as data/amoutParsingMapping, but you can run the function
	of the same name (in src/matrixGeneration) to generate a new one. Be warned,
	it requires your effort for several hours.
	
	2) Now call either one of the matrix generating functions to get the data
	you want as a matrix. You'll also get back an index which maps from row or
	column numbers to actual strings and vice versa.


Matrix Factoring:

	matrixFactorization: currently, this is some code that just plays with NMF
	