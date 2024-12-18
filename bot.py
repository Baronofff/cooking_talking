import json
import telebot
import random
import redis
import logging
from qa_model import model_pipeline


# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
with open("token.txt", "r", encoding="utf-8") as f:
    token = f.read().strip()
bot = telebot.TeleBot(token)

#Подгружение данных, необходимых для модели
with open('context.txt', 'r', encoding='utf-8') as file:
    CONTEXT = file.read()

# Инициализация Redis
try:
    r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    logging.info("Подключение к Redis успешно.")
except Exception as e:
    logging.error(f"Ошибка подключения к Redis: {e}")

# Определеение режимов работы бота
MODE_RECIPES = 'recipes'
MODE_QUESTIONS = 'questions'

# Переменная для хранения текущего режима
current_mode = MODE_RECIPES

#Подгрузка данных json (результат парсинга)
with open("data/recipes_data.json", "r", encoding="UTF-8") as file:
    all_recipes = json.load(file)
user_states = {}
headers = all_recipes[0]


def get_recipes_by_ingredients(user_input: str) -> list:
    """
    Retrieves recipes that can be made with the specified ingredients.

    Args:
        user_input (str): User input of ingredients
        (separated by commas)

    Returns:
        list: List of recipes with given ingredients or
        an explanation message (there are no recipes with such ingredients)

    """
    result = []
    ingredients = set(user_input.lower().split(", "))

    ingredient_index = headers.index("Ингредиенты")

    item = 1
    for recipe in all_recipes[1:]:
        recipe_ingredients = set(recipe[ingredient_index])
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


def send_recipes_page(chat_id: int) -> None:
    """
    Sends a page of recipes to the user in a Telegram chat.

    Args:
        chat_id (int): The user id in Telegram chat

    Returns:
        None. It directly sends message to the user.

    """
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
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(
                telebot.types.InlineKeyboardButton(
                    "Вывести еще", callback_data=f"next_{chat_id}"
                )
            )
            bot.send_message(chat_id, "Показать еще?", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Больше рецептов нет.")


def create_category_keyboard():
    """
     Creates a keyboard for selecting recipe categories in a Telegram bot.

    Returns:
        telebot.types.ReplyKeyboardMarkup: A keyboard markup object
        with recipe categories.
    """
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        "Горячее",
        "Десерты",
        "Закуски",
        "Напитки",
        "Блюда из пищи животного происхождения",
        "Салаты",
        "Другое",
        "Выпечка",
        "Гарниры",
        "Завтраки",
    )
    return markup


def handle_category(message: telebot.types.Message) -> None:
    """
    Handles the user's selection of a recipe category.

    Args:
        message (telebot.types.Message): The message object containing the user's
        selected category.

    Returns:
        None. This function will either send recipes for a specific category
         or a message indicating that there are no recipes available.
    """
    category = message.text
    recipe_list = []
    cat_index = headers.index("Категория")

    for recipe in all_recipes[1:]:  # Start from the second line (data)
        if category in recipe[headers.index("Категория")]:
            ingredients_string = recipe[cat_index]  # Get ingredients as string
            ingredients_list = ingredients_string.split(", ")  # Split into a list
            recipe_list.append(
                f"# {recipe[headers.index('Заголовок')]}\n"
                f"Понадобятся:\n{', '.join(ingredients_list)}\n"
                f"{recipe[headers.index('Ссылка')]}\n\n"
            )

    if recipe_list:
        random_recipes = random.sample(recipe_list, min(5, len(recipe_list)))
        response = f"Рецепты для категории '{category}':\n{''.join(random_recipes)}"
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, f"В категории '{category}' нет рецептов.")


@bot.message_handler(commands=["start"])
def send_welcome(message: telebot.types.Message) -> None:
    """
    Sends a welcome message to the user when they start the bot.

    Args:
        message (telebot.types.Message): The message with information
        about the user's input (it also contains the chat id).

    Returns:
        None. It sends a message to the user and displays a keyboard
         for category selection.
    """
    bot.send_message(
        message.chat.id,
        "Привет! Введи ингредиенты, или выбери категорию:\nФормат ввода:\n мука, молоко",
        reply_markup=create_category_keyboard(),
    )


@bot.message_handler(commands=["help"])
def start_message(message: telebot.types.Message) -> None:
    """
    Sends a help message to the user when they request it.

    Args:
        message (telebot.types.Message): The message with information
        about the user's input (it also contains the chat id).

    Returns:
        None. It sends a link to the help instructions.
    """
    bot.send_message(
        message.chat.id, "Ознакомьтесь с инструкцией: https://clck.ru/3FJ9NC"
    )


