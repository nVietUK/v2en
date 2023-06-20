import yaml
from multiprocessing.pool import ThreadPool
from time import time
from deep_translator import GoogleTranslator
import string
from translators import translate_text
import signal
from v2enlib import *
from columnar import columnar
from click import style

with open("config.yml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)
target = cfg["v2en"]["target"]
table_name = cfg["sqlite"]["table_name"]
first_lang = target[:2]
second_lang = target[-2:]
accept_percentage = 0.65
is_auto = True
first_dictionary_path = f"./cache/{first_lang}.dic"
second_dictionary_path = f"./cache/{second_lang}.dic"
main_execute = True
num_sent = 25
false_allow = 50
thread_alow = True
"""
    translate service:
    - google
    - bing
    - alibaba
    - sogou
"""
translators_target = ["google", "bing", "sogou", "alibaba"]


class InputSent:
    def __init__(
        self,
        first: str = "",
        second: str = "",
        isFrom: str = "",
        accurate: float = 0,
    ) -> None:
        self.isFrom = "Data set" if not isFrom else isFrom
        self.first = "N/A" if not first else first
        self.second = "N/A" if not second else second
        self.accurate = accurate
        self.isAdd = accurate > accept_percentage

    def isValid(self) -> bool:
        return bool(self.first and self.second)

    def SQLFormat(self) -> tuple:
        return (self.first, self.second, 1 if self.isAdd else 0)


# translate def
def deepTransGoogle(x: str, source: str, target: str) -> str:
    try:
        return GoogleTranslator(source=source, target=target).translate(x)
    except Exception as e:
        printError(deepTransGoogle.__name__, e, False)
        return ""


def translatorsTrans(x: str, source: str, target: str, host: str) -> str:
    try:
        ou = translate_text(
            x, from_language=source, to_language=target, translator=host
        )
        if type(ou) != str:
            printError(translatorsTrans.__name__, Exception("Type error"), False)
            return deepTransGoogle(x, source, target)
        return ou
    except Exception as e:
        printError(translatorsTrans.__name__, e, False)
        return deepTransGoogle(x, source, target)


def translatorsTransPool(cmds) -> list:
    return (
        ThreadPool(processes=len(cmds) + 2).map(
            lambda cmd: translatorsTrans(*cmd), cmds
        )
        if thread_alow
        else [translatorsTrans(*cmd) for cmd in cmds]
    )


def transIntoList(sent, source_lang, target_lang, target_dictionary):
    ou = checkSpellingPool(
        [
            [convert(e), target_dictionary, target_lang]
            for e in translatorsTransPool(
                [(sent, source_lang, target_lang, host) for host in translators_target]
            )
        ]
    )
    return [(sou, host) for sou, host in zip(ou, translators_target)]


def transIntoListPool(cmds):
    return (
        ThreadPool(processes=len(cmds) + 2).map(lambda cmd: transIntoList(*cmd), cmds)
        if thread_alow
        else [transIntoList(*cmd) for cmd in cmds]
    )


# language utils
def checkSpelling(text: str, dictionary: list, lang: str) -> str:
    printInfo(checkSpelling.__name__, multiprocessing.current_process().pid)
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
        return outstr
    except ValueError:
        printError(
            f"add word for {lang}",
            Exception(f"{word} isn't existed on Wikitionary!"),
            False,
        )
    except Exception as e:
        printError(checkSpelling.__name__, e)
    return ""


def checkSpellingPool(cmds):
    return (
        ThreadPool(processes=len(cmds) + 2).map(lambda cmd: checkSpelling(*cmd), cmds)
        if thread_alow
        else [checkSpelling(*cmd) for cmd in cmds]
    )


def addSent(input_sent: InputSent):
    time_start = time()
    is_agree, first_dump_sent, second_dump_sent, cmds, trans_data = (
        False,
        "",
        "",
        [],
        [],
    )
    input_sent.first, input_sent.second = checkSpellingPool(
        [
            [convert(input_sent.first.replace("\n", "")), first_dictionary, first_lang],
            [
                convert(input_sent.second.replace("\n", "")),
                second_dictionary,
                second_lang,
            ],
        ]
    )
    if input_sent.isValid():
        is_error = True
        try:
            first_trans, second_trans = transIntoListPool(
                [
                    [input_sent.first, first_lang, second_lang, second_dictionary],
                    [input_sent.second, second_lang, first_lang, first_dictionary],
                ]
            )
        except Exception as e:
            printError("translate section", e, False)
        else:
            trans_data = [
                InputSent(
                    input_sent.first,
                    first_tran[0],
                    first_tran[1],
                    diffratio(input_sent.second, first_tran[0]),
                )
                for first_tran in first_trans
            ] + [
                InputSent(
                    second_tran[0],
                    input_sent.second,
                    second_tran[1],
                    diffratio(input_sent.first, second_tran[0]),
                )
                for second_tran in second_trans
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
                        sql_connection,
                        table_command.format(table_name),
                        (input_sent.first, input_sent.second, 1),
                    ]
                ] + [
                    [
                        sql_connection,
                        table_command.format(table_name),
                        e.SQLFormat(),
                    ]
                    if e.isAdd
                    else None
                    for e in trans_data
                ]
        if is_error:
            first_dump_sent, second_dump_sent = input_sent.first, input_sent.second

    print_data = [
        ["Data set", input_sent.first, input_sent.second, is_agree, "N/A"]
    ] + [[e.isFrom, e.first, e.second, e.isAdd, e.accurate] for e in trans_data]
    print_patterns = [
        ("google", lambda text: style(text, bg="white")),
        ("bing", lambda text: style(text, bg="blue")),
        ("sogou", lambda text: style(text, bg="bright_yellow")),
        ("alibaba", lambda text: style(text, bg="yellow")),
        ("From", lambda text: style(text, bg="bright_black")),
        ("Source", lambda text: style(text, bg="bright_black")),
        ("Target", lambda text: style(text, bg="bright_black")),
        ("Is add?", lambda text: style(text, bg="bright_black")),
        ("Accuracy?", lambda text: style(text, bg="bright_black")),
        ("False", lambda text: style(text, fg="bright_red")),
        ("True", lambda text: style(text, fg="bright_green")),
        ("N/A", lambda text: style(text, bg="red")),
    ]
    logging.critical(
        columnar(
            data=print_data,
            headers=["From", "Source", "Target", "Is add?", "Accuracy?"],
            patterns=print_patterns,
            max_column_width=80
        )
        + f"\t({addSent.__name__}) time consume: {(time()-time_start):0,.2f}"
    )
    return first_dump_sent, second_dump_sent, cmds, is_agree


