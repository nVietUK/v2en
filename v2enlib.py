import os, string, httpx, sqlite3, resource, time, yaml, logging, librosa, string, gc
import deep_translator.exceptions, langcodes, translators.server, execjs._exceptions, deep_translator
from difflib import SequenceMatcher
from multiprocess.pool import ThreadPool, TimeoutError as TLE
from tabulate import tabulate
from tqdm import tqdm
from translators.server import TranslatorsServer


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


def translatorsTransExecutor(cmd, *args, **kwargs):
    return translatorsTrans(*cmd, *args, **kwargs)


# utils
def diffratio(x, y):
    return SequenceMatcher(None, x, y).ratio()


def isEmpty(path):
    return os.stat(path).st_size == 0


def convert(x: str) -> str:
    # fix bad data
    if "apos" in x or "quot" in x or "amp" in x:
        return ""

    x = x.replace("“", " “ ").replace("”", " ” ").replace("’", " ’ ")
    for punc in string.punctuation:
        x = x.replace(punc, f" {punc} ")
    return x.lower().replace("  ", " ").replace("  ", " ")


def get_wiktionary_headers(word: str) -> httpx.Response:
    return httpx.get(f"https://en.wiktionary.org/wiki/{word}")


def isExistOnWiki(word: str, lang: str) -> bool:
    display_name = langcodes.Language.make(language=lang).display_name()

    response = get_wiktionary_headers(word)
    return (
        f'href="#{display_name}"' in response.headers.get("link", "")
        or f'id="{display_name}"' in response.text
    )


def cleanScreen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def playFreq(freq, duration):
    if os.name == "nt":
        import winsound

        winsound.Beep(freq, duration)
    else:
        os.system(f"play -qn synth {duration/1000} sine {freq} >/dev/null 2>&1")


def playSound(melody: list, duration: list):
    melody = librosa.note_to_hz(melody)
    for note, dur in zip(melody, duration):
        playFreq(note, dur)


def checkLangFile(*args):
    for target in args:
        if os.path.exists(f"./cache/{target}.dic"):
            continue
        open(f"./cache/{target}.dic", "w").close()


def loadDictionary(path) -> list:
    try:
        if os.stat(path).st_size != 0:
            with open(path, "r") as f:
                return [word.rstrip("\n") for word in f.read().splitlines(True)]
    except Exception as e:
        printError(loadDictionary.__name__, e)
    return []


def saveDictionary(path, dictionary):
    try:
        with open(path, "w") as f:
            for e in dictionary:
                f.write(e + "\n")
    except Exception as e:
        printError("saveDictionary", e)


def function_timeout(s):
    def outer(fn):
        def inner(*args, **kwargs):
            with ThreadPool(processes=1) as pool:
                result = pool.apply_async(fn, args=args, kwds=kwargs)
                output = kwargs.get("default_value", None)
                try:
                    output = result.get(timeout=s)
                except TLE:
                    pool.terminate()
                    pool.join()
                return output

        return inner

    return outer


def func_timeout(timeout, func, *args, **kargs):
    @function_timeout(timeout)
    def execute(func, *args, **kargs):
        return func(*args, **kargs)

    return execute(func, *args, **kargs)


def measure(func):
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        execution_time = end_time - start_time
        before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        resource_consumption = before / 1024 / 1024  # Memory usage in MB
        if execution_time < time_allow and resource_consumption < resource_allow:
            return result

        logger.warn(
            f"{func.__name__}'s result:\n\tExecution time: {execution_time} seconds\n\tMemory consumption: {resource_consumption} MB"
        )
        return result

    return wrapper


def terminalWidth():
    return os.get_terminal_size().columns


# thread utils
def funcPool(func, cmds, executor, isAllowThread=True, strictOrder=False) -> list:
    try:
        with executor(
            min(len(cmds), thread_limit if thread_limit > 0 else len(cmds)),
        ) as ex:
            if not thread_alow or not isAllowThread:
                return [func(cmd) for cmd in tqdm(cmds, leave=False)]
            with tqdm(total=len(cmds), leave=False) as pbar:
                results = []
                for res in (
                    ex.imap(func, cmds)
                    if strictOrder
                    else ex.imap_unordered(func, cmds)
                ):
                    pbar.update(1)
                    results.append(res)
                return results
    except Exception as e:
        printError("funcPool", e, False)
    return []


# debug def
def printError(text, error, is_exit=True):
    if error == OSError:
        return
    logger.fatal(
        f"{'_'*50}\n\tExpectation while {text}\n\tError type: {type(error)}\n\t{error}\n{chr(8254)*50}"
    )
    if is_exit:
        exit(0)


def printInfo(name, pid):
    logger.info(f"Dive into {name} with pid id: {pid}")


# translate def
def deepTransGoogle(x: str, source: str, target: str) -> str:
    try:
        return deep_translator.GoogleTranslator(source=source, target=target).translate(
            x
        )
    except deep_translator.exceptions.LanguageNotSupportedException:
        return deepTransGoogle(
            x, str(langcodes.Language.get(source)), str(langcodes.Language.get(target))
        )
    except Exception as e:
        printError(deepTransGoogle.__name__, e, False)
        return ""


