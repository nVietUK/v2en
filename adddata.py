import os, yaml, sqlite3
from difflib import SequenceMatcher
from deep_translator import GoogleTranslator

with open('config.yml', "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)
target = cfg['v2en']['target']
"""
input_path = './data/{}.txt.temp'.format(target[:2])
output_path = './data/{}.txt.temp'.format(target[-2:])
"""
accecpt_percentage = 0.8
is_auto = False
table_name = "Translation"

def convert(x):
    x = x.replace(".", " . ").replace(",", " , ").replace("(", " ( ")
    x = x.replace(")", " ) ").replace("\"", " \" ").replace(":", " : ")
    return x

def cleanScreen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def diffratio(x, y):
    return SequenceMatcher(None, x, y).ratio()

def gtrans(x, target):
    return GoogleTranslator(target=target).translate(x)

def createSQLColumn(conn, col_name, col_type, col_status="NOT NULL", col_value="N/A"):
    try:
        conn.cursor().execute("""
            ALTER TABLE {}
            ADD {} {} {} DEFAULT {}
        """.format(table_name, col_name, col_type, col_status, col_value))
    except Exception as e:
        printError('createSQLColumn', e)

def printError(text, error):
    print("---------------------\n\tExpectation while {}\n\t\tError type: {}\n \
          ---------------------\n\n{}".format(text, type(error), error))
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
            createSQLColumn(conn, str(e).split()[-1], askUserStr('col_type').upper(), askUserStr('col_status').upper(), str(askUserInt('col_value')))
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

if __name__ == '__main__':
    sql_connection = getSQLCursor(cfg['sqlite']['path'])
    createSQLtable(sql_connection)

    first_input_path = "./data/train.{}".format(target[:2])
    first_input_dump = open('./data/dump.{}'.format(target[:2]), "a"); 
    second_input_path = "./data/train.{}".format(target[-2:])
    second_input_dump = open('./data/dump.{}'.format(target[-2:]), "a")
    while 1:
        cleanScreen()
        is_error = False
        is_agree = '!'
        first_input_file = open(first_input_path, "r")
        first_input_sent = first_input_file.readline().replace('\n', '')
        first_input_gtrans = gtrans(first_input_sent, target[-2:])
        second_input_file = open(second_input_path, "r")
        second_input_sent = second_input_file.readline().replace('\n', '')
        second_input_gtrans = gtrans(second_input_sent, target[:2]); 
        fir_to_sec_gratio = diffratio(first_input_sent, second_input_gtrans) 
        sec_to_fir_gratio = diffratio(second_input_sent, first_input_gtrans)
        if not first_input_sent or not second_input_sent:
            break
        if (first_input_sent.find('&') != -1 or second_input_sent.find('&') != -1): is_error = True
        elif fir_to_sec_gratio > accecpt_percentage or is_auto \
            or sec_to_fir_gratio > accecpt_percentage: is_agree = ''
        else:
            print("\t{} input (acc: {})\n\t\t- {}\n\t\t- {}\n"\
                    .format(target[:2], diffratio(first_input_sent, second_input_gtrans), first_input_sent, second_input_gtrans))
            print("\t{} input (acc: {})\n\t\t- {}\n\t\t- {}\n"\
                    .format(target[-2:], diffratio(second_input_sent, first_input_gtrans), second_input_sent, first_input_gtrans))
            is_agree = input("\tAdd to database? (Y/n)")
        if (is_agree.lower() == 'y' or is_agree == '') and not is_error:
            createOBJ(sql_connection, """
                INSERT INTO {}(Source, Target, Verify)
                VALUES(?,?,?)
            """.format(table_name), (first_input_sent, second_input_sent, 1))
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