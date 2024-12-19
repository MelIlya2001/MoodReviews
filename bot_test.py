from telebot import TeleBot, types

# Создание экземпляра бота
bot = TeleBot("8070577012:AAE5w6oHRC2eI9VoSKBHWnnN36fH5tQp7-8")

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message: types.Message):
    bot.reply_to(message, 'Привет! Я ваш Telegram-бот.')

# Запуск бота
bot.polling(none_stop=True)