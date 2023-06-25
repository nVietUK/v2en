import os, string, httpx, langcodes, sqlite3, resource, time, yaml, logging, librosa
from difflib import SequenceMatcher
from multiprocess.pool import ThreadPool, TimeoutError as TLE


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
accept_percentage = cfg["v2en"]["accept_percentage"]
time_allow = cfg["v2en"]["time_allow"]
resource_allow = cfg["v2en"]["resource_allow"]

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
