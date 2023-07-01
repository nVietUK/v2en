import sqlite3, v2enlib.utils as utils


def createSQLtable(connection, table_name):
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
        utils.printError(createSQLtable.__name__, e, False)


def createOBJ(sql, obj, conn):
    try:
        if obj[0] and obj[1]:
            conn.cursor().execute(sql, obj)
    except Exception as e:
        utils.printError(createOBJ.__name__, e, False)


def createOBJPool(cmds, conn):
    for cmd in cmds:
        createOBJ(*cmd, conn=conn)


def getSQLCursor(path) -> sqlite3.Connection:  # type: ignore
    try:
        sqliteConnection = sqlite3.connect(path)
        print("Database created and Successfully Connected to SQLite")
        return sqliteConnection
    except Exception as e:
        utils.printError(getSQLCursor.__name__, e, True)


def getSQL(conn, request):
    cursor = conn.cursor()
    cursor.execute(request)
    return cursor.fetchall()
