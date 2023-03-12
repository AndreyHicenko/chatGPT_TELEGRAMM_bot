import sqlite3
import datetime
import asyncio

#при покупке подписки вносит данные в базу данных
def serch_user_in_db(user_id, duration):
    list1 = []
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    result = cursor.execute(f"SELECT user_id FROM users_buy_subscription WHERE user_id")
    result = result.fetchall()
    for i in range(len(result)):
        list1.append(result[i][0])
    if str(user_id) not in list1:
        add_users(user_id, duration)
    elif str(user_id) in list1:
        upddate_datebase(user_id, duration)
    cursor.close()

def add_users(user_id, duration):

    now = datetime.datetime.now()
    date_beginning = now.date()
    date_final = now.date()
    date_final += datetime.timedelta(days=duration * 30)
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    sqlite_insert_query = f"""INSERT INTO users_buy_subscription
                          (user_id, date_beginning, duration, date_final)
                          VALUES
                          (?, ?, ?, ?);"""
    data_tuple = (user_id, date_beginning, duration, date_final)
    count = cursor.execute(sqlite_insert_query, data_tuple)
    sqlite_connection.commit()
    cursor.close()

#при запросе если труе то доступ получает иначе нет
def serch_user(user_id):
    list1 = []
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    result = cursor.execute(f"SELECT user_id FROM users_buy_subscription WHERE user_id")
    result = result.fetchall()
    cursor.close()
    for i in range(len(result)):
        list1.append(result[i][0])
    if str(user_id) not in list1:
        return False
    elif str(user_id) in list1:
        now = datetime.datetime.now()
        sqlite_connection = sqlite3.connect('db/db_user_buy.db')
        cursor = sqlite_connection.cursor()
        cursor.execute(f"SELECT date_final FROM users_buy_subscription WHERE user_id = {user_id}")
        records = cursor.fetchall()

        if now > datetime.datetime.strptime(records[0][0], "%Y-%m-%d"):
            cursor.close()
            return False
        else:
            return True








def upddate_datebase(user_id, duration):
    now = datetime.datetime.now()
    date_beginning = now.date()
    date_final = now.date()
    date_final += datetime.timedelta(days=duration * 30)
    sqlite_connection = sqlite3.connect('db/db_user_buy.db')
    cursor = sqlite_connection.cursor()
    sql_update_query = f"""Update users_buy_subscription set date_beginning = ? where user_id = ?"""
    data_tuple = (date_beginning, user_id)
    cursor.execute(sql_update_query, data_tuple)
    sqlite_connection.commit()
    sql_update_query = f"""Update users_buy_subscription set date_final = ? where user_id = ?"""
    data_tuple = (date_final, user_id)
    cursor.execute(sql_update_query, data_tuple)
    sqlite_connection.commit()
    sql_update_query = f"""Update users_buy_subscription set duration = ? where user_id = ?"""
    data_tuple = (duration, user_id)
    cursor.execute(sql_update_query, data_tuple)
    sqlite_connection.commit()
    cursor.close()

