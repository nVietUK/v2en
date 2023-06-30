import contextlib, tkinter as tk
import yaml, signal, time, gc, os
from multiprocessing import Process
from multiprocessing.pool import Pool
from pynput import keyboard

with open("config.yml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)
target = cfg["v2en"]["target"]
num_sent = cfg["v2en"]["num_sent"]
allow_GUI = cfg["v2en"]["allow_GUI"]
first_lang = target[:2]
second_lang = target[-2:]
table_name = cfg["sqlite"]["table_name"]
safe_execute = cfg["v2en"]["safe_execute"]
allowFalseTranslation = cfg["v2en"]["allowFalseTranslation"]
first_dictionary_path, second_dictionary_path = (
    f"./cache/{first_lang}.dic",
    f"./cache/{second_lang}.dic",
)
first_path, second_path = f"./data/{first_lang}.txt", f"./data/{second_lang}.txt"
main_execute = True
false_allow = num_sent / 2 * 3


from v2enlib import (
    printError,
    loadDictionary,
    checkLangFile,
    getSQLCursor,
    createSQLtable,
    emptyFile,
    saveDictionary,
    addSentExecutor,
    createOBJPool,
    functionPool,
    playNotes,
    InputSent,
    sound_tracks,
)


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


def saveFiles(sql_connection, saveIN, saveOU, first_dump_sents, second_dump_sents):
    sql_connection.commit()
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


def safeExecute(saveIN, saveOU, sql_connection, first_dictionary, second_dictionary):
    false_count, first_dump_sents, second_dump_sents = 0, [], []
    global main_execute
    while main_execute:
        time_start = time.time()
        if emptyFile(first_path) or emptyFile(second_path):
            print("Done!")
            break

        first_dump_sent, second_dump_sent, cmds, numberAddedTrans = [], [], [], 0

        for e in functionPool(
            addSentExecutor,
            [
                [
                    InputSent(saveIN[idx], saveOU[idx]),
                    first_dictionary,
                    second_dictionary,
                ]
                for idx in range(num_sent if len(saveIN) > num_sent else len(saveIN))
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
                printError(
                    "mainModule",
                    Exception("Too many fatal translation!"),
                    False,
                )
                main_execute = False
        createOBJPool(cmds, sql_connection)

        second_dump_sents += second_dump_sent
        first_dump_sents += first_dump_sent
        saveOU = saveOU[num_sent:]
        saveIN = saveIN[num_sent:]

        saveDictionary(first_dictionary_path, first_dictionary)
        saveDictionary(second_dictionary_path, second_dictionary)
        print(
            f"\t\t(mainModule) time consume: {(time.time()-time_start):0,.2f} ({numberAddedTrans})",
        )
        del cmds, first_dump_sent, second_dump_sent
        gc.collect()
    saveFiles(sql_connection, saveIN, saveOU, first_dump_sents, second_dump_sents)


def unsafeExecute(saveIN, saveOU, sql_connection, first_dictionary, second_dictionary):
    false_count, first_dump_sents, second_dump_sents = 0, [], []
    global main_execute
    while main_execute:
        time_start = time.time()
        if emptyFile(first_path) or emptyFile(second_path):
            print("Done!")
            break

        first_dump_sent, second_dump_sent, cmds = [], [], []

        for e in functionPool(
            addSentExecutor,
            [
                [
                    InputSent(saveIN[idx], saveOU[idx]),
                    first_dictionary,
                    second_dictionary,
                ]
                for idx in range(num_sent if len(saveIN) > num_sent else len(saveIN))
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
            if false_count > false_allow and main_execute and not allowFalseTranslation:
                printError(
                    "mainModule",
                    Exception("Too many fatal translation!"),
                    False,
                )
                main_execute = False
        createOBJPool(cmds, sql_connection)

        second_dump_sents += second_dump_sent
        first_dump_sents += first_dump_sent
        saveOU = saveOU[num_sent:]
        saveIN = saveIN[num_sent:]

        saveDictionary(first_dictionary_path, first_dictionary)
        saveDictionary(second_dictionary_path, second_dictionary)
        print(
            f"\t\t(mainModule) time consume: {(time.time()-time_start):0,.2f}",
        )
        del cmds, first_dump_sent, second_dump_sent
        gc.collect()
    saveFiles(sql_connection, saveIN, saveOU, first_dump_sents, second_dump_sents)


def main():
    playNotes(*sound_tracks["macos_startup"])
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    checkLangFile(first_lang, second_lang)
    first_dictionary = loadDictionary(first_dictionary_path)
    second_dictionary = loadDictionary(second_dictionary_path)
    signal.signal(signal.SIGINT, signalHandler)
    sql_connection = getSQLCursor(cfg["sqlite"]["path"])
    createSQLtable(sql_connection, table_name)

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
        )

    playNotes(*sound_tracks["windows7_shutdown"])


if __name__ == "__main__":
    main()
