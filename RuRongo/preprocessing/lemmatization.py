# lemmatization
import spacy
nlp = spacy.load('ru_core_news_sm')

def lemmatization(utterance):
  doc = nlp(utterance)
  return  " ".join([token.lemma_ for token in doc if token.dep_ != 'punct'])
