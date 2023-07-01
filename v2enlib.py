import contextlib, tensorflow as tf, tensorflow_model_optimization as tfmot
import os, string, httpx, sqlite3, resource, time, yaml, logging, librosa, string, gc
import deep_translator.exceptions, langcodes, requests, traceback, platform, numpy as np
import hashlib, subprocess, soundfile as sf, scipy
from difflib import SequenceMatcher
from multiprocess.pool import ThreadPool
from multiprocess.context import TimeoutError as TLE
from tabulate import tabulate
from tqdm import tqdm
from translators import server as TransServer
from functools import lru_cache


# debug def
def printError(text, error, important):
    text = f"{'_'*50}\n\tExpectation while {text}\n\tError type: {type(error)}\n\t{error}\n{chr(8254)*50}"
    logging.fatal(text)
    if important:
        print(text)


# pre define
sound_tracks = {
    "macos_startup": [["F#2", "C#3", "F#3", "C#4", "F#4", "A#4"], [5 / 3] * 6, [0] * 6],
    "windows7_shutdown": [
        ["G#4", "E4", "B4", "C5"],
        [0.25, 0.25, 0.25, 0.25],
        [0.0, 0.3, 0.6, 0.9],
    ],
}


# classes
class InputSent:
    def __init__(
        self,
        first: str = "",
        second: str = "",
        isFrom: str = "",
        accurate: float = 0,
    ) -> None:
        self.isFrom = isFrom or "Data set"
        self.first = first or "N/A"
        self.second = second or "N/A"
        self.accurate = accurate
        self.isAdd = accurate > accept_percentage

    def isValid(self) -> bool:
        return bool(self.first and self.second)

    def SQLFormat(self) -> tuple:
        return (self.first, self.second, 1 if self.isAdd else 0)


# executors
def transIntoListExecutor(cmd):
    return transIntoList(*cmd)


def addSentExecutor(cmd):
    return addSent(*cmd)


def checkSpellingExecutor(cmd):
    return checkSpelling(*cmd)


# utils
def differentRatio(x, y):
    return SequenceMatcher(None, x, y).ratio()


def emptyFile(path):
    return os.stat(path).st_size == 0


def convert(x: str) -> str:
    if not x:
        return ""
    # fix bad data
    if "apos" in x or "quot" in x or "amp" in x or "&#91;" in x:
        return ""

    x = x.replace("“", " “ ").replace("”", " ” ").replace("’", " ’ ")
    for punc in string.punctuation:
        x = x.replace(punc, f" {punc} ")
    try:
        return x.lower().replace("  ", " ").replace("  ", " ")
    except Exception as e:
        printError(convert.__name__, e, False)
        return ""


@lru_cache(maxsize=1024)
def getWikitionaryHeaders(word: str) -> httpx.Response:
    return httpx.get(f"https://en.wiktionary.org/wiki/{word}")


def existOnWiki(word: str, lang: str) -> bool:
    display_name = langcodes.Language.make(language=lang).display_name()

    response = getWikitionaryHeaders(word)
    return (
        f'href="#{display_name}"' in response.headers.get("link", "")
        or f'id="{display_name}"' in response.text
    )


def cleanScreen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def getKeyByValue(d, value):
    return [k for k, v in d.items() if v == value]


def playNote(note, duration, volume, note_duration, start_time):
    """
    Plays a single note with the given duration and volume using the soundfile library.
    """
    sr = 44100  # sample rate
    freq = librosa.note_to_hz(note)
    samples = scipy.signal.sawtooth(  # type: ignore
        2 * np.pi * np.arange(sr * note_duration) * freq / sr, 0.5
    )
    decay = np.linspace(volume, 0, int(sr * note_duration))
    scaled = samples * decay
    scaled /= np.max(np.abs(scaled))

    # Compute hash of audio data
    hashname = hashlib.sha256(scaled).hexdigest()

    # Create subdirectory for stored audio files
    os.makedirs(".wav", exist_ok=True)

    # Check if file with the same hash already exists
    filename = os.path.join(".wav", f"{hashname[:10]}.wav")
    if not os.path.exists(filename):
        # Write scaled audio data to file
        sf.write(filename, scaled, sr)

    time.sleep(start_time)

    # Play audio file using appropriate command depending on platform
    if platform.system() == "Windows":
        subprocess.Popen(
            [
                "powershell",
                'New-Object Media.SoundPlayer "{filename}"'.format(filename=filename),
            ]
        )
    elif platform.system() == "Darwin":
        subprocess.Popen(["afplay", filename])
    else:
        subprocess.Popen(["play", "-q", filename])


