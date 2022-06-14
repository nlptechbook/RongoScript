# lemmatization
import spacy
nlp = spacy.load('en_core_web_sm')

def lemmatization(utterance):
  doc = nlp(utterance)
  return  " ".join([token.lemma_ for token in doc if token.dep_ != 'punct'])
