import yaml, tensorflow_model_optimization as tfmot, numpy as np, tensorflow as tf, re, pickle
from keras.utils import pad_sequences
from v2enlib import language_model, cleanScreen

with open("config.yml", "r") as f:
    cfg = yaml.safe_load(f)
target = cfg["v2en"]["target"]
val_cache_path = cfg["training"]["val_cache_path"]
model_shape_path = cfg["training"]["model_shape_path"]
checkpoint_path = cfg["training"]["checkpoint_path"]

try:
    with open(model_shape_path, "rb") as f:
        (
            tmp_x_shape,
            second_preproc_sentences_shape,
            first_tokenizer_len,
            second_tokenizer_len,
        ) = pickle.load(f)
    rnn_model = language_model(
        tmp_x_shape,
        second_preproc_sentences_shape,
        first_tokenizer_len,
        second_tokenizer_len,
    )
    rnn_model.load_weights(checkpoint_path)
    print("model loaded")
    with open(val_cache_path, "rb") as f:
        output_tokenizer, input_tokenizer, preproc_output_sentences = pickle.load(f)
except Exception as e:
    print("loading model failed")
    print(e)
    exit(0)


def logits_to_text(logits, tokenizer):
    index_to_words = {id: word for word, id in tokenizer.word_index.items()}
    index_to_words[0] = ""

    # So basically we are predicting output for a given word and then selecting best answer
    # Then selecting that label we reverse-enumerate the word from id
    return " ".join([index_to_words[prediction] for prediction in np.argmax(logits, 1)])


def final_predictions(text):
    y_id_to_word = {value: key for key, value in output_tokenizer.word_index.items()}
    y_id_to_word[0] = "<PAD>"

    sentence = [input_tokenizer.word_index[word] for word in text.split()]
    sentence = pad_sequences(
        [sentence], maxlen=preproc_output_sentences.shape[-2], padding="post"
    )

    print(logits_to_text(rnn_model.predict(sentence[:1])[0], output_tokenizer))


cleanScreen()
txt = input(">> ")
final_predictions(re.sub(r"[^\w]", " ", txt))
