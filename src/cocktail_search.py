"""Utilities for searching."""


def possible_cocktails(available_ingredients, cocktails):
    """Returns all cocktails that can be made with ingredients on hand."""
    possible = []
    for cocktail in cocktails:
        has_all = True
        for ingredient in cocktail:
            if ingredient not in available_ingredients:
                has_all = False
                break
        if not has_all:
            possible.append(cocktail)
    return possible


def cocktails_missing_n_ingredients(available_ingredients, cocktails, n):
    """Returns all cocktails that can be made, missing up to n ingredients."""
    query_result = []
    for cocktail in cocktails:
        missing = 0
        for ingredient in cocktail:
            if ingredient not in available_ingredients:
                missing += 1
        if missing <= n:
            query_result.append(cocktail)
    return query_result