@bot.message_handler(commands=['mode'])
def switch_mode(message: telebot.types.Message)-> None:
    """
    Switches the current mode of the bot between recipe search and question answering.

    Args:
        message (telebot.types.Message): The message with information
        about the user's input (it also contains the chat id).

    Returns:
        None. It changes the current_mode and sends a message to the user
        confirming the new mode.
    """
    global current_mode
    if current_mode == MODE_RECIPES:
        current_mode = MODE_QUESTIONS
        bot.send_message(message.chat.id, "Режим переключен: задавайте вопросы")
    else:
        current_mode = MODE_RECIPES
        bot.send_message(message.chat.id, "Режим переключен: ищите рецепты.")



@bot.message_handler(func=lambda message: current_mode == MODE_RECIPES)
def send_recipes(message: telebot.types.Message) -> None:
    """
    Handles incoming messages when the bot is in recipe search mode.

    Args:
        message (telebot.types.Message): The message with information
        about the user's input (it also contains the chat id).

    Returns:
        None. It sends recipe information to the user based on their input.
    """
    user_input = message.text
    if user_input in [
        "Горячее",
        "Десерты",
        "Закуски",
        "Напитки",
        "Блюда из пищи животного происхождения",
        "Салаты",
        "Другое",
        "Выпечка",
        "Гарниры",
        "Завтраки",
    ]:
        handle_category(message)
    else:
        recipes = get_recipes_by_ingredients(user_input)
        user_states[message.chat.id] = {"recipes": recipes, "page": 0}
        send_recipes_page(message.chat.id)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: telebot.types.CallbackQuery) -> None:
    """
    Handles callback queries from the user, specifically for changing the page
    of recipe results.

    Args:
        call (telebot.types.CallbackQuery): The object containing information
        about the user's action, including the data associated with
        the callback and the user's chat ID.

    Returns:
        None. It modifies the user_states and sends updated recipe information
        based on their navigation request.
    """
    if call.data.startswith("next_"):
        chat_id = int(call.data.split("_")[1])
        user_states[chat_id]["page"] += 1
        send_recipes_page(chat_id)
        bot.answer_callback_query(call.id)


# Функция для получения информации о вопросе из кэша или API
def get_question_from_cache(question: str) -> dict|None:
    """
    Retrieves the cached answer for a given question.

    Args:
        question (str): The question (user input) for which the cached answer
        is to be retrieved.

    Returns:
        The deserialized answer as a dictionary or None if no answer is found
        or if an error occurs during retrieval.
    """
    try:
        cached_info = r.get(question)
        if cached_info:
            logging.info(f"Ответ найден в кэше для вопроса: {question}")
            return json.loads(cached_info)  # Десериализация JSON
        else:
            logging.info(f"Ответ не найден в кэше для вопроса: {question}")
            return None
    except Exception as e:
        logging.error(f"Ошибка при получении данных из кэша: {e}")
        return None


@bot.message_handler(func=lambda message: current_mode == MODE_QUESTIONS)
def handle_questions(message: telebot.types.Message) -> None:
    """
    Handles incoming messages(questions) when the bot is in QUESTION mode.

    Args:
        message (): The incoming message object containing the user's question

    Returns:
        None. The function sends a message with an answer
        back to the user
    """
    question = message.text
    answer_info = get_question_from_cache(question)
    print(answer_info)

    if answer_info:
        # Отправляем информацию о сообщении пользователю
        bot.send_message(message.chat.id, answer_info)
    else:
        try:
            # Получаем ответ от модели
            question_answer = model_pipeline(question=question, context=CONTEXT)['answer']
            # Сохраняем ответ в кэш
            r.setex(question, 3600, json.dumps(question_answer))  # Сохраняем как строку JSON
            logging.info(f"Ответ сохранен в кэше для вопроса: {question}")
            # Отправляем ответ пользователю
            bot.send_message(message.chat.id, question_answer)
            print(question_answer)
        except Exception as e:
            logging.error(f"Ошибка при получении ответа от модели: {e}")
            bot.send_message(message.chat.id, "Извините, произошла ошибка при обработке вашего запроса.")


# Запускаем бот
if __name__ == "__main__":
    try:
        bot.polling()
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")