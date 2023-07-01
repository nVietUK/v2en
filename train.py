import numpy as np, tensorflow_model_optimization as tfmot
import tensorflow as tf, pickle, yaml, os
from datetime import datetime
from v2enlib import utils, ai, SQL

try:
    with open("config.yml", "r") as f:
        cfg = yaml.safe_load(f)
    table_name = cfg["sqlite"]["table_name"]
    conn = SQL.getSQLCursor(cfg["sqlite"]["path"])
    cfg = cfg["training"]
    val_cache_path = cfg["val_cache_path"]
    model_shape_path = cfg["model_shape_path"]
    os.makedirs("models", exist_ok=True)
    checkpoint_path = cfg["checkpoint_path"]
    learning_rate = cfg["learning_rate"]
    allow_pruning = cfg["allow_pruning"]
except Exception as e:
    utils.printError("importing config", e, True)
    exit()
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
for e in SQL.getSQL(conn, f"SELECT * FROM {table_name}"):
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

rnn_model = ai.language_model(
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
    monitor='val_accuracy',
    mode='max'
)
earlystop_accuracy = tf.keras.callbacks.EarlyStopping(
    monitor="val_accuracy", patience=10, verbose=1, mode="max"
)
earlystop_loss = tf.keras.callbacks.EarlyStopping(
    monitor="val_loss", patience=10, verbose=1, mode="min"
)
update_pruning = tfmot.sparsity.keras.UpdatePruningStep()
callbacks = [
    checkpoint,
    earlystop_accuracy,
    earlystop_loss,
    tf.keras.callbacks.TensorBoard(log_dir="./logs"),
    tf.keras.callbacks.LearningRateScheduler(ai.lr_schedule)
]
if allow_pruning:
    callbacks += [update_pruning]

batch_size = 450
try:
    if in_develop:
        exit(0)
    utils.cleanScreen()
    rnn_model.summary()

    history = rnn_model.fit(
        tmp_x,
        second_preproc_sentences,
        batch_size=batch_size,
        epochs=50,
        validation_split=0.2,
        callbacks=callbacks,
        use_multiprocessing=True
    )
    os.makedirs("logs", exist_ok=True)
    np.savetxt(
        f"./logs/{datetime.now().strftime('%d.%m.%Y %H-%M-%S')}.txt",
        np.array(history.history["accuracy"]),
        delimiter=",",
    )
except Exception as e:
    print(e)
    exit(0)

os.makedirs("cache", exist_ok=True)
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
