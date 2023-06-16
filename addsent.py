import os
import yaml
import sqlite3
import requests
import multiprocessing
import multiprocessing.pool
import time
from difflib import SequenceMatcher
import deep_translator
import string

with open("config.yml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)
target = cfg["v2en"]["target"]
lang_source = target[:2]
debug = False
lang_target = target[-2:]
accecpt_percentage = 0.65
is_auto = True
table_name = "Translation"
num_process = 6


# debug def
def printError(text, error, is_exit=True):
    print(
        "---------------------\n\tExpectation while {} \
        \n\tError type: {}\n--------------------- \
          \n\n{}".format(
            text, type(error), error
        )
    )
    if is_exit:
        exit(0)


def printInfo(name, pid):
    if not debug:
        return
    print(f"Dive into {name} with pid id: {pid}")


# translate def
def gtrans(x: str, source: str, target: str) -> str:
    try:
        return deep_translator.GoogleTranslator(source=source, target=target).translate(x)
    except Exception as e:
        printError(gtrans.__name__, e, False)


def dtrans(x, source, target):
    return ""
    try:
        return deep_translator.MyMemoryTranslator(source=source, target=target).translate(x)
    except deep_translator.exceptions.TooManyRequests:
        return ""
    except Exception as e:
        printError(dtrans.__name__, e, False)


# utils
def diffratio(x, y):
    return SequenceMatcher(None, x, y).ratio()

def isEmpty(path):
    return os.stat(path).st_size == 0

def convert(x: str) -> str:
    x = x.replace("“", " “ ").replace("”", " ” ").replace("’", " ’ ")
    for punc in string.punctuation:
        x = x.replace(punc, f" {punc} ")
    return x.lower().replace("  ", " ").replace("  ", " ")


def isExistOnWiki(word: str) -> bool:
    printInfo(isExistOnWiki.__name__, multiprocessing.current_process().name)
    return (
        requests.get(f"https://en.wiktionary.org/wiki/{word}").status_code == 200
        or requests.get(f"https://en.wikipedia.org/wiki/{word}").status_code == 200
    )


def isExistOnWikiPool(cmds):
    pool = multiprocessing.pool.ThreadPool(processes=num_process)
    return pool.map(isExistOnWiki, cmds)


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
            return f.read().splitlines(True)
    except Exception as e:
        printError(loadDictionary.__name__, e)


def saveDictionary(path, dictionary):
    try:
        with open(path, "w") as f:
            for e in dictionary:
                f.write(e+'\n')
    except Exception as e:
        printError(saveDictionary.__name__, e)


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


# sql defs
def createSQLColumn(conn, col_name, col_type, col_status="NOT NULL", col_value="N/A"):
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
        printError(createSQLColumn.__name__, e)


def createSQLtable(connection):
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
        conn.cursor().execute(sql, obj)
        conn.commit()
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


def getSQLCursor(path):
    try:
        sqliteConnection = sqlite3.connect(path)
        print("Database created and Successfully Connected to SQLite")
    except sqlite3.Error as error:
        printError(getSQLCursor.__name__, error)
    return sqliteConnection


# language utils
def checkSpelling(text, dictionary) -> str:
    printInfo(checkSpelling.__name__, multiprocessing.current_process().pid)
    try:
        words = text.split()
        outstr = ""
        for idx, word in enumerate(words):
            if (
                word in dictionary
                or word.isnumeric()
                or isExistOnWiki(word)
                or isExistOnWiki(f"{words[idx-1]} {word}")
                or (idx+1 < len(words) and isExistOnWiki(f"{word} {words[idx+1]}"))
            ):
                outstr += f"{word} "
            else:
                raise ValueError(f"{word} not existed")
            if word.isalpha() and word not in dictionary:
                dictionary.insert(0, word)
        return outstr
    except ValueError:
        if not is_auto and askUserYN(f"Add {word} to dictionary?"):
            dictionary[word] = 1
            print(f"add {word} !")
            return checkSpelling(text, dictionary)
        else:
            printError(f"add word {word}", "", False)
            return ""
    except Exception as e:
        printError(checkSpelling.__name__, e)


def checkSpellingExecute(cmd):
    return checkSpelling(cmd[0], cmd[1])


def checkSpellingPool(cmds):
    pool = multiprocessing.pool.ThreadPool(processes=num_process)
    return pool.map(checkSpellingExecute, cmds)


if __name__ == "__main__":
    sql_connection = getSQLCursor(cfg["sqlite"]["path"])
    createSQLtable(sql_connection)
    checkLangFile(lang_source, lang_target)

    first_dictionary_path = f"./cache/{lang_source}.dic"
    second_dictionary_path = f"./cache/{lang_target}.dic"
    first_dictionary = loadDictionary(first_dictionary_path)
    second_dictionary = loadDictionary(second_dictionary_path)
    first_input_path = f"./data/{lang_source}.txt"
    first_input_dump = open(f"./data/{lang_source}.dump", "a")
    second_input_path = f"./data/{lang_target}.txt"
    second_input_dump = open(f"./data/{lang_target}.dump", "a")
    while 1:
        time_start = time.time()
        is_error = False
        is_agree = "!"
        is_add = False
        add_gtrans = False
        add_dtrans = False
        if isEmpty(first_input_path) or isEmpty(second_input_path):
            print("Done!")
            exit()
        first_input_file = open(first_input_path, "r")
        second_input_file = open(second_input_path, "r")
        first_input_sent, second_input_sent = checkSpellingPool(
            (
                [
                    convert(str(first_input_file.readline()).replace("\n", "")),
                    first_dictionary,
                ],
                [
                    convert(str(second_input_file.readline()).replace("\n", "")),
                    second_dictionary,
                ],
            )
        )
        if not first_input_sent or not second_input_sent:
            is_error = True
        else:
            try:
                (
                    first_input_gtrans,
                    second_input_gtrans,
                    first_input_dtrans,
                    second_input_dtrans,
                ) = checkSpellingPool(
                    (
                        (
                            convert(gtrans(first_input_sent, lang_source, lang_target)),
                            second_dictionary,
                        ),
                        (
                            convert(gtrans(second_input_sent, lang_target, lang_source)),
                            first_dictionary,
                        ),
                        (
                            convert(dtrans(first_input_sent, lang_source, lang_target)),
                            second_dictionary,
                        ),
                        (
                            convert(dtrans(second_input_sent, lang_target, lang_source)),
                            first_dictionary,
                        ),
                    )
                )
            except Exception as e:
                is_error = True
                printError("translate section", e, False)
            else:
                fir_to_sec_gratio = diffratio(first_input_sent, second_input_gtrans)
                sec_to_fir_gratio = diffratio(second_input_sent, first_input_gtrans)
                fir_to_sec_dratio = diffratio(first_input_sent, second_input_dtrans)
                sec_to_fir_dratio = diffratio(second_input_sent, first_input_dtrans)
                if fir_to_sec_gratio > accecpt_percentage or sec_to_fir_gratio > accecpt_percentage:
                    is_agree = ""
                    add_gtrans = True
                if fir_to_sec_dratio > accecpt_percentage or sec_to_fir_dratio > accecpt_percentage:
                    is_agree = ""
                    add_dtrans = True

                if not add_dtrans and not add_gtrans:
                    first_input_trans = first_input_gtrans
                    second_input_trans = second_input_gtrans
                    fir_to_sec_ratio = fir_to_sec_gratio
                    sec_to_fir_ratio = sec_to_fir_gratio
                    add_gtrans = True
                    add_dtrans = False
                    if abs(fir_to_sec_ratio - sec_to_fir_ratio) < abs(
                        fir_to_sec_dratio - sec_to_fir_dratio
                    ):
                        first_input_trans = first_input_dtrans
                        second_input_trans = second_input_dtrans
                        fir_to_sec_ratio = fir_to_sec_dratio
                        sec_to_fir_ratio = sec_to_fir_dratio
                        add_dtrans = True
                        add_gtrans = False
                    if not is_auto:
                        cleanScreen()
                        print(
                            f"\t{lang_source} input (acc: {fir_to_sec_ratio})\n\t\t- {first_input_sent}\n\t\t- {second_input_trans}\n"
                        )
                        print(
                            f"\t{lang_target} input (acc: {sec_to_fir_ratio})\n\t\t- {second_input_sent}\n\t\t- {first_input_trans}\n"
                        )
                        is_agree = askUserStr("\tAdd to database? (Y/n)")
                    else:
                        is_error = True
                elif not add_dtrans and not is_auto:
                    cleanScreen()
                    print(
                        f"\t{lang_source} input (acc: {fir_to_sec_dratio})\n\t\t- {first_input_sent}\n\t\t- {second_input_dtrans}\n"
                    )
                    print(
                        f"\t{lang_target} input (acc: {sec_to_fir_dratio})\n\t\t- {second_input_sent}\n\t\t- {first_input_dtrans}\n"
                    )
                    is_add = askUserYN("\tAdd to database?")
                    add_dtrans = is_add.lower() == "y" or is_add == ""
                elif not add_gtrans and not is_auto:
                    cleanScreen()
                    print(
                        f"\t{lang_source} input (acc: {fir_to_sec_gratio})\n\t\t- {first_input_sent}\n\t\t- {second_input_gtrans}\n"
                    )
                    print(
                        f"\t{lang_target} input (acc: {sec_to_fir_gratio})\n\t\t- {second_input_sent}\n\t\t- {first_input_gtrans}\n"
                    )
                    is_add = askUserYN("\tAdd to database?")
                    add_gtrans = is_add.lower() == "y" or is_add == ""
        if (is_agree.lower() == "y" or is_agree == "") and not is_error:
            table_command = """
                INSERT INTO {}(Source, Target, Verify)
                VALUES(?,?,?)
            """
            createOBJ(
                sql_connection,
                table_command.format(table_name),
                (first_input_sent, second_input_sent, 1),
            )
            if add_dtrans:
                createOBJ(
                    sql_connection,
                    table_command.format(table_name),
                    (first_input_sent, first_input_dtrans, 1),
                )
                createOBJ(
                    sql_connection,
                    table_command.format(table_name),
                    (second_input_dtrans, second_input_sent, 1),
                )
            if add_gtrans:
                createOBJ(
                    sql_connection,
                    table_command.format(table_name),
                    (first_input_sent, first_input_gtrans, 1),
                )
                createOBJ(
                    sql_connection,
                    table_command.format(table_name),
                    (second_input_gtrans, second_input_sent, 1),
                )
            is_add = True
        elif is_agree == "exit":
            break
        else:
            first_input_dump.write(f"\n{(first_input_sent)}")
            second_input_dump.write(f"\n{(second_input_sent)}")
        saveIN = first_input_file.read().splitlines(True)
        saveOU = second_input_file.read().splitlines(True)
        first_input_file.close()
        second_input_file.close()
        with open(first_input_path, "w") as file:
            file.writelines(saveIN[1:])
        with open(second_input_path, "w") as file:
            file.writelines(saveOU[1:])
        print(
            f"\t({(time.time()-time_start):0,.2f}) ({is_add}) >> ",
            first_input_sent,
            "|",
            second_input_sent,
        )
    first_input_dump.close()
    second_input_dump.close()
    saveDictionary(first_dictionary_path, first_dictionary)
    saveDictionary(second_dictionary_path, second_dictionary)
