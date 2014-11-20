"""A directory of cocktails for searching."""
import random
from data_processing.matrix_generation import recipe_data


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
            self._dictionary[name] = recipe

    def random_drinks(self, n):
        """ Select n random elements from the directory.
            Return [(key, value)]."""
        selection = random.sample(self._dictionary.items(), n)
        return [(name, recipe) for name, recipe in selection]

    def all_ingredients(self):
        """ Provide a list of all ingredient names. """
        return list(self._ingredients)

    def recipe(self, name):
        """Provide the recipe for a single name."""
        return self._dictionary.get(name)

    def search(self, required=None, forbidden=None):
        """All cocktails without forbidden elements, but with required."""
        if required:
            required = {i for i in required if i in self._ingredients}
        if forbidden:
            forbidden = {i for i in forbidden if i in self._ingredients}
        if not required and not forbidden:
            return self._dictionary.items()
        allowed = []
        for name, recipe in self._dictionary.iteritems():
            ingredients = {ingredient for ingredient, amount in recipe}
            if required and not required.intersection(ingredients):
                continue
            if forbidden and forbidden.intersection(ingredients):
                continue
            allowed.append((name, recipe))
        return allowed

    def flexible_search(self, liquor_on_shelf, allowed_missing_elements=0):
        """Return all cocktails that can be made, buying only n ingredients."""
        if liquor_on_shelf:
            liquor_on_shelf = {i for i in liquor_on_shelf if i in self._ingredients}
        else:
            liquor_on_shelf = set([])
        allowed = {}
        for name, recipe in self._dictionary.iteritems():
            ingredients = {ingredient for ingredient, amount in recipe}
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


if __name__ == '__main__':
    import doctest
    doctest.testmod()