import sqlite3


# debug def
def printError(text, error, debug, is_exit=True, avoid_debug=False):
    if not debug and not avoid_debug:
        return
    print(
        f"{'_'*50}\n\tExpectation while {text}\n\tError type: {type(error)}\n\t{error}\n{chr(8254)*50}"
    )
    if is_exit:
        exit(0)


def printInfo(name, pid, debug):
    if not debug:
        return
    print(f"Dive into {name} with pid id: {pid}")


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


# sqlite3 defs
def createSQLColumn(conn, col_name, col_type, table_name, debug, col_status="NOT NULL", col_value="N/A"):
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
        printError(createSQLColumn.__name__, e, debug)


def createSQLtable(connection, table_name, debug):
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
        printError(createSQLtable.__name__, e, debug)


def createOBJ(conn, sql, obj, debug):
    try:
        if obj[0] and obj[1]:
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
            createOBJ(conn, sql, obj, debug)
    except Exception as e:
        printError(createOBJ.__name__, e, debug)


def createOBJExecute(cmd):
    return createOBJ(*cmd)


def createOBJPool(cmds, con):
    for cmd in cmds:
        createOBJExecute(cmd)
    con.commit()


def getSQLCursor(path) -> sqlite3.Connection:
    try:
        sqliteConnection = sqlite3.connect(path)
        print("Database created and Successfully Connected to SQLite")
    except sqlite3.Error as error:
        printError(getSQLCursor.__name__, error, True, True)
    except Exception as e:
        printError(getSQLCursor.__name__, e, True, True)
    return sqliteConnection

def getSQL(conn, request):
    cursor = conn.cursor()
    cursor.execute(request)
    return cursor.fetchall()
