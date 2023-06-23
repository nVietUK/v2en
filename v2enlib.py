import os, string, httpx, langcodes, sqlite3, resource, time
from difflib import SequenceMatcher
from functools import lru_cache
from multiprocess.pool import TimeoutError, Pool


# classes
class Logging:
    def __init__(self, target: str) -> None:
        self.file_path = f"./logs/{target}.log"

    def to_file(self, text: str) -> None:
        with open(self.file_path, "a") as logfile:
            logfile.write(text + "\n")

    def to_console(self, text: str) -> None:
        print(text)

    def to_both(self, text: str) -> None:
        self.to_console(text)
        self.to_file(text)


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


@lru_cache(maxsize=1024)
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


def checkLangFile(*args):
    for target in args:
        if os.path.exists(f"./cache/{target}.dic"):
            continue
        open(f"./cache/{target}.dic", "w").close()


def loadDictionary(path):
    try:
        if os.stat(path).st_size == 0:
            return []
        with open(path, "r") as f:
            return [word.rstrip("\n") for word in f.read().splitlines(True)]
    except Exception as e:
        printError(loadDictionary.__name__, e, logging)


def saveDictionary(path, dictionary):
    try:
        with open(path, "w") as f:
            for e in dictionary:
                f.write(e + "\n")
    except Exception as e:
        printError(saveDictionary.__name__, e, logging)


def timming(func, *args):
    time_start = time.time()
    logging.to_console(f"{func.__name__} is timming")
    ou = func(*args)
    logging.to_console(f"{func.__name__}: {time.time() - time_start}")
    return ou


def function_timeout(s):
    def outer(fn):
        def inner(*args, **kwargs):
            with Pool(1) as p:
                result = p.apply_async(fn, args=args, kwds=kwargs)
                output = kwargs["default_value"]
                try:
                    output = result.get(timeout=s)
                except TimeoutError:
                    p.terminate()
                p.join()
                return output

        return inner

    return outer


def func_timeout(timeout, func, *args, **kargs):
    @function_timeout(timeout)
    def execute(func, *args, **kargs):
        return func(*args, **kargs)

    return execute(func, *args, **kargs)


time_allow = 10
resource_allow = 5


def measure(logging):
    def wrap(func):
        def wrapper(*args, **kwargs):
            start_time = time.monotonic()
            result = func(*args, **kwargs)
            end_time = time.monotonic()
            execution_time = end_time - start_time
            before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            resource_consumption = before / 1024 / 1024  # Memory usage in MB
            if execution_time < time_allow and resource_consumption < resource_allow:
                return result

            logging.to_file(
                f"{func.__name__}'s result:\n\tExecution time: {execution_time} seconds\n\tMemory consumption: {resource_consumption} MB"
            )
            return result

        return wrapper

    return wrap


# debug def
def printError(text, error, logging: Logging, is_exit=True):
    logging.to_file(
        f"{'_'*50}\n\tExpectation while {text}\n\tError type: {type(error)}\n\t{error}\n{chr(8254)*50}"
    )
    if is_exit:
        exit(0)


def printInfo(name, pid, logging: Logging):
    logging.to_file(f"Dive into {name} with pid id: {pid}")


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
        printError(createSQLtable.__name__, e, logging)


def createOBJ(conn, sql, obj):
    try:
        if obj[0] and obj[1]:
            conn.cursor().execute(sql, obj)
    except Exception as e:
        printError(createOBJ.__name__, e, logging)


@measure
def createOBJPool(cmds, con):
    for cmd in cmds:
        createOBJ(*cmd)
    con.commit()


def getSQLCursor(path) -> sqlite3.Connection:
    try:
        sqliteConnection = sqlite3.connect(path)
        print("Database created and Successfully Connected to SQLite")
        return sqliteConnection
    except Exception as e:
        printError(getSQLCursor.__name__, e, logging, True)
        exit(0)


def getSQL(conn, request):
    cursor = conn.cursor()
    cursor.execute(request)
    return cursor.fetchall()
from addsent import target
logging = Logging(target)