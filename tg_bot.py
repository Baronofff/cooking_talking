import telebot
import redis
import json
import logging
from qa_model import model_pipeline

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = telebot.TeleBot('7338498731:AAHgdp_Ep3tXkO9Wb5boVSMf-0kRdaV9-1o')

with open('context.txt', 'r', encoding='utf-8') as file:
    CONTEXT = file.read()

# Инициализация Redis
try:
    r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    logging.info("Подключение к Redis успешно.")
except Exception as e:
    logging.error(f"Ошибка подключения к Redis: {e}")

# Функция для получения информации о вопросе из кэша или API
def get_question_from_cache(question):
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

@bot.message_handler(func=lambda message: True)
def handle_movie_command(message):
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
            # logging.info(f"Ответ сохранен в кэше для вопроса: {question}")
            # Отправляем ответ пользователю
            bot.send_message(message.chat.id, question_answer)
            print(question_answer)
        except Exception as e:
            # logging.error(f"Ошибка при получении ответа от модели: {e}")
            bot.send_message(message.chat.id, "Извините, произошла ошибка при обработке вашего запроса.")

# Запускаем бот
if __name__ == "__main__":
    try:
        bot.polling()
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")