@measure
def translatorsTrans(
    trans, cmd: list, trans_timeout, tname: str = "", isDived: bool = False
) -> list:
    try:
        ou = func_timeout(
            trans_timeout,
            trans,
            query_text=cmd[0],
            from_language=cmd[1],
            to_language=cmd[2],
            default_value="",
        )
        return [ou, tname]
    except translators.server.TranslatorError as e:
        if not isDived:
            return _extracted_from_translatorsTrans_13(
                cmd, e, trans, trans_timeout / 2, tname
            )
    except (execjs._exceptions.RuntimeUnavailableError, TypeError, ValueError):
        pass
    except Exception as e:
        printError(translatorsTrans.__name__, e, False)
    return [deepTransGoogle(*cmd), "google"]


# TODO Rename this here and in `translatorsTrans`
def _extracted_from_translatorsTrans_13(cmd, e, trans, trans_timeout, tname) -> list:
    try:
        tcmd, execute = cmd.copy(), False
        if (e.args[0]).find("vie") != -1:
            tcmd[2 if (e.args[0]).find("to_language") != -1 else 1] = "vie"
            execute = True

        if (e.args[0]).find("vi_VN") != -1:
            tcmd[2 if (e.args[0]).find("to_language") != -1 else 1] = "vi_VN"
            execute = True

        if (e.args[0]).find("vi-VN") != -1:
            tcmd[2 if (e.args[0]).find("to_language") != -1 else 1] = "vi-VN"
            execute = True
        return (
            translatorsTrans(trans, tcmd, trans_timeout, tname, True)
            if execute
            else ["", ""]
        )
    except IndexError:
        return ["", ""]


@measure
def transIntoList(sent, source_lang, target_lang, target_dictionary):
    return funcPool(
        checkSpellingExecutor,
        [
            [convert(e[0]), target_dictionary, target_lang, e[1]]
            for e in funcPool(
                translatorsTransExecutor,
                [
                    [
                        trans,
                        [sent, source_lang, target_lang],
                        trans_timeout,
                        name,
                    ]
                    for name, trans in translator.translators_dict.items()
                ],
                ThreadPool,
            )
        ],
        ThreadPool,
    )


# language utils
def checkSpelling(
    text: str, dictionary: list, lang: str, tname: str = ""
) -> str | list:
    word = ""
    try:
        words = text.split()
        outstr = ""
        for idx, word in enumerate(words):
            if (
                word in dictionary
                or word.isnumeric()
                or word in string.punctuation
                or isExistOnWiki(word, lang)
                or isExistOnWiki(f"{words[idx-1]} {word}", lang)
                or (
                    idx + 1 < len(words)
                    and isExistOnWiki(f"{word} {words[idx+1]}", lang)
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
        printError(checkSpelling.__name__, e)
    return ["", ""] if tname else ""


def checkSpellingExecutor(cmd):
    return checkSpelling(*cmd)


@measure
def addSent(input_sent: InputSent, first_dictionary, second_dictionary):
    is_agree, first_dump_sent, second_dump_sent, cmds, trans_data = (
        False,
        "",
        "",
        [],
        [],
    )
    input_sent.first, input_sent.second = funcPool(
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
    )
    if input_sent.isValid():
        is_error = True
        first_trans, second_trans = funcPool(
            transIntoListExecutor,
            [
                [input_sent.first, first_lang, second_lang, second_dictionary],
                [input_sent.second, second_lang, first_lang, first_dictionary],
            ],
            ThreadPool,
        )
        trans_data = [
            InputSent(
                input_sent.first,
                first_tran[0],
                first_tran[1],
                diffratio(input_sent.second, first_tran[0]),
            )
            for first_tran in first_trans
            if first_tran[0]
        ] + [
            InputSent(
                second_tran[0],
                input_sent.second,
                second_tran[1],
                diffratio(input_sent.first, second_tran[0]),
            )
            for second_tran in second_trans
            if second_tran[0]
        ]

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

        print_data = [["Data set", input_sent.first, input_sent.second, "N/A"]] + [
            [e.isFrom, e.first, e.second, e.accurate] for e in trans_data
        ]
        width = int(terminalWidth() / 4)
        logger.log(
            101,
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
    return first_dump_sent, second_dump_sent, cmds, is_agree


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
        printError(createSQLtable.__name__, e)


def createOBJ(sql, obj, conn):
    try:
        if obj[0] and obj[1]:
            conn.cursor().execute(sql, obj)
    except Exception as e:
        printError(createOBJ.__name__, e)


def createOBJPool(cmds, conn):
    for cmd in cmds:
        createOBJ(*cmd, conn=conn)


def getSQLCursor(path) -> sqlite3.Connection:
    try:
        sqliteConnection = sqlite3.connect(path)
        print("Database created and Successfully Connected to SQLite")
        return sqliteConnection
    except Exception as e:
        printError(getSQLCursor.__name__, e, True)
        exit(0)


def getSQL(conn, request):
    cursor = conn.cursor()
    cursor.execute(request)
    return cursor.fetchall()


with open("config.yml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)
target = cfg["v2en"]["target"]
first_lang = target[:2]
second_lang = target[-2:]
accept_percentage = cfg["v2en"]["accept_percentage"]
time_allow = cfg["v2en"]["time_allow"]
resource_allow = cfg["v2en"]["resource_allow"]
thread_alow = cfg["v2en"]["thread"]["allow"]
thread_limit = cfg["v2en"]["thread"]["limit"]
table_name = cfg["sqlite"]["table_name"]
translator = TranslatorsServer()
trans_timeout = cfg["v2en"]["trans_timeout"]

# logger init
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s\n%(message)s")
logger = logging.getLogger("v2en")
logger.setLevel(logging.WARN)
file_handler = logging.FileHandler(f"./logs/{target}.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(101)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
