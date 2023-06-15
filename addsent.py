import os, yaml, sqlite3, requests
from difflib import SequenceMatcher
from deep_translator import GoogleTranslator, MyMemoryTranslator
from symspellpy import SymSpell, Verbosity

with open('config.yml', "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)
target = cfg['v2en']['target']
lang_source = target[:2]
lang_target = target[-2:]
"""
input_path = './data/{}.txt.temp'.format(target[:2])
output_path = './data/{}.txt.temp'.format(target[-2:])
"""
accecpt_percentage = 0.65
is_auto = False
table_name = "Translation"

def convert(x):
    x = x.replace(".", " . ").replace(",", " , ").replace("(", " ( ")
    x = x.replace(")", " ) ").replace("\"", " \" ").replace(":", " : ")
    return x.lower().replace("  ", " ").replace("  ", " ")

def cleanScreen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def diffratio(x, y):
    return SequenceMatcher(None, x, y).ratio()

def gtrans(x, source, target):
    return GoogleTranslator(source=source, target=target).translate(x)

def dtrans(x, source, target):
    return MyMemoryTranslator(source=source, target=target).translate(x)

def createSQLColumn(conn, col_name, col_type, col_status="NOT NULL", col_value="N/A"):
    try:
        conn.cursor().execute("""
            ALTER TABLE {}
            ADD {} {} {} DEFAULT {}
        """.format(table_name, col_name, col_type, col_status, col_value))
    except Exception as e:
        printError('createSQLColumn', e)

def printError(text, error):
    print("---------------------\n\tExpectation while {}\n\tError type: {}\n \--------------------- \
          \n\n{}".format(text, type(error), error))
    exit(0)

def createSQLtable(connection):
    sql_create_table = """CREATE TABLE IF NOT EXISTS {} (
                            Source LONGTEXT NOT NULL,
                            Target LONGTEXT NOT NULL,
                            Verify BOOL NOT NULL
                        );""".format(table_name)
    try:
        connection.cursor().execute(sql_create_table)
        connection.commit()
    except Exception as e:
        printError("createSQLtabe", e)

def askUserStr(name_value):
    answer = input("\t{} >> ".format(name_value))
    return str(answer)

def askUserInt(name_value):
    answer = input("\t{} >> ".format(name_value))
    return int(answer)

def createOBJ(conn, sql, obj):
    try:
        conn.cursor().execute(sql, obj)
        conn.commit()
    except sqlite3.OperationalError as e:
        if str(e).find("no column")!=-1:
            createSQLColumn(conn, str(e).split()[-1], askUserStr('col_type').upper(), \
                            askUserStr('col_status').upper(), str(askUserInt('col_value')))
            createOBJ(conn, sql, obj)
    except Exception as e:
        printError("createOBJ", e)

def getSQLCursor(path):
    try:
        sqliteConnection = sqlite3.connect(path)
        print("Database created and Successfully Connected to SQLite")
    except sqlite3.Error as error:
        printError("getSQLCursor", error)
    return sqliteConnection

def downloadDictionary(*args):
    for target in args:
        if os.path.exists('./cache/{}.dic'.format(target)): continue
        open('./cache/{}.dic'.format(target), 'wb').write(requests.get(" \
            https://raw.githubusercontent.com/wooorm/dictionaries/main/dictionaries/{}/index.dic".format(target)).content)

def checkSpelling(text, dictionary):
    try:
        words = text.split(); outstr = ""
        for word in words:
            if word.isalpha():
                outstr+=dictionary.lookup(word, Verbosity.TOP, max_edit_distance=2)[0].term+' '
            else: outstr+=word+' '
        return outstr
    except IndexError:
        is_add = input("\tAdd {} to dictionary? (Y/n) ".format(word))
        if is_add.lower() == 'y' or is_add == '':
            dictionary.words[word]=1
            return checkSpelling(text, dictionary)
    except Exception as e:
        printError('checkSpelling', e)

if __name__ == '__main__':
    sql_connection = getSQLCursor(cfg['sqlite']['path'])
    createSQLtable(sql_connection)
    downloadDictionary(lang_source, lang_target)

    first_dictionary_path = './cache/{}.dic'.format(lang_source)
    second_dictionary_path = './cache/{}.dic'.format(lang_target)
    first_dictionary = SymSpell(2, 18, 1); second_dictionary = SymSpell(2, 18, 1)
    first_dictionary.create_dictionary(first_dictionary_path)
    second_dictionary.create_dictionary(second_dictionary_path)
    first_input_path = "./data/train.{}".format(lang_source)
    first_input_dump = open('./data/dump.{}'.format(lang_source), "a"); 
    second_input_path = "./data/train.{}".format(lang_target)
    second_input_dump = open('./data/dump.{}'.format(lang_target), "a")
    while 1:
        is_error = False; is_agree = '!'; add_gtrans = False; add_dtrans = False
        first_input_file = open(first_input_path, "r")
        second_input_file = open(second_input_path, "r")
        first_input_sent = convert(first_input_file.readline().replace('\n', ''))
        second_input_sent = convert(second_input_file.readline().replace('\n', ''))
        if not first_input_sent or not second_input_sent:
            break
        if (first_input_sent.find('&') != -1 or second_input_sent.find('&') != -1): is_error = True
        else:
            first_input_sent = checkSpelling(first_input_sent, first_dictionary)
            second_input_sent = checkSpelling(second_input_sent, second_dictionary)

            first_input_gtrans = checkSpelling(convert(gtrans(first_input_sent, lang_source, lang_target)), second_dictionary)
            second_input_gtrans = checkSpelling(convert(gtrans(second_input_sent, lang_target, lang_source)), first_dictionary)
            first_input_dtrans = checkSpelling(convert(dtrans(first_input_sent, lang_source, lang_target)), second_dictionary)
            second_input_dtrans = checkSpelling(convert(dtrans(second_input_sent, lang_target, lang_source)), first_dictionary)

            fir_to_sec_gratio = diffratio(first_input_sent, second_input_gtrans) 
            sec_to_fir_gratio = diffratio(second_input_sent, first_input_gtrans)
            fir_to_sec_dratio = diffratio(first_input_sent, second_input_dtrans)
            sec_to_fir_dratio = diffratio(second_input_sent, first_input_dtrans)
            if fir_to_sec_gratio > accecpt_percentage or \
                sec_to_fir_gratio > accecpt_percentage: 
                is_agree = ''; add_gtrans = True
            if fir_to_sec_dratio > accecpt_percentage or \
                sec_to_fir_dratio > accecpt_percentage:
                is_agree = ''; add_dtrans = True
            
            if not add_dtrans and not add_gtrans:
                first_input_trans = first_input_gtrans
                second_input_trans = second_input_gtrans
                fir_to_sec_ratio = fir_to_sec_gratio
                sec_to_fir_ratio = sec_to_fir_gratio
                if (abs(fir_to_sec_gratio-sec_to_fir_gratio) < abs(fir_to_sec_dratio-sec_to_fir_dratio)):
                    first_input_trans = first_input_dtrans
                    second_input_trans = second_input_dtrans
                    fir_to_sec_ratio = fir_to_sec_dratio
                    sec_to_fir_ratio = sec_to_fir_dratio
                cleanScreen()
                print("\t{} input (acc: {})\n\t\t- {}\n\t\t- {}\n"\
                        .format(lang_source, fir_to_sec_ratio, first_input_sent, second_input_trans))
                print("\t{} input (acc: {})\n\t\t- {}\n\t\t- {}\n"\
                        .format(lang_target, sec_to_fir_ratio, second_input_sent, first_input_trans))
                is_agree = input("\tAdd to database? (Y/n) ")
            elif not add_dtrans:
                cleanScreen()
                print("\t{} input (acc: {})\n\t\t- {}\n\t\t- {}\n"\
                        .format(lang_source, fir_to_sec_dratio, first_input_sent, second_input_dtrans))
                print("\t{} input (acc: {})\n\t\t- {}\n\t\t- {}\n"\
                        .format(lang_target, sec_to_fir_dratio, second_input_sent, first_input_dtrans))
                is_add = input("\tAdd to database? (Y/n) ")
                add_dtrans = is_add.lower() == 'y' or is_add == ''
            elif not add_gtrans:
                cleanScreen()
                print("\t{} input (acc: {})\n\t\t- {}\n\t\t- {}\n"\
                        .format(lang_source, fir_to_sec_gratio, first_input_sent, second_input_gtrans))
                print("\t{} input (acc: {})\n\t\t- {}\n\t\t- {}\n"\
                        .format(lang_target, sec_to_fir_gratio, second_input_sent, first_input_gtrans))
                is_add = input("\tAdd to database? (Y/n) ")
                add_gtrans = is_add.lower() == 'y' or is_add == ''
        if (is_agree.lower() == 'y' or is_agree == '') and not is_error:
            createOBJ(sql_connection, """
                INSERT INTO {}(Source, Target, Verify)
                VALUES(?,?,?)
            """.format(table_name), (first_input_sent, second_input_sent, 1))
            if add_dtrans:
                createOBJ(sql_connection, """
                    INSERT INTO {}(Source, Target, Verify)
                    VALUES(?,?,?)
                """.format(table_name), (first_input_sent, first_input_dtrans, 1))
                createOBJ(sql_connection, """
                    INSERT INTO {}(Source, Target, Verify)
                    VALUES(?,?,?)
                """.format(table_name), (second_input_dtrans, second_input_sent, 1))
            if add_gtrans:
                createOBJ(sql_connection, """
                    INSERT INTO {}(Source, Target, Verify)
                    VALUES(?,?,?)
                """.format(table_name), (first_input_sent, first_input_gtrans, 1))
                createOBJ(sql_connection, """
                    INSERT INTO {}(Source, Target, Verify)
                    VALUES(?,?,?)
                """.format(table_name), (second_input_gtrans, second_input_sent, 1))
            print(first_input_sent, second_input_sent)
        elif (is_agree == 'exit'): break
        else:
            first_input_dump.write("\n{}".format(convert(first_input_sent)))
            second_input_dump.write("\n{}".format(convert(second_input_sent)))
        saveIN = first_input_file.read().splitlines(True)
        saveOU = second_input_file.read().splitlines(True)
        first_input_file.close(); second_input_file.close()
        with open(first_input_path, "w") as file: file.writelines(saveIN[1:])
        with open(second_input_path, "w") as file: file.writelines(saveOU[1:])
    first_input_dump.close(); second_input_dump.close()
    open(first_dictionary_path, 'w').close()
    with open(first_dictionary_path, "w") as f: 
        f.writelines(word.lower()+'\n' for word in first_dictionary.words.keys())
    open(second_dictionary_path, 'w').close()
    with open(second_dictionary_path, "w") as f: 
        f.writelines(word.lower()+'\n' for word in second_dictionary.words.keys())