def playNotes(notes, durations, note_start_times):
    """
    Plays multiple notes simultaneously with varying durations and decreasing volume using a thread pool.
    """
    pool = ThreadPool(len(notes))
    for i in range(len(notes)):
        pool.apply_async(
            playNote,
            (
                notes[i],
                durations[i],
                1 - (i / len(notes)),
                durations[i],
                note_start_times[i],
            ),
        )
    pool.close()
    pool.join()


def checkLangFile(*args):
    for target in args:
        if os.path.exists(f"./cache/{target}.dic"):
            continue
        open(f"./cache/{target}.dic", "w").close()


def loadDictionary(path) -> list:
    try:
        if not emptyFile(path):
            with open(path, "r") as f:
                return [word.rstrip("\n") for word in f.read().splitlines(True)]
    except Exception as e:
        printError(loadDictionary.__name__, e, False)
    return []


def saveDictionary(path, dictionary):
    try:
        with open(path, "w") as f:
            for e in dictionary:
                f.write(e + "\n")
    except Exception as e:
        printError("saveDictionary", e, False)


def functionTimeoutWrapper(s):
    def outer(fn):
        def inner(*args, **kwargs):
            with ThreadPool(processes=1) as pool:
                result = pool.apply_async(fn, args=args, kwds=kwargs)
                output = kwargs.get("default_value", None)
                with contextlib.suppress(TLE):
                    output = result.get(timeout=s) if s else result.get()
                return output

        return inner

    return outer


def functionTimeout(timeout, func, **kwargs):
    @functionTimeoutWrapper(timeout)
    def execute(func, **kwargs):
        args, kwargs = kwargs.get("args", None), kwargs.get("kwargs", None)
        return (
            func(*args, **kwargs)
            if args and kwargs
            else func(**kwargs)
            if kwargs
            else func(*args)
        )

    return execute(func, **kwargs)


def measureFunction(func):
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        execution_time = end_time - start_time
        before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        resource_consumption = before / 1024 / 1024  # Memory usage in MB
        if execution_time < time_allow and resource_consumption < resource_allow:
            return result

        logging.warn(
            f"{func.__name__}'s result:\n\tExecution time: {execution_time} seconds\n\tMemory consumption: {resource_consumption} MB"
        )
        return result

    return wrapper


def terminalWidth():
    return os.get_terminal_size().columns


# thread utils
def functionPool(
    func, cmds, executor, isAllowThread=True, strictOrder=False, poolName: str = ""
) -> list:
    if (len(cmds)) == 0:
        return []
    with executor(
        processes=min(len(cmds), thread_limit if thread_limit > 0 else len(cmds)),
    ) as ex:
        if not thread_alow or not isAllowThread:
            return [func(cmd) for cmd in tqdm(cmds, leave=False, desc=poolName)]
        with tqdm(total=len(cmds), leave=False, desc=poolName) as pbar:
            results = []
            for res in (
                ex.imap(func, cmds) if strictOrder else ex.imap_unordered(func, cmds)
            ):
                pbar.update(1)
                results.append(res)
            return results


def argsPool(
    funcs: list,
    executor,
    subexecutor,
    isAllowThread: bool = True,
    strictOrder: bool = False,
    poolName: str = "",
    **kwargs,
) -> list:
    with executor(
        processes=min(len(funcs), thread_limit if thread_limit > 0 else len(funcs)),
    ) as ex:
        if not thread_alow or not isAllowThread:
            return [
                subexecutor([func, kwargs])
                for func in tqdm(funcs, leave=False, desc=poolName)
            ]
        with tqdm(total=len(funcs), leave=False, desc=poolName) as pbar:
            results = []
            kwargsc = [dict(kwargs) for _ in range(len(funcs))]
            for res in (
                ex.imap(
                    subexecutor,
                    [[func, kwargsc[i]] for i, func in enumerate(funcs)],
                )
                if strictOrder
                else ex.imap_unordered(
                    subexecutor,
                    [[func, kwargsc[i]] for i, func in enumerate(funcs)],
                )
            ):
                pbar.update(1)
                results.append(res)
            return results


# translate def
def deepTransGoogle(query_text: str, from_language: str, to_language: str) -> str:
    try:
        return deep_translator.GoogleTranslator(
            source=from_language, target=to_language
        ).translate(query_text)
    except (
        deep_translator.exceptions.LanguageNotSupportedException,
        deep_translator.exceptions.InvalidSourceOrTargetLanguage,
    ):
        return deepTransGoogle(
            query_text,
            str(langcodes.Language.get(from_language)),
            str(langcodes.Language.get(to_language)),
        )
    except Exception as e:
        printError(deepTransGoogle.__name__, e, False)
        return ""


