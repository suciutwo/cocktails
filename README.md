Directory Structure:

	data - coctail/ingredient data
	src - source code
	results - algorithm output


Data Collection Pipeline:
Gets data from the website and makes it (basically) accessible

	Steps:
	1) run scrapeCocktails: script for downloading raw html from the website
	2) run parsePages: script for parsing downloaded raw html

	This results in:
		"savedCocktails" --all cocktail html
		"savedIngredients" --all ingredient html

		"cleanedCocktails" --result of parsing cocktails
		"cleanedIngredients"  --result of parsing ingredients


Data Formatting Pipeline:

	TBD
	