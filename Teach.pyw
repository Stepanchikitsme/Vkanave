import telebot
import pandas as pd

TOKEN = '7149671004:AAH06wLqEOnyYFUHPCqBuhX_zNAH3LKx5bA'

# Создаем объект бота
bot = telebot.TeleBot(TOKEN)

# Проверяем наличие файла данных CSV
phrases_data = pd.read_csv('data.csv', sep=';')

# Ща будем смотреть, какой юзер вводит свои штучки
user_states = {}

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: message.chat.type == 'private')
def handle_message(message):
    global phrases_data
    global user_states

    chat_id = message.chat.id

    # Если начало нового диалога, сразу кидаем на ввод фразы
    if chat_id not in user_states:
        user_states[chat_id] = {'Фраза': '', 'Ответ': ''}
        bot.reply_to(message, "Привет! Я бот, который учится отвечать на твои вопросы. Введи фразу:")
        return

    # В зависимости от того, вводится фраза или ответ, сохраняем в память
    if not user_states[chat_id]['Фраза']:
        user_states[chat_id]['Фраза'] = message.text
        bot.send_message(chat_id, "Теперь введи ответ на эту фразу:")
    else:
        user_states[chat_id]['Ответ'] = message.text
        bot.reply_to(message, "Я запомнил эту пару!")
        # Записываем пару в файл
        new_row = pd.DataFrame({'Фраза': [user_states[chat_id]['Фраза']], 'Ответ': [user_states[chat_id]['Ответ']]})
        phrases_data = pd.concat([phrases_data, new_row], ignore_index=True)
        phrases_data.to_csv('data.csv', sep=';', index=False)
        # Очищаем состояние юзера
        del user_states[chat_id]

@bot.message_handler(func=lambda message: message.reply_to_message is not None, content_types=['text'])
def handle_reply(message):
    global phrases_data
    global user_states
    chat_id = message.chat.id
    replied_message = message.reply_to_message

    # Получаем текст оригинального сообщения и ответа
    original_text = replied_message.text
    reply_text = message.text

    if original_text == "":
        pass
    else:
        new_row = pd.DataFrame({'Фраза': [original_text], 'Ответ': [reply_text]})
        phrases_data = pd.concat([phrases_data, new_row], ignore_index=True)
        phrases_data.to_csv('data.csv', sep=';', index=False)

bot.infinity_polling()
