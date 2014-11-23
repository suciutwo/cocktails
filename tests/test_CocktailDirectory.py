"""Test for CocktailDirectory"""

from src.CocktailDirectory import CocktailDirectory, Cocktail


class TestCocktailDirectory:

    martini_recipe = [(u'gin', 2.25), (u'olive', 0.5), (u'lemon twist', 0.5), (u'dry vermouth', 0.25)]
    martini_cocktail = Cocktail('Martini (extra Dry)', martini_recipe)

    def __init__(self):
        self.dir = None

    def setup(self):
        self.dir = CocktailDirectory()

    def test_serialize(self):
        assert self.martini_cocktail.json() == """{"name": "Martini (extra Dry)", "recipe": [{"ingredient": "gin", "amount": 2.25}, {"ingredient": "olive", "amount": 0.5}, {"ingredient": "lemon twist", "amount": 0.5}, {"ingredient": "dry vermouth", "amount": 0.25}]}"""

    def test_cocktail(self):
        assert not self.dir.cocktail('martini'), self.dir.cocktail('martini')
        martini_result = self.dir.cocktail('Martini (extra Dry)')
        assert martini_result.recipe[0].ingredient == 'gin', martini_result.recipe
        assert martini_result == self.martini_cocktail, martini_result

    def test_cocktails(self):
        assert not self.dir.cocktails(['martini', 'blah'])
        martini_result = self.dir.cocktails(['Martini (extra Dry)'])[0]
        assert martini_result.recipe[0].ingredient == 'gin', martini_result.recipe
        assert martini_result == self.martini_cocktail, self.martini_cocktail

    def test_random_drinks(self):
        assert len(self.dir.random_cocktails(4)) > 3
        assert len(self.dir.random_cocktails(5)) == 5

    def test_all_ingredients(self):
        count = len(self.dir.all_ingredients())
        assert count == 450, "ALL INGREDIENTS " + str(count)

    def test_search_all(self):
        d = self.dir
        all_recipes = d.search()
        assert len(all_recipes) == 4502, len(all_recipes)


    def test_search_have(self):
        d = self.dir
        results = d.search(owned=['gin', 'dry vermouth', 'olive', 'lemon twist'])
        assert len(results) == 7, len(results)

    def test_search_gin(self):
        d = self.dir
        drinks_with_gin = d.search(required=['gin'])
        assert len(drinks_with_gin) == 1275, len(drinks_with_gin)
        drinks_with_gin = d.search(required=['gin', 'gklkakja'])
        assert len(drinks_with_gin) == 1275, len(drinks_with_gin)

    def test_search_no_gin(self):
        d = self.dir
        drinks_no_gin = d.search(forbidden=['gin'])
        assert len(drinks_no_gin) == 3227, len(drinks_no_gin)
        drinks_no_gin = d.search(required=['kkkkjdk'], forbidden=['gin', 'something madeup??!'])
        assert len(drinks_no_gin) == 3227, len(drinks_no_gin)

    def test_search_no_gin_with_vodka(self):
        d = self.dir
        drinks_with_gin = d.search(required=['vodka'], forbidden=['gin'])
        assert len(drinks_with_gin) == 208, len(drinks_with_gin)

    def test_flex_search(self):
        d = self.dir
        can_make = d.flexible_search(['gin'], 1)
        assert len(can_make) == 33, len(can_make)
        assert set(can_make[0][0]) == {u'sweet vermouth'}, can_make[0][0]
        assert len(can_make[0][1]) == 4, can_make[0][1]