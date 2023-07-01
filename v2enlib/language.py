import string, httpx, string, gc, contextlib, os
import deep_translator.exceptions, langcodes, requests
from translators import server as TransServer
from v2enlib import const, utils
from tabulate import tabulate
from functools import lru_cache


# * classes
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
        self.isAdd = accurate > const.accept_percentage

    def isValid(self) -> bool:
        return bool(self.first and self.second)

    def SQLFormat(self) -> tuple:
        return (self.first, self.second, 1 if self.isAdd else 0)


# * executors
def transIntoListExecutor(cmd):
    return transIntoList(*cmd)


def addSentExecutor(cmd):
    return addSent(*cmd)


def checkSpellingExecutor(cmd):
    return checkSpelling(*cmd)


# * translate def
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
        utils.printError(deepTransGoogle.__name__, e, False)
        return ""


@utils.measureFunction
def translatorsTransSub(cmd: list):
    function_timeout = cmd[1].get("function_timeout", None)
    trans_name = utils.getKeyByValue(const.trans_dict, cmd[0])[0]

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
                ou = utils.functionTimeout(function_timeout, cmd[0], kwargs=cmd[1])
            except TransServer.TranslatorError as e:
                with contextlib.suppress(*allow_error):
                    if tcmd := _extracted_from_translatorsTrans_13(cmd[1].values(), e):
                        ou = utils.functionTimeout(
                            function_timeout / 2, cmd[0], args=tcmd
                        )
                    else:
                        ou = utils.functionTimeout(
                            function_timeout, deepTransGoogle, kwargs=cmd[1]
                        )
            except allow_error:
                ou = utils.functionTimeout(
                    function_timeout / 2, deepTransGoogle, kwargs=cmd[1]
                )
            except Exception as e:
                utils.printError("translatorsTransSub", e, False)
        if function_timeout:
            cmd[1]["function_timeout"] = function_timeout
        return [ou, trans_name]

    return execute(cmd)


@utils.measureFunction
def translatorsTrans(cmd: list, trans_timeout) -> list:
    return utils.argsPool(
        const.trans_dict.values(),  # type: ignore
        utils.ThreadPool,
        translatorsTransSub,
        alwaysThread=True,
        poolName="translationPool",
        query_text=cmd[0],
        from_language=cmd[1],
        to_language=cmd[2],
        function_timeout=trans_timeout,
    )


# TODO Rename this here and in `translatorsTrans`
@utils.measureFunction
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
        utils.printError("change format language", e, False)
    return []


@utils.measureFunction
def transIntoList(sent, source_lang, target_lang, target_dictionary):
    return utils.functionPool(
        checkSpellingExecutor,
        [
            [convert(e[0]), target_dictionary, target_lang, e[1]]
            for e in translatorsTrans(
                [sent, source_lang, target_lang], const.trans_timeout
            )
        ],
        utils.ThreadPool,
        alwaysThread=True,
        poolName="transCheckSpelling",
    )


# * language utils
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
        utils.printError(
            f"add word for {lang}",
            Exception(f"{word} isn't existed on Wikitionary!"),
            False,
        )
    except Exception as e:
        utils.printError(checkSpelling.__name__, e, False)
    return ["", ""] if tname else ""


@utils.measureFunction
def addSent(input_sent: InputSent, first_dictionary, second_dictionary):
    is_agree, first_dump_sent, second_dump_sent, cmds, trans_data, print_data = (
        False,
        "",
        "",
        [],
        [],
        ["Data set", input_sent.first, input_sent.second, "N/A"],
    )
    input_sent.first, input_sent.second = utils.functionPool(
        checkSpellingExecutor,
        [
            [
                convert(input_sent.first.replace("\n", "")),
                first_dictionary,
                const.first_lang,
            ],
            [
                convert(input_sent.second.replace("\n", "")),
                second_dictionary,
                const.second_lang,
            ],
        ],
        utils.ThreadPool,
        strictOrder=True,
        alwaysThread=True,
        poolName="sentsCheckSpelling",
    )
    if input_sent.isValid():
        is_error, trans_data = True, []
        for first_tran, second_tran in zip(
            *utils.functionPool(
                transIntoListExecutor,
                [
                    [
                        input_sent.first,
                        const.first_lang,
                        const.second_lang,
                        second_dictionary,
                    ],
                    [
                        input_sent.second,
                        const.second_lang,
                        const.first_lang,
                        first_dictionary,
                    ],
                ],
                utils.ThreadPool,
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
                        utils.differentRatio(input_sent.second, first_tran[0]),
                    )
                )
            if second_tran[0]:
                trans_data.append(
                    InputSent(
                        second_tran[0],
                        input_sent.second,
                        second_tran[1],
                        utils.differentRatio(input_sent.first, second_tran[0]),
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
                    table_command.format(const.table_name),
                    (input_sent.first, input_sent.second, 1),
                ]
            ] + [
                [
                    table_command.format(const.table_name),
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
        if len(print_data) < 10:
            utils.logging.info(
                tabulate(
                    tabular_data=print_data,
                    headers=["From", "Source", "Target", "Accuracy?"],
                    tablefmt="fancy_grid",
                    showindex="always",
                    maxcolwidths=[None, None, 45, 45, 7],
                    floatfmt=(".2f" * 5),
                ),
            )
    del trans_data
    gc.collect()
    return first_dump_sent, second_dump_sent, cmds, is_agree, len(print_data) - 1


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
        utils.printError(convert.__name__, e, False)
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


def loadDictionary(path) -> list:
    try:
        if not utils.emptyFile(path):
            with open(path, "r") as f:
                return [word.rstrip("\n") for word in f.read().splitlines(True)]
    except Exception as e:
        utils.printError(loadDictionary.__name__, e, False)
    return []


def saveDictionary(path, dictionary):
    try:
        with open(path, "w") as f:
            for e in dictionary:
                f.write(e + "\n")
    except Exception as e:
        utils.printError("saveDictionary", e, False)


def checkLangFile(*args):
    for target in args:
        if os.path.exists(f"./cache/{target}.dic"):
            continue
        open(f"./cache/{target}.dic", "w").close()
