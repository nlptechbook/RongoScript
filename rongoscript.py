# building the model to work with
from configs import *

import json
import os.path

from complements import ner_extraction
from complements import ner_replacement
from lemmatization import lemmatization
from syntactic import syntactic

import numpy as np
import pathlib
import random
import string
import re
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.layers import TextVectorization 

from transformer import TransformerBlock
from transformer import EmbeddingBlock

from adds import *

class model:
  def __init__(self, training_data, lang = 'en'):
    self.error = None
    try:
      f = open(training_data, encoding='utf-8')
      # returns JSON as a dictionary
      data = json.load(f)
    except Exception as exp:
      self.error = str('File reading error: ' + str(exp))
      return
    train_pairs = []
    responses = []
    classes = []
    try:
      for i in data['samples']:
        train_pairs = train_pairs + [(i["class"], utterance, i["ner"]) for utterance in i["utterance"]]
        responses = responses + [(i["class"], response) for response in i["response"]]
        classes.append((i["class"], i["action"], i["ner"]))
    except Exception as exp:
      self.error = str('Wrong structure: ' + str(exp))
      return
    if len(classes) > num_classes:
      self.error = str('Too many classes in your data. This demo allows not more than ' + str(num_classes))
      return
    #perform the ner replacement in train pairs where necessary
    train_pairs = [(pair[0], ner_replacement(pair[1])) if pair[2] else (pair[0], pair[1]) for pair in train_pairs] 
    #splitting the training data into X and Y
    x_train = [lemmatization(pair[1]) for pair in train_pairs]
    y_train = [pair[0] for pair in train_pairs]
    # getting the vector of token postions in the syntactic tree of an utterance
    x_syntactic = syntactic([pair[1] for pair in train_pairs])
    x_syntactic = keras.preprocessing.sequence.pad_sequences(x_syntactic, maxlen=sequence_length, truncating ='post')
    #casting Y elements to int
    y_train = list(map(int, y_train))
    #creating the vectorization layer needed to map tokens to integer values
    vectorization = TextVectorization(
      max_tokens=vocab_size, output_mode="int", output_sequence_length=sequence_length,
    )
    #computing a vocabulary of string terms from tokens found in our corpus
    vectorization.adapt(x_train)
    #performing vectorization of the sentences found in x_train
    x_train = vectorization(x_train)
    #converting x_train to numpy array
    x_train = x_train.numpy()
    #padding x_train sequences to the same length.
    x_train = keras.preprocessing.sequence.pad_sequences(x_train, maxlen=sequence_length)
    # building the end-to-end model  
    inputs1 = layers.Input(shape=(None, ))
    inputs2 = layers.Input(shape=(None, ))
    embedding_layer = EmbeddingBlock(sequence_length, vocab_size, embed_dim)
    x = embedding_layer([inputs1,inputs2])
    transformer_block = TransformerBlock(embed_dim, num_heads, ff_dim)
    x = transformer_block(x)
    x = layers.GlobalAveragePooling1D()(x)
    x = layers.Dropout(0.1)(x)
    x = layers.Dense(20, activation="relu")(x)
    x = layers.Dropout(0.1)(x)
    outputs = layers.Dense(20, activation="softmax")(x)
    #creating the model
    model = keras.Model(inputs=[inputs1, inputs2], outputs=outputs)
    #converting y_train to numpy array
    y_train = np.asarray(y_train)
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    history = model.fit([x_train, x_syntactic], y_train, batch_size=batch_size, epochs=200)
    #setting the class variables
    self.model = model
    self.vectorization = vectorization
    self.responses = responses
    self.classes = classes

  def get_prediction(self, utterance):
    #input processing with ner
    ner_dict = ner_extraction(utterance)
    utterance_ner = ner_replacement(utterance)
    utterance_ner = lemmatization(utterance_ner)
    # finding the length of the utterance's ner replacement to truncate then the vector passed to the model
    mxln = len(utterance_ner.split())
    if mxln > sequence_length:
      mxln = sequence_length 
    if mxln < 2:
      mxln = 2   
    # vectorization of the utterance
    x_pred_ner = self.vectorization([utterance_ner])
    x_pred_ner = x_pred_ner.numpy()
    # truncating the utterance vector
    x_pred_ner = keras.preprocessing.sequence.pad_sequences(x_pred_ner, maxlen=mxln, truncating ='post')
    # calculating the vector of the token levels in the syntactic tree
    syntactic_pos = syntactic([utterance_ner])
    pos = keras.preprocessing.sequence.pad_sequences(syntactic_pos, maxlen=mxln, truncating ='post')
    # making a prediction
    predictions = self.model.predict([x_pred_ner, pos])
    predictions = predictions[0, :]
    # Getting indices of N = 2 maximum values
    v = np.argsort(predictions)[::-1][:2]
    confidence_ner = (self.classes[v[0]][0], predictions[v[0]], predictions[v[1]])
    #regular input processing
    utterance = lemmatization(utterance)
    # finding the length of the utterance to truncate then the vector passed to the model
    mxln = len(utterance.split())
    if mxln > sequence_length:
      mxln = sequence_length  
    if mxln < 2:
      mxln = 2  
    #making vectorazion
    x_pred = self.vectorization([utterance])
    x_pred = x_pred.numpy()
    x_pred = keras.preprocessing.sequence.pad_sequences(x_pred, maxlen=mxln, truncating ='post')
    if np.all(x_pred == 1):
      return str("I don't understand!")
    # calculating the vector of the token levels in the syntactic tree
    syntactic_pos = syntactic([utterance])
    pos = keras.preprocessing.sequence.pad_sequences(syntactic_pos, maxlen=mxln, truncating ='post')
    #making a prediction
    predictions = self.model.predict([x_pred, pos])
    predictions = predictions[0, :]
    # Getting indices of N = 2 maximum values
    v = np.argsort(predictions)[::-1][:2]
    confidence = (self.classes[v[0]][0], predictions[v[0]], predictions[v[1]])
    if ((confidence[1] + confidence[2])< confidence_threshold) and ((confidence_ner[1]+confidence_ner[2]) < confidence_threshold):
      return str('An appropriate answer not found, within the specified confidence threshold of the neural network.')
    from operator import itemgetter
    predicted_class = max([confidence_ner, confidence], key=itemgetter(1))[0]
    answer = ''
    if self.classes[predicted_class][1]:
      try:
        if self.classes[predicted_class][2]:
          answer = globals()[str(self.classes[predicted_class][1])](ner_dict)
        else:
          answer = globals()[str(self.classes[predicted_class][1])]()
      except Exception as exp:
        answer = 'No such function on the server: ' + str(exp)
    else: 
      answer = random.choice([response for response in self.responses if response[0] == predicted_class])[1]
    return str(answer)
