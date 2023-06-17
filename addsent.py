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
import translators

with open("config.yml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)
target = cfg["v2en"]["target"]
first_lang = target[:2]
debug = False
second_lang = target[-2:]
accept_percentage = 0.65
is_auto = True
table_name = "Translation"
num_process = 15
"""
    translate service:
    - google
    - bing
    - yandex
    - alibaba
    - youdao
    - sogou
    - argox
"""
translators_target = ["google", "yandex", "alibaba", , "youdao", "sogou", "argox"]


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
def deepTransGoogle(x: str, source: str, target: str) -> str:
    try:
        return deep_translator.GoogleTranslator(source=source, target=target).translate(x)
    except Exception as e:
        printError(deepTransGoogle.__name__, e, False)
        return ""


def translatorsTrans(x, source, target, host):
    try:
        return translators.translate_text(
            x, from_language=source, to_language=target, translator=host
        )
    except Exception as e:
        printError(translatorsTrans.__name__, e, False)
        return deepTransGoogle(x, source, target)


def translatorsTransExecute(cmd):
    return translatorsTrans(cmd[0], cmd[1], cmd[2], cmd[3])


def translatorsTransPool(cmds):
    return multiprocessing.pool.ThreadPool(processes=num_process).map(translatorsTransExecute, cmds)


# utils
def diffratio(x, y):
    return SequenceMatcher(None, x, y).ratio()


def isEmpty(path):
    return os.stat(path).st_size == 0


def convert(x: str) -> str:
    # fix bad data
    if "apos" in x or "quot" in x:
        return ""

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


def createOBJExecute(cmd):
    return createOBJ(cmd[0], cmd[1], cmd[2])


def createOBJPool(cmds, con):
    for cmd in cmds:
        createOBJExecute(cmd)
    con.commit()


def getSQLCursor(path):
    try:
        sqliteConnection = sqlite3.connect(path)
        print("Database created and Successfully Connected to SQLite")
    except sqlite3.Error as error:
        printError(getSQLCursor.__name__, error)
    return sqliteConnection


# language utils
def checkSpelling(text, dictionary, lang) -> str:
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
                or (idx + 1 < len(words) and isExistOnWiki(f"{word} {words[idx+1]}"))
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
            with open(f"./cache/{lang}.err", "a") as f:
                f.write(word + "\n")
            return ""
    except Exception as e:
        printError(checkSpelling.__name__, e)


def checkSpellingExecute(cmd):
    return checkSpelling(cmd[0], cmd[1], cmd[2])


def checkSpellingPool(cmds):
    return multiprocessing.pool.ThreadPool(processes=num_process).map(checkSpellingExecute, cmds)


if __name__ == "__main__":
    sql_connection = getSQLCursor(cfg["sqlite"]["path"])
    createSQLtable(sql_connection)
    checkLangFile(first_lang, second_lang)

    first_dictionary_path = f"./cache/{first_lang}.dic"
    second_dictionary_path = f"./cache/{second_lang}.dic"
    first_dictionary = loadDictionary(first_dictionary_path)
    second_dictionary = loadDictionary(second_dictionary_path)
    first_path = f"./data/{first_lang}.txt"
    second_path = f"./data/{second_lang}.txt"
    while 1:
        time_start = time.time()
        is_error = False
        is_agree = "!"
        is_add = False
        if isEmpty(first_path) or isEmpty(second_path):
            print("Done!")
            exit()
        first_file = open(first_path, "r")
        first_dump = open(f"./data/{first_lang}.dump", "a")
        second_file = open(second_path, "r")
        second_dump = open(f"./data/{second_lang}.dump", "a")
        first_sent, second_sent = checkSpellingPool(
            (
                [
                    convert(str(first_file.readline()).replace("\n", "")),
                    first_dictionary,
                    first_lang,
                ],
                [
                    convert(str(second_file.readline()).replace("\n", "")),
                    second_dictionary,
                    second_lang,
                ],
            )
        )
        if not first_sent or not second_sent:
            is_error = True
        else:
            try:
                second_trans = checkSpellingPool(
                    (
                        [convert(trans), first_dictionary, first_lang]
                        for trans in translatorsTransPool(
                            (
                                (second_sent, second_lang, first_lang, host)
                                for host in translators_target
                            )
                        )
                    )
                )
                first_trans = checkSpellingPool(
                    (
                        [convert(trans), second_dictionary, second_lang]
                        for trans in translatorsTransPool(
                            (
                                (first_sent, first_lang, second_lang, host)
                                for host in translators_target
                            )
                        )
                    )
                )
            except Exception as e:
                is_error = True
                printError("translate section", e, False)
            else:
                first_ratio = [diffratio(first_sent, trans_sent) for trans_sent in second_trans]
                second_ratio = [diffratio(second_sent, trans_sent) for trans_sent in first_trans]

                if (
                    all(not ratio > accept_percentage for ratio in first_ratio)
                    and all(not ratio > accept_percentage for ratio in second_ratio)
                    and not is_auto
                ):
                    cleanScreen()
                    print(
                        f"\t{first_lang} input (acc: {first_ratio[0]})\n\t\t- {first_sent}\n\t\t- {second_trans[0]}\n"
                    )
                    print(
                        f"\t{second_lang} input (acc: {second_ratio[0]})\n\t\t- {second_sent}\n\t\t- {first_trans[0]}\n"
                    )
                    is_agree = askUserStr("Add to database? (Y/n)")
                elif any(ratio > accept_percentage for ratio in first_ratio) or any(
                    ratio > accept_percentage for ratio in second_ratio
                ):
                    is_agree = ""
                else:
                    is_error = True
        if (is_agree.lower() == "y" or is_agree == "") and not is_error:
            table_command = """
                INSERT INTO {}(Source, Target, Verify)
                VALUES(?,?,?)
            """
            cmds = [
                [sql_connection, table_command.format(table_name), (first_sent, second_sent, 1)]
            ]
            for first_tran, second_tran, first_rate, second_rate in zip(
                first_trans, second_trans, first_ratio, second_ratio
            ):
                if first_rate > accept_percentage or second_rate > accept_percentage:
                    cmds += [
                        [
                            sql_connection,
                            table_command.format(table_name),
                            (first_sent, first_tran, 1),
                        ],
                        [
                            sql_connection,
                            table_command.format(table_name),
                            (second_tran, second_sent, 1),
                        ],
                    ]
            createOBJPool(cmds, sql_connection)
            is_add = True
        elif is_agree == "exit":
            break
        else:
            if first_sent != "" and second_sent != "":
                first_dump.write(f"\n{(first_sent)}")
                second_dump.write(f"\n{(second_sent)}")
        saveIN = first_file.read().splitlines(True)
        saveOU = second_file.read().splitlines(True)
        first_file.close()
        second_file.close()
        with open(first_path, "w") as file:
            file.writelines(saveIN[1:])
        with open(second_path, "w") as file:
            file.writelines(saveOU[1:])
        print(
            f"\t({(time.time()-time_start):0,.2f}) ({is_add}) >> ",
            first_sent,
            "|",
            second_sent,
        )
        first_dump.close()
        second_dump.close()
        saveDictionary(first_dictionary_path, first_dictionary)
        saveDictionary(second_dictionary_path, second_dictionary)
