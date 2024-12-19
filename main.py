#8070577012:AAE5w6oHRC2eI9VoSKBHWnnN36fH5tQp7-8
#Mood_reviews_bot
#https://t.me/+agQpEdvcxBY4MDVi
import matplotlib.pyplot as plt
import matplotlib
import io
matplotlib.use('Agg')
import time
import REQUESTS
from telebot import TeleBot, types
import requests
import re
from bs4 import BeautifulSoup
from MODEL import analyze_reviews

token = "8070577012:AAE5w6oHRC2eI9VoSKBHWnnN36fH5tQp7-8"
chat_id = "-1002464195623"
bot_id = '8070577012'
id_chanel='https://t.me/moods_reviews'
bot = TeleBot(token)
#<-------------------------------------------------------------------------------------->
import joblib
import pandas as pd
import numpy as np

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer as wnl
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import  TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

import emoji
import re
english_stopwords = set(stopwords.words('russian'))

model = joblib.load('C:/Users/Kanat/OneDrive/Рабочий стол/unik/MoodReviews/rf_model.pkl')
vectorizer = joblib.load('C:/Users/Kanat/OneDrive/Рабочий стол/unik/MoodReviews/tfidf_vectorizer.pkl')

emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FB00-\U0001FBFF]'
pattern = r'[^\w\s!?' + emoji_pattern + r']'
#<-------------------------------------------------------------------------------------->

# Переменная для хранения ссылки
url = ""

# Функция для проверки, является ли ссылка Wildberries и относится ли к отзывам
def is_wildberries_review_link(url):
    pattern = re.compile(
        r'^(https?://(www\.)?wildberries\.ru/catalog/\d+/feedbacks\?imtId=\d+(&\w+=\w+)*$)'
    )
    return re.match(pattern, url) is not None



def create_bar_chart(positive, neutral, negative):
    labels = ['Положительные', 'Нейтральные', 'Негативные']
    sizes = [positive, neutral, negative]

    # Larger figure size
    plt.figure(figsize=(10, 8))
    plt.bar(labels, sizes, color=['#00FF00', '#808080', '#FF0000'], alpha=0.7)

    plt.xlabel('Типы отзывов', fontsize=14)
    plt.ylabel('Количество', fontsize=14)
    plt.title('Результаты анализа настроений', fontsize=16)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)

    # Save to buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf


@bot.message_handler(commands=['start'])
def start(message):
    global url  # Используем глобальную переменную
    url = ""  # Обнуляем значение переменной

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_start = types.KeyboardButton("/start")
    btn_send_link = types.KeyboardButton("Отправить ссылку")
    btn_clear = types.KeyboardButton("Очистить")
    btn_about = types.KeyboardButton("Обо мне")  # Новая кнопка "Обо мне"
    markup.add(btn_start, btn_send_link, btn_clear, btn_about)

    answer = f'Приветствую, {message.from_user.first_name}, я обучен анализировать настроение покупателей по их отзывам на Wildberries!'
    answer2 = f'Выберите действие с кнопками ниже:'
    bot.send_message(message.chat.id, text=answer + "\n" + answer2, reply_markup=markup)


@bot.message_handler(commands=['clear'])
def clear_url(message):
    global url  # Используем глобальную переменную
    url = ""  # Обнуляем значение переменной
    bot.send_message(message.chat.id, text="Сохранённая ссылка была обнулена.")


# Реакция на текст
@bot.message_handler(func=lambda message: True)
def on_message(message):
    global url  # Используем глобальную переменную
    if message.text == "Отправить ссылку":
        bot.send_message(message.chat.id, text="Отправляйте ссылку на отзывы товара.")
    elif message.text == "Очистить":
        clear_url(message)
    elif message.text == "Обо мне":  # Обработка нажатия кнопки "Обо мне"
        bot.send_message(message.chat.id,
                         text="Я бот, созданный тремя студентами 3-го курса ДГТУ - Тимохой, Ильей и Никитосом.")
    elif is_wildberries_review_link(message.text):
        url = message.text  # Сохраняем ссылку в переменной
        bot.send_message(message.chat.id, text="Сейчас все узнаем...")


        # Получаем отзывы
        reviews = REQUESTS.get_reviews(url)
        result, positive_reviews_count, neutral_reviews_count, negative_reviews_count = analyze_reviews(reviews, vectorizer, model, pattern, english_stopwords)

        # Формируем сообщение с отзывами
        if reviews:

            bot.send_message(message.chat.id, text=result)
            pie_chart = create_bar_chart(positive_reviews_count, neutral_reviews_count, negative_reviews_count)
            bot.send_photo(message.chat.id, photo=pie_chart)
        else:
            bot.send_message(message.chat.id, text="Не удалось извлечь отзывы.")
    else:
        bot.send_message(message.chat.id, text="Это не ссылка на отзывы Wildberries. Пожалуйста, проверьте и отправьте правильную ссылку.")

if __name__ == '__main__':
    bot.polling(none_stop=True, timeout=10000)

