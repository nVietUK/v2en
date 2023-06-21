import sqlite3
from difflib import SequenceMatcher
from html.parser import HTMLParser
import langcodes
import os
import requests
import string
import multiprocessing.pool
from addsent import target


class Logging:
    def __init__(self) -> None:
        self.logfile = open(f"./logs/{target}.log", "a")

    def toFile(self, text: str) -> None:
        self.logfile.write(text + "\n")

    def toConsole(self, text: str) -> None:
        print(text)

    def toBoth(self, text: str) -> None:
        self.toConsole(text)
        self.toFile(text)


logging = Logging()


# debug def
def printError(text, error, is_exit=True):
    logging.toFile(
        f"{'_'*50}\n\tExpectation while {text}\n\tError type: {type(error)}\n\t{error}\n{chr(8254)*50}"
    )
    if is_exit:
        exit(0)


def printInfo(name, pid):
    logging.toFile(f"Dive into {name} with pid id: {pid}")


# ask user defs
def askUserStr(name_value):
    answer = input(f"\t{name_value} >> ")
    return str(answer)


def askUserInt(name_value):
    answer = input(f"\t{name_value} >> ")
    return int(answer)


def askUserYN(message):
    is_agree = input(f"{message} (Y/n) ")
    return is_agree.lower() == "y" or is_agree == ""


# sqlite3 defs
def createSQLColumn(
    conn, col_name, col_type, table_name, debug, col_status="NOT NULL", col_value="N/A"
):
    try:
        conn.cursor().execute(
            """
            ALTER TABLE {}
            ADD {} {} {} DEFAULT {}
        """.format(
                table_name, col_name, col_type, col_status, col_value
            )
        )
    except Exception as e:
        printError(createSQLColumn.__name__, e, debug)


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


def createOBJ(conn, sql, obj):
    try:
        if obj[0] and obj[1]:
            conn.cursor().execute(sql, obj)
    except sqlite3.OperationalError as e:
        if "no column" in str(e):
            createSQLColumn(
                conn,
                str(e).split()[-1],
                askUserStr("col_type").upper(),
                askUserStr("col_status").upper(),
                str(askUserInt("col_value")),
            )
            createOBJ(conn, sql, obj)
    except Exception as e:
        printError(createOBJ.__name__, e)


def createOBJPool(cmds, con):
    [createOBJ(*cmd) for cmd in cmds]
    con.commit()


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


def isExistOnWiki(word: str, lang: str) -> bool:
    display_name = langcodes.Language.make(language=lang).display_name()

    class LanguageParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.isExist = False

        def handle_starttag(self, tag, attrs):
            if tag == "a":
                for attr in attrs:
                    if attr[0] == "href" and f"#{display_name}" == attr[1]:
                        self.isExist = True
            if tag == "span":
                for attr in attrs:
                    if attr[0] == "id" and attr[1] == display_name:
                        self.isExist = True

    printInfo(isExistOnWiki.__name__, multiprocessing.current_process().name)
    response = requests.get(f"https://en.wiktionary.org/wiki/{word}")
    parser = LanguageParser()
    parser.feed(response.text)
    return parser.isExist


def cleanScreen() -> None:
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


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
        printError(loadDictionary.__name__, e)


def saveDictionary(path, dictionary):
    try:
        with open(path, "w") as f:
            for e in dictionary:
                f.write(e + "\n")
    except Exception as e:
        printError(saveDictionary.__name__, e)
