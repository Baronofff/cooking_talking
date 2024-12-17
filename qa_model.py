from transformers import pipeline

model_pipeline = pipeline(
   task='question-answering',
   model='milyausha2801/rubert-russian-qa-sberquad'
)
