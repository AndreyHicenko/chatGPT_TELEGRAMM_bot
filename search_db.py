import sqlite3
import datetime
import asyncio



def date_check(user_id):
    now = datetime.datetime.now().date()
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    res = cursor.execute('SELECT date_final FROM users WHERE user_id = ?', (user_id,)).fetchall()
    return res



#вызывать при нажатии на кнопку оформить подписку
def upddate_datebase(user_id, duration):
    now = datetime.datetime.now()
    date_beginning = now.date()
    date_final = now.date()
    date_final += datetime.timedelta(days=duration * 30)
    if search_money(user_id) < 100:
        return False
    else:
        update_money_buy(user_id)
        sqlite_connection = sqlite3.connect('db/db_user_buy.db')
        cursor = sqlite_connection.cursor()
        sql_update_query = f"""Update users set date_beginning = ? where user_id = ?"""
        data_tuple = (date_beginning, user_id)
        cursor.execute(sql_update_query, data_tuple)
        sqlite_connection.commit()
        sql_update_query = f"""Update users set date_final = ? where user_id = ?"""
        data_tuple = (date_final, user_id)
        cursor.execute(sql_update_query, data_tuple)
        sqlite_connection.commit()
        sql_update_query = f"""Update users set duration = ? where user_id = ?"""
        data_tuple = (duration, user_id)
        cursor.execute(sql_update_query, data_tuple)
        sqlite_connection.commit()
        update_subscription_availability_true(user_id)
        cursor.close()
        return f'🔓 Подписка оформлена и будет действительна до {date_final}'


#################################################################################################################

def search_user_with_db(user_id):
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    res = cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchall()
    if len(res) == 0:
        return False
    else:
        return True


def search_money(user_id):
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    res = cursor.execute('SELECT money FROM users WHERE user_id = ?', (user_id,)).fetchmany(1)
    return res[0][0]


def search_remaining_tokens(user_id):
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    res = cursor.execute('SELECT remaining_tokens FROM users WHERE user_id = ?', (user_id,)).fetchmany(
        1)
    return res[0][0]


def update_money(user_id, money):
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    money = int(search_money(user_id)) + int(money)
    cursor.execute('UPDATE users SET money = ? WHERE user_id = ?', (money, user_id))
    sqlite_connection.commit()

def update_money_buy(user_id):
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    money = int(search_money(user_id)) - int(100)
    cursor.execute('UPDATE users SET money = ? WHERE user_id = ?', (money, user_id))
    sqlite_connection.commit()


def add_new_user(user_id):
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    cursor.execute(
        'INSERT INTO users (user_id, remaining_tokens, subscription_availability, money) VALUES (?, ?, ?, ?)',
        (user_id, 5000, 0, 0))
    sqlite_connection.commit()


def update_token(user_id, lenth_str):
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    lenth_str = (lenth_str * 6) // 1

    remains = int(search_remaining_tokens(user_id)) - lenth_str
    if remains < 0:
        remains = 0
    cursor.execute('UPDATE users SET remaining_tokens = ? WHERE user_id = ?', (remains, user_id))
    sqlite_connection.commit()

def search_token(user_id):
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    res = cursor.execute('SELECT remaining_tokens FROM users WHERE user_id = ?', (user_id,)).fetchmany(
        1)
    return res[0][0]


def update_subscription_availability_true(user_id):
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    cursor.execute('UPDATE users SET subscription_availability = ? WHERE user_id = ?', (1, user_id))
    sqlite_connection.commit()


def update_subscription_availability_false(user_id):
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    cursor.execute('UPDATE users SET subscription_availability = ? WHERE user_id = ?', (0, user_id))
    sqlite_connection.commit()

def search_subscription_availability(user_id):
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    res = cursor.execute('SELECT subscription_availability FROM users WHERE user_id = ?', (user_id,)).fetchmany(
        1)
    return res[0][0]


########################################################################################################################

def update_label(label_payments, user_id):
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    cursor.execute('UPDATE users SET label_payments = ? WHERE user_id = ?', (label_payments, user_id))
    sqlite_connection.commit()

def get_payment_status(user_id):
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    res = cursor.execute('SELECT status_payments, label_payments FROM users WHERE user_id = ?', (user_id,)).fetchall()
    return res

def update_payment_status(user_id):
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    cursor.execute('UPDATE users SET status_payments = ? WHERE user_id = ?', (True, user_id))
    sqlite_connection.commit()

def update_payment_status_false(user_id):
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    cursor.execute('UPDATE users SET status_payments = ? WHERE user_id = ?', (False, user_id))
    sqlite_connection.commit()



