from os import getenv

import telebot
from handlers import db

TOKEN = getenv('BOT_TOKEN') if (getenv('BOT_TOKEN') is not None) else open('tokens.txt', 'r').readline().strip()

bot = telebot.TeleBot(TOKEN)

full_name = ''
policy_number = 0
is_registered = False

current_user = {'user_id': None, 'name': None, 'surname': None, 'patronymic': None, 'policy_number': None}


@bot.message_handler(commands=['start'])
def start_message(message):
    global is_registered
    global current_user

    current_user['user_id'] = message.from_user.id

    if db.db_find_val(current_user.get('user_id'), current_user):
        is_registered = True

        bot.send_message(message.chat.id, 'Добро пожаловать, {}!'.format(current_user.get('name')))
    else:
        is_registered = False

        bot.send_message(message.chat.id, 'Добро пожаловать!')


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
    global full_name
    global current_user

    while policy_number == 0:
        try:
            policy_number = int(message.text)
        except ValueError:
            bot.send_message(message.from_user.id, 'Введите действительный номер!')

    processed_full_name = full_name.split(' ')

    current_user['surname'] = processed_full_name[0]
    current_user['name'] = processed_full_name[1]
    current_user['patronymic'] = processed_full_name[2]

    current_user['policy_number'] = policy_number

    db.db_save_val(user_id=current_user.get('user_id'), user_name=current_user.get('name'),
                   user_surname=current_user.get('surname'),
                   user_patronymic=current_user.get('patronymic'), policy_number=current_user.get('policy_number'))

    bot.send_message(message.from_user.id, 'Регистрация окончена!')


bot.polling(none_stop=True)
