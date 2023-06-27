import numpy as np
import tensorflow as tf, pickle, yaml, os
from datetime import datetime
from v2enlib import getSQLCursor, getSQL, cleanScreen, language_model
import tensorflow_model_optimization as tfmot

with open("config.yml", "r") as f:
    cfg = yaml.safe_load(f)
table_name = cfg["sqlite"]["table_name"]
conn = getSQLCursor(cfg["sqlite"]["path"])
cfg = cfg["training"]
val_cache_path = cfg["val_cache_path"]
model_shape_path = cfg["model_shape_path"]
checkpoint_path = cfg["checkpoint_path"]
learning_rate = cfg["learning_rate"]
in_develop = False


# check if gpu avaliable
gpus = tf.config.list_physical_devices("GPU")
if len(gpus) == 0:
    print("test is only applicable on GPU")
    exit(0)
else:
    try:
        # Currently, memory growth needs to be the same across GPUs
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
            tf.config.set_logical_device_configuration(
                gpu, [tf.config.LogicalDeviceConfiguration(memory_limit=4096)]
            )
        logical_gpus = tf.config.list_logical_devices("GPU")
        print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
    except RuntimeError as e:
        # Memory growth must be set before GPUs have been initialized
        print(e)
os.environ["TF_GPU_ALLOCATOR"] = "cuda_malloc_async"


def tokenize(x):
    tokenizer = tf.keras.preprocessing.text.Tokenizer(filters="", lower=False)
    tokenizer.fit_on_texts(x)
    return tokenizer.texts_to_sequences(x), tokenizer


def pad(x, length=None):
    return tf.keras.utils.pad_sequences(x, maxlen=length, padding="post")


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

rnn_model = language_model(
    tmp_x.shape,
    second_preproc_sentences.shape[1],
    len(first_tokenizer.word_index) + 1,
    len(second_tokenizer.word_index) + 1,
)

# Prunning model feature
checkpoint = tf.keras.callbacks.ModelCheckpoint(
    checkpoint_path,
    save_best_only=True,
    save_weights_only=True,
    verbose=1,
    monitor="val_loss",
    mode="min",
)
earlystop_accuracy = tf.keras.callbacks.EarlyStopping(
    monitor="val_accuracy", patience=5, verbose=1, mode="max"
)
earlystop_loss = tf.keras.callbacks.EarlyStopping(
    monitor="val_loss", patience=5, verbose=1, mode="min"
)
reducelr = tf.keras.callbacks.ReduceLROnPlateau(
    monitor="val_loss", factor=0.2, patience=2, min_lr=learning_rate / 1000, verbose=1
)
update_pruning = tfmot.sparsity.keras.UpdatePruningStep()
callbacks = [
    update_pruning,
    checkpoint,
    earlystop_accuracy,
    earlystop_loss,
    reducelr,
]

try:
    if in_develop:
        exit(0)
    cleanScreen()
    rnn_model.summary()

    history = rnn_model.fit(
        tmp_x,
        second_preproc_sentences,
        batch_size=512,
        epochs=50,
        validation_split=0.2,
        callbacks=callbacks,
    )

    np.savetxt(
        f"./logs/{datetime.now().strftime('%d.%m.%Y %H-%M-%S')}.txt",
        np.array(history.history["accuracy"]),
        delimiter=",",
    )
except Exception as e:
    print(e)
    exit(0)

with open(val_cache_path, "wb") as f:
    pickle.dump([second_tokenizer, first_tokenizer, second_preproc_sentences], f)
with open(model_shape_path, "wb") as f:
    pickle.dump(
        [
            tmp_x.shape,
            second_preproc_sentences.shape[1],
            len(first_tokenizer.word_index) + 1,
            len(second_tokenizer.word_index) + 1,
        ],
        f,
    )