@measureFunction
def translatorsTransSub(cmd: list):
    function_timeout = cmd[1].get("function_timeout", None)
    trans_name = getKeyByValue(trans_dict, cmd[0])[0]

    def execute(cmd: list):
        ou = ""
        allow_error = (
            requests.exceptions.JSONDecodeError,
            TransServer.TranslatorError,
            requests.exceptions.HTTPError,
        )
        if function_timeout:
            del cmd[1]["function_timeout"]
        if cmd[0]:
            try:
                ou = functionTimeout(function_timeout, cmd[0], kwargs=cmd[1])
            except TransServer.TranslatorError as e:
                with contextlib.suppress(*allow_error):
                    if tcmd := _extracted_from_translatorsTrans_13(cmd[1].values(), e):
                        ou = functionTimeout(function_timeout / 2, cmd[0], args=tcmd)
                    else:
                        ou = functionTimeout(
                            function_timeout, deepTransGoogle, kwargs=cmd[1]
                        )
            except allow_error:
                ou = functionTimeout(
                    function_timeout / 2, deepTransGoogle, kwargs=cmd[1]
                )
            except Exception as e:
                printError("translatorsTransSub", e, False)
        if function_timeout:
            cmd[1]["function_timeout"] = function_timeout
        return [ou, trans_name]

    return execute(cmd)


@measureFunction
def translatorsTrans(cmd: list, trans_timeout) -> list:
    return argsPool(
        trans_dict.values(),  # type: ignore
        ThreadPool,
        translatorsTransSub,
        poolName="translationPool",
        query_text=cmd[0],
        from_language=cmd[1],
        to_language=cmd[2],
        function_timeout=trans_timeout,
    )


# TODO Rename this here and in `translatorsTrans`
@measureFunction
def _extracted_from_translatorsTrans_13(cmd: list, e) -> list:
    try:
        if not len(e.args):
            return []
        tcmd, execute = list(cmd), False
        if (e.args[0]).find("vie") != -1:
            tcmd[2 if (e.args[0]).find("to_language") != -1 else 1] = "vie"
            execute = True

        if (e.args[0]).find("vi_VN") != -1:
            tcmd[2 if (e.args[0]).find("to_language") != -1 else 1] = "vi_VN"
            execute = True

        if (e.args[0]).find("vi-VN") != -1:
            tcmd[2 if (e.args[0]).find("to_language") != -1 else 1] = "vi-VN"
            execute = True
        if execute:
            return tcmd
    except Exception as e:
        printError("change format language", e, False)
    return []


@measureFunction
def transIntoList(sent, source_lang, target_lang, target_dictionary):
    return functionPool(
        checkSpellingExecutor,
        [
            [convert(e[0]), target_dictionary, target_lang, e[1]]
            for e in translatorsTrans([sent, source_lang, target_lang], trans_timeout)
        ],
        ThreadPool,
        poolName="transCheckSpelling",
    )


# language utils
def checkSpelling(text: str, dictionary: list, lang: str, tname: str = ""):
    word = ""
    try:
        words = text.split()
        outstr = ""
        for idx, word in enumerate(words):
            if (
                word in dictionary
                or word.isnumeric()
                or word in string.punctuation
                or existOnWiki(word, lang)
                or existOnWiki(f"{words[idx-1]} {word}", lang)
                or (
                    idx + 1 < len(words) and existOnWiki(f"{word} {words[idx+1]}", lang)
                )
            ):
                outstr += f"{word} "
            else:
                raise ValueError(f"{word} not existed")
            if word.isalpha() and word not in dictionary:
                dictionary.insert(0, word)
        return [outstr, tname] if tname else outstr
    except ValueError:
        printError(
            f"add word for {lang}",
            Exception(f"{word} isn't existed on Wikitionary!"),
            False,
        )
    except Exception as e:
        printError(checkSpelling.__name__, e, False)
    return ["", ""] if tname else ""


