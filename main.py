import telebot
from logic import *  
bot = telebot.TeleBot(token)

bot.message_handler(commands=['start'])(start)
bot.message_handler(commands=['go'])(go)
bot.message_handler(commands=['switch'])(switch_pokemon)
bot.message_handler(commands=['show'])(show_pokemons)
bot.message_handler(commands=['heal'])(heal_pokemon)
bot.message_handler(commands=['evolve'])(evolve_command)



bot.polling()