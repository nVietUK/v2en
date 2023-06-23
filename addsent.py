import contextlib, deep_translator.exceptions, langcodes
import yaml, string, translators.server, signal, execjs._exceptions, deep_translator, time
from translators.server import TranslatorsServer
from tabulate import tabulate
from multiprocessing.pool import ThreadPool


with open("config.yml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)
target = cfg["v2en"]["target"]
table_name = cfg["sqlite"]["table_name"]
first_lang = target[:2]
second_lang = target[-2:]
accept_percentage = cfg["v2en"]["accept_percentage"]
is_auto = True
first_dictionary_path = f"./cache/{first_lang}.dic"
second_dictionary_path = f"./cache/{second_lang}.dic"
main_execute = True
num_sent = 6
false_allow = 25
thread_alow = True
thread_limit = 0
trans_timeout = 8
translator = TranslatorsServer()

from v2enlib import (
    printError,
    measure,
    func_timeout,
    convert,
    isExistOnWiki,
    diffratio,
    loadDictionary,
    checkLangFile,
    getSQLCursor,
    createSQLtable,
    isEmpty,
    saveDictionary,
    createOBJPool,
    InputSent,
    logger,
)


# thread utils
def funcPool(func, cmds, isAllowThread=True):
    with contextlib.suppress(Exception, ValueError):
        if thread_alow and isAllowThread:
            with ThreadPool(
                min(len(cmds), thread_limit if thread_limit > 0 else len(cmds))
            ) as ex:
                return ex.map(func, cmds)
    return [func(cmd) for cmd in cmds]


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
def translatorsTrans(trans, cmd: list, trans_timeout, isDived: bool = False):
    try:
        return func_timeout(
            trans_timeout,
            trans,
            query_text=cmd[0],
            from_language=cmd[1],
            to_language=cmd[2],
            default_value="",
        )
    except translators.server.TranslatorError as e:
        if not isDived:
            return _extracted_from_translatorsTrans_13(cmd, e, trans, trans_timeout / 2)
    except (execjs._exceptions.RuntimeUnavailableError, TypeError, ValueError):
        pass
    except Exception as e:
        printError(translatorsTrans.__name__, e, False)
    return deepTransGoogle(*cmd)


# TODO Rename this here and in `translatorsTrans`
def _extracted_from_translatorsTrans_13(cmd, e, trans, trans_timeout):
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
        return translatorsTrans(trans, tcmd, trans_timeout, True) if execute else ""
    except IndexError:
        return ""


def translatorsTransExecutor(cmd, *args, **kwargs):
    return translatorsTrans(*cmd, *args, **kwargs)


def transIntoList(sent, source_lang, target_lang, target_dictionary):
    ou = funcPool(
        checkSpellingExecutor,
        [
            [convert(e), target_dictionary, target_lang]
            for e in funcPool(
                translatorsTransExecutor,
                [
                    [trans, [sent, source_lang, target_lang], trans_timeout]
                    for name, trans in translator.translators_dict.items()
                ],
            )
        ],
    )
    return list(zip(ou, translator.translators_dict.keys()))


@measure
def transIntoListExecutor(cmd):
    return transIntoList(*cmd)


# language utils
def checkSpelling(text: str, dictionary: list, lang: str) -> str:
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


def checkSpellingExecutor(cmd):
    return checkSpelling(*cmd)


@measure
def addSent(input_sent: InputSent):
    time_start = time.time()
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
    )
    if input_sent.isValid():
        is_error = True
        first_trans, second_trans = funcPool(
            transIntoListExecutor,
            [
                [input_sent.first, first_lang, second_lang, second_dictionary],
                [input_sent.second, second_lang, first_lang, first_dictionary],
            ],
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
                for e in trans_data
                if e.isAdd
            ]
        if is_error:
            first_dump_sent, second_dump_sent = input_sent.first, input_sent.second

        print_data = [["Data set", input_sent.first, input_sent.second, "N/A"]] + [
            [e.isFrom, e.first, e.second, e.accurate] for e in trans_data if e.isAdd
        ]
        logger.log(
            101,
            tabulate(
                tabular_data=print_data,
                headers=["From", "Source", "Target", "Accuracy?"],
                tablefmt="fancy_grid",
                showindex="always",
                maxcolwidths=[None, None, 75, 75, 10],
                floatfmt=(".2f" * 5),
            ),
        )
    print(f"\t({addSent.__name__}) time consume: {(time.time()-time_start):0,.2f}")
    return first_dump_sent, second_dump_sent, cmds, is_agree


def signalHandler(sig, frame):
    global main_execute
    logger.log(101, "\tStop program!")
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
    with open(first_path, "r") as first_file:
        with open(second_path, "r") as second_file:
            saveIN, saveOU = first_file.read().splitlines(
                True
            ), second_file.read().splitlines(True)
    while main_execute:
        time_start = time.time()
        if isEmpty(first_path) or isEmpty(second_path):
            logger.log(101, "Done!")
            exit()

        first_dump_sent, second_dump_sent, cmds = [], [], []

        for e in funcPool(
            addSent,
            [
                InputSent(saveIN[idx], saveOU[idx])
                for idx in range(num_sent if len(saveIN) > num_sent else len(saveIN))
            ],
        ):
            if e[0] != "" and e[1] != "":
                first_dump_sent.append(e[0])
                second_dump_sent.append(e[1])
            cmds.extend(i for i in e[2] if i)
            false_count += -false_count if e[3] else 1
            if false_count > false_allow and main_execute:
                printError(
                    "mainModule",
                    Exception("Too many fatal translation!"),
                    False,
                )
        subtime = time.time()
        createOBJPool(cmds)

        with open(f"./data/{first_lang}.dump", "a") as f:
            for sent in first_dump_sent:
                f.write(f"{sent}\n")
        with open(f"./data/{second_lang}.dump", "a") as f:
            for sent in second_dump_sent:
                f.write(f"{sent}\n")

        saveOU = saveOU[num_sent:]
        saveIN = saveIN[num_sent:]

        saveDictionary(first_dictionary_path, first_dictionary)
        saveDictionary(second_dictionary_path, second_dictionary)
        logger.log(
            101,
            f"\t\t(mainModule) time consume: {(time.time()-time_start):0,.2f}\n\t\t{time.time()-subtime}",
        )
    sql_connection.commit()
    with open(first_path, "w") as file:
        file.writelines(saveIN)
    with open(second_path, "w") as file:
        file.writelines(saveOU)