@measureFunction
def addSent(input_sent: InputSent, first_dictionary, second_dictionary):
    is_agree, first_dump_sent, second_dump_sent, cmds, trans_data, print_data = (
        False,
        "",
        "",
        [],
        [],
        ["Data set", input_sent.first, input_sent.second, "N/A"],
    )
    input_sent.first, input_sent.second = functionPool(
        checkSpellingExecutor,
        [
            [convert(input_sent.first.replace("\n", "")), first_dictionary, first_lang],
            [
                convert(input_sent.second.replace("\n", "")),
                second_dictionary,
                second_lang,
            ],
        ],
        ThreadPool,
        strictOrder=True,
        poolName="sentsCheckSpelling",
    )
    if input_sent.isValid():
        is_error, trans_data = True, []
        for first_tran, second_tran in zip(
            *functionPool(
                transIntoListExecutor,
                [
                    [input_sent.first, first_lang, second_lang, second_dictionary],
                    [input_sent.second, second_lang, first_lang, first_dictionary],
                ],
                ThreadPool,
                strictOrder=True,
                poolName="transIntoList",
            )
        ):
            if first_tran[0]:
                trans_data.append(
                    InputSent(
                        input_sent.first,
                        first_tran[0],
                        first_tran[1],
                        differentRatio(input_sent.second, first_tran[0]),
                    )
                )
            if second_tran[0]:
                trans_data.append(
                    InputSent(
                        second_tran[0],
                        input_sent.second,
                        second_tran[1],
                        differentRatio(input_sent.first, second_tran[0]),
                    )
                )

        if any(e.isAdd for e in trans_data):
            is_agree = True
            is_error = False
        if is_agree and not is_error:
            table_command = """
                INSERT INTO {}(Source, Target, Verify)
                VALUES(?,?,?)
            """
            cmds = [
                [
                    table_command.format(table_name),
                    (input_sent.first, input_sent.second, 1),
                ]
            ] + [
                [
                    table_command.format(table_name),
                    e.SQLFormat(),
                ]
                for e in trans_data
                if e.isAdd
            ]
        if is_error:
            first_dump_sent, second_dump_sent = input_sent.first, input_sent.second

        print_data += [
            [e.isFrom, e.first, e.second, e.accurate] for e in trans_data if e.isAdd
        ]
        width = int(terminalWidth() / 4)
        if len(print_data) < 10:
            logging.info(
                tabulate(
                    tabular_data=print_data,
                    headers=["From", "Source", "Target", "Accuracy?"],
                    tablefmt="fancy_grid",
                    showindex="always",
                    maxcolwidths=[None, None, width, width, 7],
                    floatfmt=(".2f" * 5),
                ),
            )
    del trans_data
    gc.collect()
    return first_dump_sent, second_dump_sent, cmds, is_agree, len(print_data) - 1


# sqlite3 defs
def createSQLtable(connection, table_name):
    sql_create_table = """CREATE TABLE IF NOT EXISTS {} (
                            Source LONGTEXT NOT NULL,
                            Target LONGTEXT NOT NULL,
                            Verify BOOL NOT NULL
                        );""".format(
        table_name
    )
    try:
        connection.cursor().execute(sql_create_table)
        connection.commit()
    except Exception as e:
        printError(createSQLtable.__name__, e, False)


def createOBJ(sql, obj, conn):
    try:
        if obj[0] and obj[1]:
            conn.cursor().execute(sql, obj)
    except Exception as e:
        printError(createOBJ.__name__, e, False)


def createOBJPool(cmds, conn):
    for cmd in cmds:
        createOBJ(*cmd, conn=conn)


def getSQLCursor(path) -> sqlite3.Connection:  # type: ignore
    try:
        sqliteConnection = sqlite3.connect(path)
        print("Database created and Successfully Connected to SQLite")
        return sqliteConnection
    except Exception as e:
        printError(getSQLCursor.__name__, e, True)


def getSQL(conn, request):
    cursor = conn.cursor()
    cursor.execute(request)
    return cursor.fetchall()


# model training
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
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate * 5),
        metrics=["accuracy"],
    )

    return model


try:
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.safe_load(ymlfile)
    target = cfg["v2en"]["target"]
    first_lang = target[:2]
    second_lang = target[-2:]
    accept_percentage = cfg["v2en"]["accept_percentage"]
    time_allow = cfg["v2en"]['allow']["time"]
    resource_allow = cfg["v2en"]['allow']["resource"]
    thread_alow = cfg["v2en"]["thread"]["allow"]
    thread_limit = cfg["v2en"]["thread"]["limit"]
    table_name = cfg["sqlite"]["table_name"]
    trans_timeout = cfg["v2en"]["trans_timeout"]
    initial_sparsity = cfg["training"]["initial_sparsity"]
    final_sparsity = cfg["training"]["final_sparsity"]
    begin_step = cfg["training"]["begin_step"]
    end_step = cfg["training"]["end_step"]
    learning_rate = cfg["training"]["learning_rate"]
    allow_pruning = cfg["training"]["allow_pruning"]
except Exception as e:
    printError("importing config", e, True)
    exit()
pruning_params = {
    "pruning_schedule": tfmot.sparsity.keras.PolynomialDecay(
        initial_sparsity=initial_sparsity,
        final_sparsity=final_sparsity,
        begin_step=begin_step,
        end_step=end_step,
    ),
}
trans_dict = TransServer.TranslatorsServer().translators_dict

# logger init
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s\n%(message)s")
os.makedirs(".wav", exist_ok=True)

file_handler = logging.FileHandler(f"./logs/{target}.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logging.basicConfig(level=logging.DEBUG, handlers=[file_handler])
