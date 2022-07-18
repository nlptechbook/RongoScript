
#parameters needed to find the file containing training data
filepath = '/path/to/your/jsonfile/'
sample_file = 'faq_en.json' 

### transformer parameters

#parameters needed for vectorization
vocab_size = 100
sequence_length = 10 
batch_size = 32

#parameters to configure the end-to-end model
embed_dim = 128 # Embedding size for each token
num_heads = 8  # Number of attention heads
ff_dim = 128  # Hidden layer size in feed forward network inside transformer

#confidence threshold parameter

confidence_threshold = 0.9 

#number of maximum allowed classes in the model 

num_classes = 100
