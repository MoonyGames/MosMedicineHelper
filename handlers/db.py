import sqlite3

conn = sqlite3.connect('database/db.db', check_same_thread=False)
cursor = conn.cursor()


def db_save_val(user_id: int, user_name: str, user_surname: str, user_patronymic: str, policy_number: int):
    global conn
    global cursor

    cursor.execute('INSERT INTO patients (user_id, user_name, user_surname, user_patronymic, policy_number) '
                   'VALUES (?, ?, ?, ?, ?)',
                   (user_id, user_name, user_surname, user_patronymic, policy_number))
    conn.commit()


def db_find_val(id: int, current_user: dict):
    global conn
    global cursor

    cursor.execute("SELECT * FROM patients WHERE user_id = '{}'".format(id))
    row = cursor.fetchone()

    if row is not None:
        current_user['user_id'] = row[1]
        current_user['name'] = row[2]
        current_user['surname'] = row[3]
        current_user['patronymic'] = row[4]
        current_user['policy_number'] = row[5]

        conn.close()

        return True
    else:
        conn.close()

        return False


