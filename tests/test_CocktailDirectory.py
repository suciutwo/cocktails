"""Test for CocktailDirectory"""

from src.CocktailDirectory import CocktailDirectory


class TestCocktailDirectory:

    def __init__(self):
        self.dir = None

    def setup(self):
        self.dir = CocktailDirectory()

    def test_recipe(self):
        assert self.dir.recipe('martini') is None
        martini_recipe = [(u'dry vermouth', 0.25), (u'lemon twist', 0.5), (u'olive', 0.5), (u'gin', 2.25)]
        martini_result = self.dir.recipe('Martini (extra Dry)')
        assert martini_result[0][0] == 'gin'
        assert set(martini_result) == set(martini_recipe), martini_result

    def test_random_drinks(self):
        assert len(self.dir.random_drinks(4)) > 3
        assert len(self.dir.random_drinks(5)) == 5

    def test_all_ingredients(self):
        count = len(self.dir.all_ingredients())
        assert count == 450, "ALL INGREDIENTS " + str(count)

    def test_search_all(self):
        d = self.dir
        all_recipes = d.search()
        assert len(all_recipes) == 4502, len(all_recipes)

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
        # for thing in can_make:
        #     print thing
        assert len(can_make) == 33, len(can_make)
        assert set(can_make[0][0]) == {u'sweet vermouth'}, can_make[0][0]
        assert len(can_make[0][1]) == 4, can_make[0][1]