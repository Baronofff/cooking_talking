# milyausha2801/rubert-russian-qa-sberquad
#
# from transformers import AutoTokenizer, AutoModelForCausalLM
#
# tokenizer = AutoTokenizer.from_pretrained("ai-forever/rugpt3large_based_on_gpt2")
# model = AutoModelForCausalLM.from_pretrained("ai-forever/rugpt3large_based_on_gpt2")
#
# print('hi')

# Use a pipeline as a high-level helper
# from transformers import pipeline
#
# pipe = pipeline("question-answering", model="ydshieh/tiny-random-gptj-for-question-answering")
# preds = pipe(
#     question="What is the name of the repository?",
#     context="The name of the repository is huggingface/transformers"
#
# )
# print(preds)


from transformers import pipeline

# Создаем пайплайн для задачи question answering
# Use a pipeline as a high-level helper
# =================
# from transformers import pipeline
#
# qa_pipeline = pipeline("question-answering", model="milyausha2801/rubert-russian-qa-sberquad")
#
# # Контекст и вопрос
# context = "Мама мыла раму."
# question = "Кто мыл раму?"
#
# # Получение ответа
# result = qa_pipeline({
#     'question': question,
#     'context': context
# })
#
# # Распечатка ответа
# print(f"Ответ: {result['answer']}")
#
from transformers import pipeline

with open('ilon.txt', 'r', encoding='utf-8') as file:
    ilon_context = file.read()

question = 'Как дела?'
context = ilon_context

model_pipeline = pipeline(
   task='question-answering',
   model='milyausha2801/rubert-russian-qa-sberquad'
)

result = model_pipeline(question=question, context=context)
print(f"Ответ: {result['answer']}")