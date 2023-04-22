from sqlite3 import Error
import sqlite3

def create_connection(db_file):
    conn = None;
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn):
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS calls (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        phone_number TEXT NOT NULL,
                        conversation_history TEXT NOT NULL,
                        conversation_vector BLOB NOT NULL
                     )''')
    except sqlite3.Error as e:
        print(e)

def update_or_insert_call(conn, phone_number, conversation_history, conversation_vector):
    sql_update = """UPDATE calls SET conversation_history = ?, conversation_vector = ? WHERE phone_number = ?;"""
    sql_insert = """INSERT INTO calls(phone_number, conversation_history, conversation_vector) VALUES(?, ?, ?);"""

    cur = conn.cursor()

    # Update the conversation history if the phone number exists
    cur.execute(sql_update, (conversation_history, conversation_vector, phone_number))
    conn.commit()

    # If no rows were affected, insert a new call entry
    if cur.rowcount == 0:
        cur.execute(sql_insert, (phone_number, conversation_history, conversation_vector))
        conn.commit()

    return cur.lastrowid

def delete_all_calls(conn):
    sql = "DELETE FROM calls;"
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()

