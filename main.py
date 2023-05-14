from os import getenv

import telebot
from telebot import types

from handlers import db

TOKEN = getenv('BOT_TOKEN') if (getenv('BOT_TOKEN') is not None) else open('tokens.txt', 'r').readline().strip()

bot = telebot.TeleBot(TOKEN)

full_name = ''
policy_number = 0
is_registered = False

current_user = {'user_id': None, 'name': None, 'surname': None, 'patronymic': None, 'policy_number': None}
current_hospital = {'hospital_name': None, 'hospital_address': None}
current_receipt_time = {'id': None, 'year': None, 'month': None, 'day': None, 'time': None, 'is_taken': None,
                        'hospital_name': None,
                        'hospital_address': None}

hospitals_list = []
current_receipt_time_list = []
current_receipt_time_index = None


@bot.message_handler(commands=['start'])
def start_message(message):
    global is_registered
    global current_user

    current_user['user_id'] = message.from_user.id

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    registration_button = types.KeyboardButton("Регистрация ✏️")
    markup.add(registration_button)

    markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    hospital_list_button = types.KeyboardButton("Выбор больницы 🏥️")
    markup1.add(hospital_list_button)

    receipts_list_button = types.KeyboardButton("Просмотр ваших записей ✏️")
    markup1.add(receipts_list_button)

    if db.db_find_val_patients(current_user.get('user_id'), current_user):
        is_registered = True

        bot.send_message(message.chat.id, 'Добро пожаловать, {}!'.format(current_user.get('name')),
                         reply_markup=markup1)
        bot.register_next_step_handler(message, show_addresses)
    else:
        is_registered = False

        bot.send_message(message.chat.id, 'Добро пожаловать!', reply_markup=markup)


@bot.message_handler(content_types=['text'])
# region Регистрация
def start(message):
    a = types.ReplyKeyboardRemove()
    if message.text == 'Регистрация ✏️':
        bot.send_message(message.from_user.id, "Введите ваше ФИО: ", reply_markup=a)
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

    db.db_save_val_patients(user_id=current_user.get('user_id'), user_name=current_user.get('name'),
                            user_surname=current_user.get('surname'),
                            user_patronymic=current_user.get('patronymic'),
                            policy_number=current_user.get('policy_number'))

    del (full_name, policy_number)

    bot.send_message(message.from_user.id, 'Регистрация окончена!')

    bot.register_next_step_handler(message, show_addresses)


# endregion

# region Запись
def show_addresses(message):
    if message.text == 'Просмотр ваших записей ✏️':
        show_your_receipt(message)
    else:
        global hospitals_list

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        buttons = []

        hospitals_list = db.get_column_values('hospitals', 'hospital_name')

        for i in range(0, db.get_row_count('hospitals')):
            buttons.append(types.KeyboardButton(f'🏥 {hospitals_list[i]}'))
            markup.add(buttons[i])

        markup.add(types.KeyboardButton("🔙 Назад"))

        bot.send_message(message.from_user.id, "Выберите больницу: ", reply_markup=markup)
        bot.register_next_step_handler(message, show_receipts_time)


def show_receipts_time(message):
    if message.text == "🔙 Назад":
        start_message(message)
    else:
        global current_receipt_time_list

        for i in range(0, len(hospitals_list)):
            if message.text[2:] == hospitals_list[i]:
                for row in db.select_rows_with_values_hospitals('receipt_time', 0, hospitals_list[i]):
                    current_receipt_time_list.append(
                        {'id': row[0], 'year': row[1], 'month': row[2], 'day': row[3], 'time': row[4],
                         'is_taken': row[5],
                         'hospital_name': row[6], 'hospital_address': row[7]})

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        for i in range(len(current_receipt_time_list)):
            button_receipt = types.InlineKeyboardButton(
                text='🕑{}.{}.{} {} {}'.format(
                    current_receipt_time_list[i].get('year'),
                    current_receipt_time_list[i].get('month'),
                    current_receipt_time_list[i].get('day'),
                    current_receipt_time_list[i].get('time'),
                    current_receipt_time_list[i].get('hospital_address')
                )
            )
            markup.add(button_receipt)

        markup.add(types.KeyboardButton("🔙 Назад"))

        bot.send_message(message.from_user.id, "Выберите запись: ", reply_markup=markup)

        bot.register_next_step_handler(message, process_receipt_time)



def process_receipt_time(message):
    global current_receipt_time_list

    if message.text == "🔙 Назад":
        current_receipt_time_list = []
        show_addresses(message)
    else:
        processed_receipt = str(message.text[1:])
        processed_receipt = processed_receipt.split(' ')

        year = processed_receipt[0].split('.')[0]
        month = processed_receipt[0].split('.')[1]
        day = processed_receipt[0].split('.')[2]

        current_receipt_time['year'] = int(year)
        current_receipt_time['month'] = int(month)
        current_receipt_time['day'] = int(day)
        current_receipt_time['time'] = processed_receipt[1]
        current_receipt_time['hospital_address'] = processed_receipt[2] + ' ' + processed_receipt[3]

        db.update_column_value('receipt_time', 'is_taken', 1,
                               current_receipt_time.get('year'),
                               current_receipt_time.get('month'),
                               current_receipt_time.get('day'),
                               current_receipt_time.get('time'),
                               current_receipt_time.get('hospital_address'))

        db.update_column_value('receipt_time', 'patient', current_user['user_id'],
                               current_receipt_time.get('year'),
                               current_receipt_time.get('month'),
                               current_receipt_time.get('day'),
                               current_receipt_time.get('time'),
                               current_receipt_time.get('hospital_address'))

        bot.send_message(message.from_user.id, "Вы записаны ✅!")

        current_receipt_time_list = []

        start_message(message)


# endregion

# region Просмотр запискй
def show_your_receipt(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for row in db.select_rows_with_values_receipts('receipt_time', int(current_user.get('user_id'))):
        button_receipt = types.InlineKeyboardButton(
            text='🕑{}.{}.{} {} {} {}'.format(
                row[1],
                row[2],
                row[3],
                row[4],
                row[6],
                row[7]
            )
        )
        markup.add(button_receipt)

    markup.add(types.KeyboardButton("🔙 Назад"))

    bot.send_message(message.from_user.id, "Вот ваши записи!", reply_markup=markup)
    bot.register_next_step_handler(message, back_button)

def back_button(message):
    if message.text == "🔙 Назад":
        start_message(message)


# endregion

bot.polling(none_stop=True)
