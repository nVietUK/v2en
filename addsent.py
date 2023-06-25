import yaml, signal, time, gc
from multiprocessing.pool import Pool

with open("config.yml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)
target = cfg["v2en"]["target"]
num_sent = cfg["v2en"]["num_sent"]
first_lang = target[:2]
second_lang = target[-2:]
table_name = cfg["sqlite"]["table_name"]
first_dictionary_path = f"./cache/{first_lang}.dic"
second_dictionary_path = f"./cache/{second_lang}.dic"
main_execute = True
false_allow = num_sent / 2 * 3


from v2enlib import (
    printError,
    loadDictionary,
    checkLangFile,
    getSQLCursor,
    createSQLtable,
    isEmpty,
    saveDictionary,
    addSentExecutor,
    createOBJPool,
    playSound,
    funcPool,
    InputSent,
    logger,
)


def signalHandler(sig, frame):
    global main_execute
    if main_execute:
        logger.log(101, "\tStop program!")
        main_execute = False


if __name__ == "__main__":
    checkLangFile(first_lang, second_lang)
    first_dictionary = loadDictionary(first_dictionary_path)
    second_dictionary = loadDictionary(second_dictionary_path)
    signal.signal(signal.SIGINT, signalHandler)
    sql_connection = getSQLCursor(cfg["sqlite"]["path"])
    createSQLtable(sql_connection, table_name)
    false_count, first_dump_sents, second_dump_sents = 0, [], []

    first_path, second_path = f"./data/{first_lang}.txt", f"./data/{second_lang}.txt"
    with open(first_path, "r") as first_file:
        with open(second_path, "r") as second_file:
            saveIN, saveOU = first_file.read().splitlines(
                True
            ), second_file.read().splitlines(True)
    playSound(["E3", "G3", "C4", "D4"], [200, 200, 500, 500])
    while main_execute:
        time_start = time.time()
        if isEmpty(first_path) or isEmpty(second_path):
            logger.log(101, "Done!")
            break

        first_dump_sent, second_dump_sent, cmds = [], [], []

        for e in funcPool(
            addSentExecutor,
            [
                [InputSent(saveIN[idx], saveOU[idx]), first_dictionary, second_dictionary]
                for idx in range(num_sent if len(saveIN) > num_sent else len(saveIN))
            ],
            Pool,
            False,
            strictOrder=True,
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
        #                main_execute = False
        createOBJPool(cmds, sql_connection)

        if main_execute:
            second_dump_sents += second_dump_sent
            first_dump_sents += first_dump_sent
            saveOU = saveOU[num_sent:]
            saveIN = saveIN[num_sent:]

        saveDictionary(first_dictionary_path, first_dictionary)
        saveDictionary(second_dictionary_path, second_dictionary)
        logger.log(
            101,
            f"\t\t(mainModule) time consume: {(time.time()-time_start):0,.2f}",
        )
        del cmds, first_dump_sent, second_dump_sent
        gc.collect()
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
playSound(["C7", "A#6", "G6", "E6"], [200, 150, 100, 50])
