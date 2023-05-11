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
                        phone_number TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        conversation_history TEXT NOT NULL,
                        conversation_vector BLOB NOT NULL,
                        communication_type TEXT NOT NULL CHECK (communication_type IN ('call', 'sms')),
                        PRIMARY KEY (phone_number, timestamp)
                     )''')
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")

def update_or_insert_call(conn, phone_number, timestamp, conversation_history, conversation_vector, communication_type):
    sql_update = """UPDATE calls SET conversation_history = ?, conversation_vector = ?, communication_type = ? WHERE phone_number = ? AND timestamp = ?;"""
    sql_insert = """INSERT INTO calls(phone_number, timestamp, conversation_history, conversation_vector, communication_type) VALUES(?, ?, ?, ?, ?);"""

    cur = conn.cursor()

    # Update the conversation history if the phone number and timestamp exist
    cur.execute(sql_update, (conversation_history, conversation_vector, communication_type, phone_number, timestamp))
    conn.commit()

    # If no rows were affected, insert a new call entry
    if cur.rowcount == 0:
        cur.execute(sql_insert, (phone_number, timestamp, conversation_history, conversation_vector, communication_type))
        conn.commit()

    return (phone_number, timestamp)

def get_conversation_data(conn, phone_number):
    sql = """SELECT conversation_history, conversation_vector, communication_type FROM calls WHERE phone_number = ? ORDER BY timestamp DESC LIMIT 1;"""
    cur = conn.cursor()
    cur.execute(sql, (phone_number,))
    row = cur.fetchone()
    if row:
        return row[0], row[1], row[2]
    else:
        return None, None, None

def delete_all_calls(conn):
    sql = "DELETE FROM calls;"
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()

