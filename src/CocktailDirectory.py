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

    def search(self, owned=None, required=None, forbidden=None):
        """ All cocktails without forbidden elements, but with required.
            If owned is not None, all cocktails returned will use only owned ingredients. """
        if required:
            required = {ingredient for ingredient in required
                        if ingredient in self._ingredients}
        if forbidden:
            forbidden = {ingredient for ingredient in forbidden
                         if ingredient in self._ingredients}
        if owned:
            owned = {ingredient for ingredient in owned
                       if ingredient in self._ingredients}
        if not owned and not required and not forbidden:
            return self._dictionary.values()
        allowed = []
        for cocktail in self._dictionary.itervalues():
            ingredients = {instruction.ingredient
                           for instruction in cocktail.recipe}
            if owned and not ingredients.issubset(owned):
                continue
            if required and not required.issubset(ingredients):
                continue
            if forbidden and forbidden.intersection(ingredients):
                continue
            allowed.append(cocktail)
        return allowed

    def flexible_search(self, owned, required=None, forbidden=None, allowed_missing_elements=0):
        """Return all cocktails that can be made, buying only n ingredients."""
        if owned:
            owned = {ingredient for ingredient in owned
                               if ingredient in self._ingredients}
        else:
            owned = set([])
        if required:
            required = {ingredient for ingredient in required
                        if ingredient in self._ingredients}
        if forbidden:
            forbidden = {ingredient for ingredient in forbidden
                        if ingredient in self._ingredients}
        result_dictionary = {}
        for name, cocktail in self._dictionary.iteritems():
            ingredients = {instruction.ingredient for instruction in cocktail.recipe}
            if required and not required.issubset(ingredients):
                continue
            if forbidden and forbidden.intersection(ingredients):
                continue
            missing_ingredients = ingredients - owned
            if 0 < len(missing_ingredients) <= allowed_missing_elements:
                missing_ingredients = list(missing_ingredients)
                missing_ingredients.sort()
                missing_ingredients = '*^*'.join(missing_ingredients)
                if missing_ingredients not in result_dictionary:
                    result_dictionary[missing_ingredients] = set([])
                result_dictionary[missing_ingredients].add(name)

        sorted_missing_ingredients = sorted(result_dictionary, reverse=True, key=lambda k: len(result_dictionary[k]))
        result = []
        for key in sorted_missing_ingredients:
            ingredients = key.split('*^*')
            result.append((ingredients, result_dictionary[key]))
        return result
