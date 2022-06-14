#NER processing
import spacy
nlp = spacy.load('en_core_web_sm')
nlp.add_pipe('merge_noun_chunks')

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
