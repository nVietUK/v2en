import contextlib
import yaml, signal, time, gc, os, argparse
from multiprocessing import Process
from multiprocessing.pool import Pool
from v2enlib import utils, language, SQL, const

try:
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.safe_load(ymlfile)
    target = cfg["v2en"]["target"]
    num_sent = cfg["v2en"]["num_sent"]
    allow_GUI = cfg["v2en"]["allow"]["GUI"]
    first_lang = target[:2]
    second_lang = target[-2:]
    table_name = cfg["sqlite"]["table_name"]
    safe_execute = cfg["v2en"]["safe_execute"]
    allowFalseTranslation = cfg["v2en"]["allow"]["FalseTranslation"]
    if allow_GUI:
        import tkinter as tk
except Exception as e:
    utils.printError("importing config", e, True)
    exit(0)
first_dictionary_path, second_dictionary_path = (
    f"./cache/{first_lang}.dic",
    f"./cache/{second_lang}.dic",
)
first_path, second_path = f"./data/{first_lang}.txt", f"./data/{second_lang}.txt"
main_execute = True
false_allow = num_sent / 2 * 3


def signalHandler(sig, handle):
    global main_execute
    if main_execute:
        print("\tStop program!")
        main_execute = False


def on_press(key):
    global main_execute
    with contextlib.suppress(AttributeError):
        if key.char == "z" and main_execute:
            os.kill(os.getpid(), signal.SIGINT)


class ExitButton:
    def __init__(self, func, **kwargs):
        if allow_GUI:
            self.root = tk.Tk()
            self.root.title("My App")
            self.button = tk.Button(self.root, text="Turn Off", command=self.turn_off)
            self.button.pack()
            self.thread = Process(
                target=self.run_loop, kwargs={"func": func, "kwargs": kwargs}
            )
            self.thread.start()
            self.root.mainloop()
            self.thread.join()
        else:
            func(**kwargs)

    def run_loop(self, func, kwargs):
        func(**kwargs)

        if allow_GUI and self.root.winfo_exists():
            self.root.destroy()

    def turn_off(self):
        self.root.destroy()
        global main_execute
        if main_execute:
            os.kill(os.getpid(), signal.SIGINT)


def saveFiles(
    sql_connection,
    saveIN,
    saveOU,
    first_dump_sents,
    second_dump_sents,
    first_dictionary_path,
    second_dictionary_path,
    first_dictionary,
    second_dictionary,
):
    sql_connection.commit()
    language.saveDictionary(first_dictionary_path, first_dictionary)
    language.saveDictionary(second_dictionary_path, second_dictionary)
    with open(first_path, "w") as file:
        file.writelines(saveIN)
    with open(second_path, "w") as file:
        file.writelines(saveOU)
    with open(f"./data/{first_lang}.dump", "a") as f:
        for sent in first_dump_sents:
            f.write(f"{sent}\n")
    with open(f"./data/{second_lang}.dump", "a") as f:
        for sent in second_dump_sents:
            f.write(f"{sent}\n")


def safeExecute(
    saveIN, saveOU, sql_connection, first_dictionary, second_dictionary, fargs
):
    false_count, first_dump_sents, second_dump_sents, exe_count = 0, [], [], 0
    global main_execute
    while main_execute:
        exe_count += 1
        time_start = time.time()
        if utils.emptyFile(first_path) or utils.emptyFile(second_path):
            print("Done!")
            break

        first_dump_sent, second_dump_sent, cmds, numberAddedTrans = [], [], [], 0

        for e in utils.functionPool(
            language.addSentExecutor,
            [
                [
                    language.InputSent(saveIN[idx], saveOU[idx]),
                    first_dictionary,
                    second_dictionary,
                ]
                for idx in range(
                    num_sent
                    if min(len(saveIN), len(saveOU)) > num_sent
                    else min(len(saveIN), len(saveOU))
                )
            ],
            Pool,
            strictOrder=True,
            poolName="addSent",
        ):
            if e[0] != "" and e[1] != "":
                first_dump_sent.append(e[0])
                second_dump_sent.append(e[1])
            cmds.extend(i for i in e[2] if i)
            false_count += -false_count if e[3] else 1
            numberAddedTrans += e[4]
            if false_count > false_allow and main_execute and not allowFalseTranslation:
                utils.printError("mainModule", Exception("Too many fatal translation!"), True)
                main_execute = False
        SQL.createOBJPool(cmds, sql_connection)

        second_dump_sents += second_dump_sent
        first_dump_sents += first_dump_sent
        saveOU = saveOU[num_sent:]
        saveIN = saveIN[num_sent:]

        print(
            f"\t\t(mainModule) time consume: {(time.time()-time_start):0,.2f} ({numberAddedTrans})",
        )
        del cmds, first_dump_sent, second_dump_sent
        gc.collect()
        if exe_count == fargs.amount_exe:
            break
    saveFiles(
        sql_connection,
        saveIN,
        saveOU,
        first_dump_sents,
        second_dump_sents,
        first_dictionary_path,
        second_dictionary_path,
        first_dictionary,
        second_dictionary,
    )


def unsafeExecute(saveIN, saveOU, sql_connection, first_dictionary, second_dictionary):
    false_count, first_dump_sents, second_dump_sents = 0, [], []
    global main_execute


def main(fargs):
    utils.playNotes(*const.sound_tracks["macos_startup"])
    if not fargs.ci_cd:
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
    language.checkLangFile(first_lang, second_lang)
    first_dictionary = language.loadDictionary(first_dictionary_path)
    second_dictionary = language.loadDictionary(second_dictionary_path)
    signal.signal(signal.SIGINT, signalHandler)
    sql_connection = SQL.getSQLCursor(cfg["sqlite"]["path"])
    SQL.createSQLtable(sql_connection, table_name)

    with open(first_path, "r") as first_file:
        with open(second_path, "r") as second_file:
            saveIN, saveOU = first_file.read().splitlines(
                True
            ), second_file.read().splitlines(True)
    if safe_execute:
        ExitButton(
            safeExecute,
            saveIN=saveIN,
            saveOU=saveOU,
            sql_connection=sql_connection,
            first_dictionary=first_dictionary,
            second_dictionary=second_dictionary,
            fargs=fargs,
        )

    utils.playNotes(*const.sound_tracks["windows7_shutdown"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--amount-exe",
        type=int,
        help="enter amount of execute to translate a number of sentence and add to .db",
        nargs="?",
        default=0,
    )
    parser.add_argument(
        '--ci_cd',
        type=bool,
        help='run addsent.py on ci/cd environment',
        nargs='?',
        default=False,
        const=True
    )
    parser.add_argument(
        '--disable-thread',
        type=bool,
        help='disable thread feature for addsent.py',
        nargs='?',
        default=False,
        const=True
    )
    fargs = parser.parse_args()
    if fargs.disable_thread:
        const.thread_alow = False
    if not fargs.ci_cd:
        from pynput import keyboard
    else:
        const.disableTQDM = True
    main(fargs)
