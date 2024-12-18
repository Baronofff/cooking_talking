import unittest

import pytest

headers = ["Категория", "Заголовок", "Ингредиенты", "Ссылка"]
all_recipes = [
    headers,
    ["Завтрак", "Омлет", "яйца, молоко, соль", "http://example.com/omlet"],
    ["Ужин", "Спагетти", "макароны, томаты, соль", "http://example.com/spaghetti"],
    ["Ужин", "Салат", "огурцы, помидоры, соль", "http://example.com/salad"],
]


def get_recipes_by_ingredients(user_input: str) -> list:
    result = []
    ingredients = set(user_input.lower().split(", "))

    ingredient_index = headers.index("Ингредиенты")

    item = 1
    for recipe in all_recipes[1:]:
        recipe_ingredients = set(recipe[ingredient_index].lower().split(", "))
        if ingredients.issubset(recipe_ingredients):
            result.append(
                f"{recipe[headers.index('Категория')]}\n#{item}: {recipe[headers.index('Заголовок')]}\n"
                f"Дополнительно понадобятся: "
                f"\n{', '.join(recipe_ingredients.difference(ingredients))}"
                f"\n{recipe[headers.index('Ссылка')]}\n\n"
            )
            item += 1
    if not result:
        result.append(
            "В нашей базе нет ни одного рецепта с использованием этих ингредиентов :("
        )
    return result


class TestGetRecipesByIngredients(unittest.TestCase):

    def test_valid_ingredients(self):
        user_input = "яйца, молоко"
        expected_output = [
            "Завтрак\n#1: Омлет\nДополнительно понадобятся: \nсоль\nhttp://example.com/omlet\n\n"
        ]
        self.assertEqual(get_recipes_by_ingredients(user_input), expected_output)

    @pytest.mark.skip(reason='rework')
    def test_partial_matches(self):
        user_input = "яйца"
        expected_output = [
            "Завтрак\n#1: Омлет\nДополнительно понадобятся: \nмолоко, соль\nhttp://example.com/omlet\n\n"
        ]

        actual_output = get_recipes_by_ingredients(user_input)

        def normalize_output(output):
            return [
                line if not line.startswith('Дополнительно понадобятся:') else
                line.split(': ')[0] + ': ' + ', '.join(sorted(line.split(': ')[1].strip().split(', ')))
                for line in output
            ]

        self.assertEqual(sorted(normalize_output(actual_output)), sorted(normalize_output(expected_output)))

    def test_no_matches(self):
        user_input = "мясо"
        expected_output = [
            "В нашей базе нет ни одного рецепта с использованием этих ингредиентов :("
        ]
        self.assertEqual(get_recipes_by_ingredients(user_input), expected_output)

    def test_empty_input(self):
        user_input = ""
        expected_output = [
            "В нашей базе нет ни одного рецепта с использованием этих ингредиентов :("
        ]
        self.assertEqual(get_recipes_by_ingredients(user_input), expected_output)


if __name__ == "__main__":
    unittest.main()
