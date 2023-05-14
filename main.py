from os import getenv

import sqlite3
import telebot

TOKEN = getenv('BOT_TOKEN') if (getenv('BOT_TOKEN') is not None) else open('tokens.txt', 'r').readline().strip()

conn = sqlite3.connect('database/db.db', check_same_thread=False)
cursor = conn.cursor()

bot = telebot.TeleBot(TOKEN)


def db_table_val(user_id: int, user_name: str, user_surname: str, user_patronymic: str, policy_number: int):
    cursor.execute('INSERT INTO patients (user_id, user_name, user_surname, user_patronymic, policy_number) '
                   'VALUES (?, ?, ?, ?, ?)',
                   (user_id, user_name, user_surname, user_patronymic, policy_number))
    conn.commit()


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Добро пожаловать!')


full_name = ''
policy_number = 0


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/reg':
        bot.send_message(message.from_user.id, "Введите ваше ФИО: ")
        bot.register_next_step_handler(message, get_name)


def get_name(message):
    global full_name
    full_name = message.text

    bot.send_message(message.from_user.id, 'Введите номер вашего полиса ОМС: ')
    bot.register_next_step_handler(message, get_policy_number)


def get_policy_number(message):
    global policy_number

    while policy_number == 0:
        try:
            policy_number = int(message.text)
        except ValueError:
            bot.send_message(message.from_user.id, 'Введите действительный номер!')

    global full_name

    processed_full_name = full_name.split(' ')

    us_surname = processed_full_name[0]
    us_name = processed_full_name[1]
    us_patronymic = processed_full_name[2]

    db_table_val(user_id=message.from_user.id, user_name=us_name, user_surname=us_surname, user_patronymic=us_patronymic, policy_number=policy_number)

    bot.send_message(message.from_user.id, 'Регистрация окончена!')


bot.polling(none_stop=True)
