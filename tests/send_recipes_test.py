import unittest
from unittest.mock import patch, MagicMock

user_states = {
    12345: {
        "recipes": [
            "Рецепт 1\n",
            "Рецепт 2\n",
            "Рецепт 3\n",
            "Рецепт 4\n",
            "Рецепт 5\n"
        ],
        "page": 0
    }
}


class MockBot:
    def send_message(self, chat_id, text, reply_markup=None):
        pass


bot = MockBot()


def send_recipes_page(chat_id: int) -> None:
    user_state = user_states[chat_id]
    recipes = user_state["recipes"]
    page = user_state["page"]

    per_page = 3
    start_index = page * per_page
    end_index = start_index + per_page

    current_page_recipes = recipes[start_index:end_index]
    if current_page_recipes:
        bot.send_message(
            chat_id,
            f"Вот возможные блюда (страница {page + 1}):\n{''.join(current_page_recipes)}",
        )

        if len(recipes) > end_index:
            markup = MagicMock()
            markup.add(
                MagicMock()
            )
            bot.send_message(chat_id, "Показать еще?", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Больше рецептов нет.")


class TestSendRecipesPage(unittest.TestCase):

    def setUp(self):
        self.user_states_backup = user_states.copy()
        user_states[12345] = {
            "recipes": [
                "Рецепт 1\n",
                "Рецепт 2\n",
                "Рецепт 3\n",
                "Рецепт 4\n",
                "Рецепт 5\n"
            ],
            "page": 0
        }

    def tearDown(self):
        global user_states
        user_states = self.user_states_backup

    @patch.object(bot, 'send_message')
    def test_send_recipes_successfully(self, mock_send_message):
        send_recipes_page(12345)
        mock_send_message.assert_any_call(12345, "Вот возможные блюда (страница 1):\nРецепт 1\nРецепт 2\nРецепт 3\n")

    @patch.object(bot, 'send_message')
    def test_no_more_recipes(self, mock_send_message):
        user_states[12345]["page"] = 2
        send_recipes_page(12345)
        mock_send_message.assert_called_with(12345, "Больше рецептов нет.")

    @patch.object(bot, 'send_message')
    def test_empty_recipes_list(self, mock_send_message):
        user_states[12345]["recipes"] = []
        send_recipes_page(12345)
        mock_send_message.assert_called_with(12345, "Больше рецептов нет.")


if __name__ == "__main__":
    unittest.main()
