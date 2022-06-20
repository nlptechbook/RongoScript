

# NER processing
import spacy
nlp = spacy.load('ru_core_news_sm')

def ner_replacement(utterance):
  doc = nlp(utterance)
  result = doc.text
  for entity in doc.ents:
    result = result.replace(entity.text, entity.label_)
  return result

def ner_extraction(utterance):
  doc = nlp(utterance)
  ner_dict = {}
  for entity in doc.ents:
    x = ner_dict.setdefault(entity.label_, entity.text)
  return ner_dict
