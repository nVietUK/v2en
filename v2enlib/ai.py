import tensorflow as tf, const

def language_model(
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
    latent_dim = 128
    layers = tf.keras.layers

    # Build the layers
    model = tf.keras.models.Sequential()
    # Embedding
    model.add(
        layers.Embedding(
            input_vocab_size,
            latent_dim,
            input_length=input_shape[1],
            input_shape=input_shape[1:],
        )
    )
    # Encoder
    model.add(layers.Bidirectional(layers.GRU(latent_dim)))
    model.add(layers.RepeatVector(output_sequence_length))
    # Decoder
    model.add(layers.Bidirectional(layers.GRU(latent_dim, return_sequences=True)))
    model.add(layers.TimeDistributed(layers.Dense(latent_dim * 4, activation="relu")))
    model.add(layers.Dropout(0.5))
    model.add(
        layers.TimeDistributed(layers.Dense(output_vocab_size, activation="softmax"))
    )

    model.compile(
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        optimizer=tf.keras.optimizers.Adam(learning_rate=const.learning_rate * 5),
        metrics=["accuracy"],
    )

    return model
