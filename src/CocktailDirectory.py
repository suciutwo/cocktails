"""A directory of cocktails for searching."""
import json
import random

from data_processing.matrix_generation import recipe_data
from collections import namedtuple


RecipeInstruction = namedtuple("RecipeInstruction", ['ingredient', 'amount'])


CocktailBase = namedtuple("Cocktail", ['name', 'recipe'])


class Cocktail(CocktailBase):

    def __new__(cls, name, ingredient_and_amount_list):
        recipe = [RecipeInstruction(ingredient, amount)
                for ingredient, amount in ingredient_and_amount_list]
        self = super(Cocktail, cls).__new__(cls, name, recipe)
        return self

    def _asdict(self):
        recipe_as_dict = [step._asdict() for step in self.recipe]
        return CocktailBase(self.name, recipe_as_dict)._asdict()

    def json(self):
        return json.dumps(self._asdict())


class CocktailDirectory:

    _dictionary = {}
    _ingredients = set([])

    def __init__(self):
        """Parse cocktail recipes from disk if not parsed."""
        if self._dictionary:
            return
        dataframe = recipe_data(None)
        for name, ingredient_series in dataframe.iterrows():
            recipe = []
            ingredient_series.sort(ascending=False)
            for ingredient, amount in ingredient_series.iteritems():
                if amount > 0:
                    ingredient = ingredient.replace('_', ' ')
                    self._ingredients.add(ingredient)
                    recipe.append((ingredient, amount))
            self._dictionary[name] = Cocktail(name, recipe)

    def random_cocktails(self, n):
        """ Select n random cocktails from the directory.
            Return list of cocktail objects."""
        return random.sample(self._dictionary.items(), n)

    def all_ingredients(self):
        """ Provide a list of all ingredient names. """
        return list(self._ingredients)

    def cocktails(self, names):
        """Bulk cocktail search. Returns list of cocktail objects."""
        return [self.cocktail(name) for name in names
                if name in self._dictionary]

    def cocktail(self, name):
        """Provide the cocktail object for a single name."""
        return self._dictionary.get(name)

    def search(self, required=None, forbidden=None):
        """All cocktails without forbidden elements, but with required."""
        if required:
            required = {ingredient for ingredient in required
                        if ingredient in self._ingredients}
        if forbidden:
            forbidden = {ingredient for ingredient in forbidden
                         if ingredient in self._ingredients}
        if not required and not forbidden:
            return self._dictionary.values()
        allowed = []
        for cocktail in self._dictionary.itervalues():
            ingredients = {instruction.ingredient
                           for instruction in cocktail.recipe}
            if required and not required.intersection(ingredients):
                continue
            if forbidden and forbidden.intersection(ingredients):
                continue
            allowed.append(cocktail)
        return allowed

    def flexible_search(self, liquor_on_shelf, allowed_missing_elements=0):
        """Return all cocktails that can be made, buying only n ingredients."""
        if liquor_on_shelf:
            liquor_on_shelf = {ingredient for ingredient in liquor_on_shelf
                               if ingredient in self._ingredients}
        else:
            liquor_on_shelf = set([])
        allowed = {}
        for name, cocktail in self._dictionary.iteritems():
            ingredients = {instruction.ingredient for instruction in cocktail.recipe}
            missing = ingredients - liquor_on_shelf
            if len(missing) == allowed_missing_elements:
                missing = list(missing)
                missing.sort()
                key = '*^*'.join(missing)
                if key not in allowed:
                    allowed[key] = set([])
                allowed[key].add(name)

        sorted_keys = sorted(allowed, reverse=True, key=lambda k: len(allowed[k]))
        result = []
        for key in sorted_keys:
            ingredients = key.split('*^*')
            result.append((ingredients, allowed[key]))
        return result
