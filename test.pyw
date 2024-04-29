import numpy as np
import pandas as pd
import telebot
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time

CSV_FILE_PATH = "data.csv"

def load_data(csv_file):
    try:
        df = pd.read_csv(csv_file, header=None, delimiter=";")
        df = df.fillna('')
        phrases = df[0].tolist()
        answers = df[1].tolist()
    except pd.errors.EmptyDataError:
        print("Файл CSV пустой. Проверь его содержимое.")
        phrases = []
        answers = []
    except Exception as e:
        print(f"Произошла ошибка при загрузке данных из CSV файла: {e}")
        phrases = []
        answers = []
    return phrases, answers

def prepare_tfidf_matrix(phrases):
    if not phrases or not any(phrases):
        print("Документы пусты или содержат только стоп-слова. Невозможно построить TF-IDF матрицу.")
        return None, None
    else:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(phrases)
        return vectorizer, tfidf_matrix

def find_most_similar_answer(input_phrase, vectorizer, tfidf_matrix, phrases, answers):
    input_phrase = input_phrase.lower()
    input_vector = vectorizer.transform([input_phrase])
    similarities = cosine_similarity(input_vector, tfidf_matrix)
    similar_indices = np.where(similarities > 0)[1]
    if similar_indices.size > 0:
        most_similar_index = np.argmax(similarities)
        most_similar_answer = answers[most_similar_index]
    else:
        most_similar_answer = "Сорян, братан, не понял вопроса, может, другие слова попробуем?"
    return most_similar_answer

bot = telebot.TeleBot("6925787597:AAHt9recfbDHso2dzdEAZLkvLBBUl12jLsA")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет, я готов отвечать на твои вопросы!")

@bot.message_handler(func=lambda message: True and  message.chat.type == 'private', content_types=['text'])
def reply_to_user_message(message):
    phrases, answers = load_data(CSV_FILE_PATH)
    vectorizer, tfidf_matrix = prepare_tfidf_matrix(phrases)
    if vectorizer is not None and tfidf_matrix is not None:
        most_similar_answer = find_most_similar_answer(message.text, vectorizer, tfidf_matrix, phrases, answers)
        bot.reply_to(message, most_similar_answer)

@bot.message_handler(func=lambda message: message.chat.type == 'group', content_types=['text'])
def reply_to_group_message(message):
    phrases, answers = load_data(CSV_FILE_PATH)
    vectorizer, tfidf_matrix = prepare_tfidf_matrix(phrases)
    if vectorizer is not None and tfidf_matrix is not None:
        if message.text.startswith('/quest'):
            query = message.text[6:].strip()
            most_similar_answer = find_most_similar_answer(query, vectorizer, tfidf_matrix, phrases, answers)
            bot.reply_to(message, most_similar_answer)
        elif '@chern_ai_bot' in message.text:
            query = message.text.replace('@chern_ai_bot', '').strip()
            most_similar_answer = find_most_similar_answer(query, vectorizer, tfidf_matrix, phrases, answers)
            bot.reply_to(message, most_similar_answer)

def start_bot():
    bot.infinity_polling()

def on_modified(event):
    phrases, answers = load_data(CSV_FILE_PATH)
    vectorizer, tfidf_matrix = prepare_tfidf_matrix(phrases)

event_handler = FileSystemEventHandler()
event_handler.on_modified = on_modified
observer = Observer()
observer.schedule(event_handler, path='.', recursive=False)
observer.start()

start_bot()
