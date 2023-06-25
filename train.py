# Now importing modules
import numpy as np
from keras.preprocessing.text import Tokenizer
from keras.utils import pad_sequences
from keras.models import Model
from keras.layers import (
    GRU,
    Input,
    Dense,
    TimeDistributed,
    RepeatVector,
    Bidirectional,
    Embedding,
)
from keras.optimizers import Adam
import tensorflow as tf
import pickle
from datetime import datetime
import yaml
from v2enlib import *
import tensorflow_model_optimization as tfmot
from tensorflow_model_optimization.sparsity.keras import (
    UpdatePruningStep,
    strip_pruning,
    prune_low_magnitude,
    PolynomialDecay,
)
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau

with open("config.yml", "r") as f:
    cfg = yaml.safe_load(f)
target = cfg["v2en"]["target"]
model_path = "./models/model.keras"
best_model_path = "./models/best.keras"
initial_sparsity = 0.50
final_sparsity = 0.90
begin_step = 1000
end_step = 5000
in_develop = False
pruning_schedule = tfmot.sparsity.keras.PolynomialDecay(
    initial_sparsity=initial_sparsity,
    final_sparsity=final_sparsity,
    begin_step=begin_step,
    end_step=end_step,
    power=5,
    frequency=100,
)

# check if gpu avaliable
if len(tf.config.list_physical_devices("GPU")) == 0:
    print("test is only applicable on GPU")
    exit(0)


def tokenize(x):
    tokenizer = Tokenizer(filters="", lower=False)
    tokenizer.fit_on_texts(x)
    return tokenizer.texts_to_sequences(x), tokenizer


def pad(x, length=None):
    return pad_sequences(x, maxlen=length, padding="post")


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

    preprocess_y = preprocess_y.reshape(*preprocess_y.shape, 1)

    return preprocess_x, preprocess_y, x_tk, y_tk


def embed_model(
    input_shape, output_sequence_length, input_vocab_size, output_vocab_size
):
    """
    Build and train a RNN model using word embedding on x and y
    :param input_shape: Tuple of input shape
    :param output_sequence_length: Length of output sequence
    :param input_vocab_size: Number of unique input words in the dataset
    :param output_vocab_size: Number of unique output words in the dataset
    :return: Keras model built, but not trained
    """
    # Config Hyperparameters
    learning_rate = 0.001
    latent_dim = 128

    # Config Model
    inputs = Input(shape=input_shape[1:])
    embedding_layer = Embedding(
        input_dim=input_vocab_size, output_dim=output_sequence_length, mask_zero=False
    )(inputs)
    bd_layer = Bidirectional(GRU(output_sequence_length))(embedding_layer)
    encoding_layer = prune_low_magnitude(
        Dense(latent_dim, activation="relu"), pruning_schedule=pruning_schedule
    )(bd_layer)
    decoding_layer = RepeatVector(output_sequence_length)(encoding_layer)
    output_layer = Bidirectional(GRU(latent_dim, return_sequences=True))(decoding_layer)
    outputs = TimeDistributed(
        prune_low_magnitude(
            Dense(output_vocab_size, activation="softmax"),
            pruning_schedule=pruning_schedule,
        )
    )(output_layer)

    model = Model(inputs=inputs, outputs=outputs)
    model.compile(
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        optimizer=Adam(learning_rate),
        metrics=["accuracy"],
    )

    return model


# Now loading data
conn = getSQLCursor(cfg["sqlite"]["path"])
table_name = cfg["sqlite"]["table_name"]

first_sent, second_sent = [], []
for e in getSQL(conn, f"SELECT * FROM {table_name}"):
    if e[2]:
        first_sent.append(e[0])
        second_sent.append(e[1])

(
    first_preproc_sentences,
    second_preproc_sentences,
    first_tokenizer,
    second_tokenizer,
) = preprocess(first_sent, second_sent)

# Reshaping the input to work with a basic RNN
tmp_x = pad(first_preproc_sentences, second_preproc_sentences.shape[1])
tmp_x = tmp_x.reshape((-1, second_preproc_sentences.shape[-2]))

rnn_model = embed_model(
    tmp_x.shape,
    second_preproc_sentences.shape[1],
    len(first_tokenizer.word_index) + 1,
    len(second_tokenizer.word_index) + 1,
)

# Prunning model feature
checkpoint = ModelCheckpoint(
    best_model_path, save_best_only=True, save_weights_only=True, verbose=1
)
earlystop = EarlyStopping(monitor="val_loss", patience=5, verbose=1)
reducelr = ReduceLROnPlateau(
    monitor="val_loss", factor=0.2, patience=2, min_lr=0.0001, verbose=1
)
callbacks = [UpdatePruningStep(), checkpoint, earlystop, reducelr]

try:
    if in_develop:
        exit(0)
    cleanScreen()
    rnn_model.summary()

    history = rnn_model.fit(
        tmp_x,
        second_preproc_sentences,
        batch_size=4096,
        epochs=20,
        validation_split=0.2,
        callbacks=callbacks,
        verbose=1,
    )
    rnn_model = strip_pruning(rnn_model.load_weights(best_model_path))
    rnn_model.save(model_path)

    np.savetxt(
        f"./logs/{datetime.now().strftime('%d.%m.%Y %H-%M-%S')}.txt",
        np.array(history.history["accuracy"]),
        delimiter=",",
    )
except Exception as e:
    print(e)
    exit(0)

val_cache_path = "./cache/var.pkl"
with open(val_cache_path, "wb") as f:
    pickle.dump([second_tokenizer, first_tokenizer, second_preproc_sentences], f)
