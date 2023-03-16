import sqlite3


def search_user_with_db(user_id):
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    res = cursor.execute('SELECT * FROM users_profile WHERE user_id = ?', (user_id,)).fetchall()
    if len(res) == 0:
        return False
    else:
        return True


def search_money(user_id):
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    res = cursor.execute('SELECT money FROM users_profile WHERE user_id = ?', (user_id,)).fetchmany(1)
    return res[0][0]


def search_remaining_tokens(user_id):
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    res = cursor.execute('SELECT remaining_tokens FROM users_profile WHERE user_id = ?', (user_id,)).fetchmany(
        1)
    return res[0][0]


def update_money(user_id, money):
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    cursor.execute('UPDATE users_profile SET money = ? WHERE user_id = ?', (money, user_id))


def add_new_user(user_id):
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    cursor.execute(
        'INSERT INTO users_profile (user_id, remaining_tokens, subscription_availability, money) VALUES (?, ?, ?, ?)',
        (user_id, 5000, 0, 0))
    sqlite_connection.commit()


def update_token(user_id, lenth_str):
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    lenth_str = (lenth_str * 6) // 1

    remains = int(search_remaining_tokens(user_id)) - lenth_str
    if remains < 0:
        remains = 0
    cursor.execute('UPDATE users_profile SET remaining_tokens = ? WHERE user_id = ?', (remains,
                                                                                       user_id))
    sqlite_connection.commit()

def search_token(user_id):
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    res = cursor.execute('SELECT remaining_tokens FROM users_profile WHERE user_id = ?', (user_id,)).fetchmany(
        1)
    return res[0][0]


def update_subscription_availability_true(user_id):
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    cursor.execute('UPDATE users_profile SET subscription_availability = ? WHERE user_id = ?', (1, user_id))
    sqlite_connection.commit()


def update_subscription_availability_false(user_id):
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    cursor.execute('UPDATE users_profile SET subscription_availability = ? WHERE user_id = ?', (0, user_id))
    sqlite_connection.commit()

def search_subscription_availability(user_id):
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    res = cursor.execute('SELECT subscription_availability FROM users_profile WHERE user_id = ?', (user_id,)).fetchmany(
        1)
    return res[0][0]
