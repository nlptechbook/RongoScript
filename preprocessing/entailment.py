# extracting the compliment clause from the sentence that comes first from the end in the passage, 
# in which a compliment clause will be found. Also returns the predicate and whether it is under negation.
# for better understanding of why you might need this, refer to https://metatext.io/datasets/commitmentbank
#
# here, you call cb_entailment(), which calls ccomp_extraction() internally.
import spacy
nlp = spacy.load('en_core_web_sm')

def cb_entailment(passage):
  doc = nlp(passage)
  for sent in reversed(list(doc.sents)):
    for token in sent:
      if token.dep_ == 'ccomp':
        ccomp, verb, negation = ccomp_extraction(sent.text)
        return ccomp, verb, negation
  return

def ccomp_extraction(sent):
  doc = nlp(sent)
  root = [token for token in doc if token.head == token][0]
  ccomp = [token for token in doc if token.dep_ == 'ccomp'][0]
  neg = 'no_negation'
  if [token for token in root.lefts if token.dep_ == 'neg']:
    neg = 'negation'
  ccomp_span = doc[ccomp.left_edge.i: ccomp.right_edge.i + 1]
  if ccomp.left_edge.dep_ in ['mark']:
    ccomp_span = ccomp_span[1:]
  return ccomp_span.text, root.lemma_, neg