def addSentPool(cmds: list):
    if thread_alow:
        return multiprocessing.pool.ThreadPool(processes=len(cmds) + 2).map(
            addSent, cmds
        )
    return [addSent(cmd) for cmd in cmds]


def signalHandler(sig, frame):
    global main_execute
    print("\tStop program!")
    main_execute = False


if __name__ == "__main__":
    checkLangFile(first_lang, second_lang)
    first_dictionary = loadDictionary(first_dictionary_path)
    second_dictionary = loadDictionary(second_dictionary_path)
    signal.signal(signal.SIGINT, signalHandler)
    sql_connection = getSQLCursor(cfg["sqlite"]["path"])
    createSQLtable(sql_connection, table_name)
    false_count = 0

    first_path, second_path = f"./data/{first_lang}.txt", f"./data/{second_lang}.txt"
    while main_execute:
        time_start = time()
        if isEmpty(first_path) or isEmpty(second_path):
            print("Done!")
            exit()

        first_dump_sent, second_dump_sent, cmds = [], [], []
        with open(first_path, "r") as first_file:
            with open(second_path, "r") as second_file:
                saveIN, saveOU = first_file.read().splitlines(
                    True
                ), second_file.read().splitlines(True)
                for e in addSentPool(
                    [
                        InputSent(saveIN[idx], saveOU[idx])
                        for idx in range(
                            num_sent if len(saveIN) > num_sent else len(saveIN)
                        )
                    ]
                ):
                    if e[0] != "" and e[1] != "":
                        first_dump_sent.append(e[0]), second_dump_sent.append(e[1])
                    cmds.extend(i for i in e[2] if i)
                    false_count += -false_count if e[3] else 1
                    if false_count > false_allow and main_execute:
                        printError(
                            "mainModule",
                            Exception("Too many fatal translation!"),
                            False,
                        )
                        main_execute = False
        createOBJPool(cmds, sql_connection)

        with open(f"./data/{first_lang}.dump", "a") as f:
            for sent in first_dump_sent:
                f.write(f"{sent}\n")
        with open(f"./data/{second_lang}.dump", "a") as f:
            for sent in second_dump_sent:
                f.write(f"{sent}\n")

        if main_execute:
            with open(first_path, "w") as file:
                file.writelines(saveIN[num_sent:])
            with open(second_path, "w") as file:
                file.writelines(saveOU[num_sent:])

        saveDictionary(first_dictionary_path, first_dictionary)
        saveDictionary(second_dictionary_path, second_dictionary)
        print(f"\t\t(mainModule) time consume: {(time()-time_start):0,.2f}")
