#Now importing modules
import numpy as np
from keras.preprocessing.text import Tokenizer
from keras.utils import pad_sequences
from keras.models import Model
from keras.layers import GRU, Input, Dense, TimeDistributed, Activation, RepeatVector, Bidirectional
from keras.layers import Embedding
from keras.optimizers import Adam
from keras.losses import sparse_categorical_crossentropy
import tensorflow as tf
import os, sys
from datetime import datetime

target='en-vi'
input_path='./data/{}.txt'.format(target[:2])
output_path='./data/{}.txt'.format(target[-2:])

# check if gpu avaliable
if len(tf.config.list_physical_devices('GPU')) == 0:
    print("test is only applicable on GPU")
    exit(0)

def load_data(path):
    input_file = os.path.join(path)
    with open(input_file, "r") as f:
        data = f.read()

    return data.split('\n')

# input:
#       x: a list of sentences
# output:
#       tokenizer.texts_to_sequences(x): a list of sentences of word's id
#       tokenizer: a list of word's id and statistic of it
def tokenize(x):
    tokenizer = Tokenizer(filters="", lower=False)
    tokenizer.fit_on_texts(x)
    return tokenizer.texts_to_sequences(x), tokenizer

# return a list of same length elements
def pad(x, length=None):
    return pad_sequences(x, maxlen=length, padding='post')

def preprocess(x, y):
    """
    Preprocess x and y
    :param x: Feature List of sentences
    :param y: Label List of sentences
    :return: Tuple of (Preprocessed x, Preprocessed y, x tokenizer, y tokenizer)
    """
    preprocess_x, x_tk = tokenize(x)
    preprocess_y, y_tk = tokenize(y)

    preprocess_x = pad(preprocess_x)
    preprocess_y = pad(preprocess_y)

    # Keras's sparse_categorical_crossentropy function requires the labels to be in 3 dimensions
    #Expanding dimensions
    preprocess_y = preprocess_y.reshape(*preprocess_y.shape, 1)

    return preprocess_x, preprocess_y, x_tk, y_tk

def logits_to_text(logits, tokenizer):
    index_to_words = {id: word for word, id in tokenizer.word_index.items()}
    index_to_words[0] = '<PAD>'

  #So basically we are predicting output for a given word and then selecting best answer
  #Then selecting that label we reverse-enumerate the word from id
    return ' '.join([index_to_words[prediction] for prediction in np.argmax(logits, 1)])

def embed_model(input_shape, output_sequence_length, input_vocab_size, output_vocab_size):
    """
    Build and train a RNN model using word embedding on x and y
    :param input_shape: Tuple of input shape
    :param output_sequence_length: Length of output sequence
    :param input_vocab_size: Number of unique input words in the dataset
    :param output_vocab_size: Number of unique output words in the dataset
    :return: Keras model built, but not trained
    """
    #Config Hyperparameters
    learning_rate = 0.005
    latent_dim = 128
    
    #Config Model
    inputs = Input(shape=input_shape[1:])
    embedding_layer = Embedding(input_dim=input_vocab_size,
                                output_dim=output_sequence_length,
                                mask_zero=False)(inputs)
    bd_layer = Bidirectional(GRU(output_sequence_length))(embedding_layer)
    encoding_layer = Dense(latent_dim, activation='relu')(bd_layer)
    decoding_layer = RepeatVector(output_sequence_length)(encoding_layer)
    output_layer = Bidirectional(GRU(latent_dim, return_sequences=True))(decoding_layer)
    outputs = TimeDistributed(Dense(output_vocab_size, activation='softmax'))(output_layer)
    
    #Create Model from parameters defined above
    model = Model(inputs=inputs, outputs=outputs)
    model.compile(loss=sparse_categorical_crossentropy,
                  optimizer=Adam(learning_rate),
                  metrics=['accuracy'])
    
    return model

#Now loading data
input_sentences=load_data(input_path)
output_sentences=load_data(output_path)

preproc_input_sentences, preproc_output_sentences, input_tokenizer, output_tokenizer =\
    preprocess(input_sentences, output_sentences)

max_input_sequence_length = preproc_input_sentences.shape[1]
max_output_sequence_length = preproc_output_sentences.shape[1]
input_vocab_size = len(input_tokenizer.word_index)
output_vocab_size = len(output_tokenizer.word_index)

print('Data Preprocessed')
print("Max input sentence length:", max_input_sequence_length)
print("Max output sentence length:", max_output_sequence_length)
print("input vocabulary size:", input_vocab_size)
print("output vocabulary size:", output_vocab_size)
    
# Reshaping the input to work with a basic RNN
tmp_x = pad(preproc_input_sentences, preproc_output_sentences.shape[1])
tmp_x = tmp_x.reshape((-1, preproc_output_sentences.shape[-2]))

model_path = './models/{}.keras'.format(target)
try:
    simple_rnn_model = tf.keras.saving.load_model(model_path)
    print("model loaded")
except:
    print("loading model failed")
simple_rnn_model = embed_model(
    tmp_x.shape,
    preproc_output_sentences.shape[1],
    len(input_tokenizer.word_index)+1,
    len(output_tokenizer.word_index)+1)

try:
    simple_rnn_model.summary()

    history=simple_rnn_model.fit(tmp_x, preproc_output_sentences, batch_size=256, epochs=56, validation_split=0.2)
    simple_rnn_model.save(model_path)

    np.savetxt('./logs/{}.txt'.format(datetime.now().strftime("%d.%m.%Y %H-%M-%S")), np.array(history.history['accuracy']), delimiter=",")
except ValueError:
    os.remove('./models/{}.keras'.format(target))
    os.execv(sys.executable, [os.path.basename(sys.executable)] + sys.argv)
except Exception as e: print(e)