from os import getenv

import sqlite3
import telebot

TOKEN = getenv('BOT_TOKEN') if (getenv('BOT_TOKEN') is not None) else open('tokens.txt', 'r').readline().strip()

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Добро пожаловать')


bot.polling(none_stop=True)
