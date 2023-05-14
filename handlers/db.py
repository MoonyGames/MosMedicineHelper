import sqlite3

conn = sqlite3.connect('database/db.db', check_same_thread=False)
cursor = conn.cursor()


def get_row_count(table_name):
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]
    return row_count


def get_column_values(table_name, column_name):
    cursor.execute(f"SELECT {column_name} FROM {table_name}")
    values = cursor.fetchall()
    return [value[0] for value in values]


def db_save_val_patients(user_id: int, user_name: str, user_surname: str, user_patronymic: str, policy_number: int):
    global conn
    global cursor

    cursor.execute('INSERT INTO patients (user_id, user_name, user_surname, user_patronymic, policy_number) '
                   'VALUES (?, ?, ?, ?, ?)',
                   (user_id, user_name, user_surname, user_patronymic, policy_number))
    conn.commit()


def db_find_val_patients(id: int, current_user: dict):
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

        return True
    else:
        return False


def db_save_val_hospitals(hospital_name: str, hospital_address: str):
    global conn
    global cursor

    cursor.execute('INSERT INTO patients (hospital_name, hospital_address) '
                   'VALUES (?, ?)',
                   (hospital_name, hospital_address))
    conn.commit()


def db_find_val_hospital(hospital_name: str, current_hospital: dict):
    global conn
    global cursor

    cursor.execute("SELECT * FROM patients WHERE hospital_name = '{}'".format(hospital_name))
    row = cursor.fetchone()

    if row is not None:
        current_hospital['hospital_name'] = row[1]
        current_hospital['hospital_address'] = row[2]

        return True
    else:
        return False


def db_save_val_receipt_time(year: int, month: int, day: int, is_taken: int, hospital_name: str):
    global conn
    global cursor

    cursor.execute('INSERT INTO receipt_time (year, month, day, is_taken, hospital_name) '
                   'VALUES (?, ?, ?, ?, ?)',
                   (year, month, day, is_taken, hospital_name))
    conn.commit()


def db_find_val_receipt_time(receipt_hospital_name: str, current_receipt_time: dict):
    global conn
    global cursor

    cursor.execute("SELECT * FROM receipt_time WHERE hospital_name = '{}'".format(receipt_hospital_name))
    row = cursor.fetchone()

    if row is not None:
        current_receipt_time['year'] = row[1]
        current_receipt_time['month'] = row[2]
        current_receipt_time['day'] = row[3]
        current_receipt_time['is_taken'] = row[4]
        current_receipt_time['hospital_name'] = row[5]

        return True
    else:
        return False
