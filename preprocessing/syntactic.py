# extracting postions in the syntactic tree
import numpy as np
import spacy
nlp = spacy.load('en_core_web_sm')

def syntactic(x_train):
  x_dep = []
  x_dep_flat = []
  for utterance in x_train:
    doc = nlp(utterance)
    sentences = list(doc.sents)
    q = np.full(20, 0)
    v = np.full(20, 0)
    maxlevel = 0
    i = 0
    for sent in sentences:
      maxsentlevel = 0
      for token in sent:
        head = token
        level = 0
        while head != sent.root:
          head = head.head
          level = level + 1
          if maxsentlevel < level:
            maxsentlevel = level
        if token.dep_ != 'punct':
          q[i] = level + maxlevel
          v[i] = level
          i=i+1
          print(token,level)
      #print(maxsentlevel)
      maxlevel = maxsentlevel + 1 + maxlevel
    x_dep.append(q) 
    x_dep_flat.append(v)
  return np.asarray(x_dep)
  
  # test
  # syntactic(['I want a greek pizza. I want it.'])
