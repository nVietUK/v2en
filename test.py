import re, os, pickle
import tensorflow as tf
import numpy as np
from dotenv import load_dotenv

load_dotenv()

target=os.getenv("TARGET")
val_cache_path=os.getenv("VAL_CACHE_PATH")

model_path = './models/{}.keras'.format(target)
try:
    rnn_model = tf.keras.saving.load_model(model_path)
    print("model loaded")
    with open(val_cache_path, 'rb') as f:
        output_tokenizer, input_tokenizer, pad_sequences,\
        preproc_output_sentences = pickle.load(f)
except Exception as e:
    print("loading model failed"); print(e); exit(0)

def logits_to_text(logits, tokenizer):
    index_to_words = {id: word for word, id in tokenizer.word_index.items()}
    index_to_words[0] = '<PAD>'

  #So basically we are predicting output for a given word and then selecting best answer
  #Then selecting that label we reverse-enumerate the word from id
    return ' '.join([index_to_words[prediction] for prediction in np.argmax(logits, 1)])

def final_predictions(text):
    y_id_to_word = {value: key for key, value in output_tokenizer.word_index.items()}
    y_id_to_word[0] = '<PAD>'

    sentence = [input_tokenizer.word_index[word] for word in text.split()]
    sentence = pad_sequences([sentence], maxlen=preproc_output_sentences.shape[-2], padding='post')
    
    print(sentence.shape)
    print(logits_to_text(rnn_model.predict(sentence[:1])[0], output_tokenizer))

txt=input()
final_predictions(re.sub(r'[^\w]', ' ', txt))