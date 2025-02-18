import telebot
import random
import json
import os
from datetime import datetime, timedelta
import pytz
from background import keep_alive

# Инициализация бота с вашим токеном
bot = telebot.TeleBot("7828743294:AAGHXfsC5h9TZrvKYP2atAZf5O0-DnxXJ2w")

# Пути к файлам для сохранения данных
user_chebans_file = "user_chebans.json"
chat_chebans_file = "chat_chebans.json"
last_used_file = "last_used.json"
attempts_file = "attempts.json"

# Глобальные переменные
user_chebans = {}
chat_chebans = {}
last_used = {}
attempts = {}


# Функция для загрузки данных из файла
def load_data():
    global user_chebans, chat_chebans, last_used, attempts

    # Загружаем данные для глобальных чебанов
    if os.path.exists(user_chebans_file):
        with open(user_chebans_file, "r") as file:
            user_chebans = json.load(file)
    else:
        user_chebans = {}

    # Загружаем данные для чебанов по чатам
    if os.path.exists(chat_chebans_file):
        with open(chat_chebans_file, "r") as file:
            chat_chebans = json.load(file)
    else:
        chat_chebans = {}

    # Загружаем данные для последнего использования команды
    if os.path.exists(last_used_file):
        with open(last_used_file, "r") as file:
            last_used = json.load(file)
    else:
        last_used = {}

    # Загружаем данные для попыток использования команды
    if os.path.exists(attempts_file):
        with open(attempts_file, "r") as file:
            attempts = json.load(file)
    else:
        attempts = {}


# Функция для сохранения данных в файл
def save_data():
    # Сохраняем глобальные чебаны
    with open(user_chebans_file, "w") as file:
        json.dump(user_chebans, file, indent=4)

    # Сохраняем чебаны по чатам
    with open(chat_chebans_file, "w") as file:
        json.dump(chat_chebans, file, indent=4)

    # Сохраняем данные для последнего использования команды
    with open(last_used_file, "w") as file:
        json.dump(last_used, file, indent=4)

    # Сохраняем данные для попыток использования команды
    with open(attempts_file, "w") as file:
        json.dump(attempts, file, indent=4)


# Загружаем данные при старте бота
load_data()

# Устанавливаем список доступных команд
bot.set_my_commands([
    telebot.types.BotCommand("start", "Приветственное сообщение"),
    telebot.types.BotCommand("cheban", "Посидеть на стуле"),
    telebot.types.BotCommand("top_chat", "Топ чебанов в чате"),
    telebot.types.BotCommand("top_global", "Глобальный топ чебанов"),
    telebot.types.BotCommand("add_to_group", "Пригласить бота в группу")
])


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "ДАТЕБАЁ! Напиши /cheban. зачем? земля вокруг солнца крутится? зачем?.\n Добавить бота в чат - https://t.me/ilovecocks_bot?startgroup=invite\n топ чата - /top_chat\n топ глобальный - /top_global"
    )


@bot.message_handler(commands=['cheban'])
def cheban(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    # Получаем текущее время в МСК
    msk_time = datetime.now(pytz.timezone('Europe/Moscow'))

    # Если пользователь уже использовал команду сегодня, проверяем количество попыток
    if user_id in last_used:
        last_used_time = datetime.fromisoformat(last_used[user_id])
        if last_used_time.date() == msk_time.date() and msk_time.hour < 22:
            if user_id not in attempts:
                attempts[user_id] = 1
            else:
                attempts[user_id] += 1

            if attempts[user_id] == 2:
                next_available_time = (msk_time + timedelta(days=1)).replace(
                    hour=22, minute=0, second=0, microsecond=0)
                time_diff = next_available_time - msk_time
                hours, remainder = divmod(time_diff.seconds, 3600)
                minutes = remainder // 60
                bot.send_message(
                    message.chat.id,
                    f"Вы уже использовали команду /cheban сегодня. Это ваше последнее предупреждение. Следующая попытка через *{hours} часов и {minutes} минут*.",
                    parse_mode='Markdown')
                save_data()
                return
            elif attempts[user_id] > 2:
                user_chebans[user_id] -= 1
                chat_chebans[chat_id][user_id] -= 1
                bot.send_message(
                    message.chat.id,
                    "Вы использовали команду /cheban слишком много раз сегодня. Ваш чебан уменьшен на *1 см*.",
                    parse_mode='Markdown')
                save_data()
                return
            else:
                next_available_time = (msk_time + timedelta(days=1)).replace(
                    hour=22, minute=0, second=0, microsecond=0)
                time_diff = next_available_time - msk_time
                hours, remainder = divmod(time_diff.seconds, 3600)
                minutes = remainder // 60
                bot.send_message(
                    message.chat.id,
                    f"Вы уже использовали команду /cheban сегодня. Попробуйте через *{hours} часов и {minutes} минут*.",
                    parse_mode='Markdown')
                save_data()
                return

    # Если у пользователя еще нет длины чебана в глобальном списке, создаём её
    if user_id not in user_chebans:
        user_chebans[user_id] = 0  # начальное значение чебана 0

    # Если в текущем чате нет чебанов, создаём
    if chat_id not in chat_chebans:
        chat_chebans[chat_id] = {}

    # Если у пользователя нет чебана в этом чате, создаём
    if user_id not in chat_chebans[chat_id]:
        chat_chebans[chat_id][user_id] = 0

    # Генерируем случайное изменение длины чебана от -5 до +15, но не 0
    change = 0
    while change == 0:  # Повторяем генерацию, пока изменение не будет отличным от 0
        change = random.randint(-5, 15)

    # Отправляем сообщение, если чебан увеличился или уменьшился
    if change > 0:
        message_text = f" просидел на табуретке 1{18*change} часов и твой чебан вырос на *{change} см*.\n Текущий размер чебана: *{user_chebans[user_id] + change} см*."
    else:
        message_text = f" помазал чебанчик мазькой за {189*abs(change)} гроши и он сократился на *{abs(change)} см*.\nТекущий размер чебана: *{user_chebans[user_id] + change} см*."

    # Обновляем длину чебана в обоих словарях, прибавляем к предыдущему значению
    user_chebans[user_id] += change
    chat_chebans[chat_id][user_id] += change

    # Обновляем время последнего использования команды и сбрасываем счетчик попыток
    last_used[user_id] = msk_time.isoformat()
    attempts[user_id] = 0

    # Сохраняем данные
    save_data()

    # Получаем username, если он есть, иначе используем 'Unknown'
    username = message.from_user.username if message.from_user.username else "Unknown"

    # Отправляем сообщение пользователю в группе или приватно
    if message.chat.type == 'private':
        bot.send_message(message.chat.id, message_text, parse_mode='Markdown')
    else:
        bot.send_message(chat_id,
                         f" @{username} {message_text}",
                         parse_mode='Markdown')


@bot.message_handler(commands=['top_chat'])
def top_chat(message):
    chat_id = message.chat.id

    if chat_id not in chat_chebans or not chat_chebans[chat_id]:
        bot.send_message(message.chat.id, "В этом чате еще нет чебанов.")
        return

    # Получаем список всех участников чата
    members = bot.get_chat_administrators(chat_id)
    member_ids = [member.user.id for member in members]

    # Отфильтровываем глобальный топ, оставляя только участников чата
    filtered_chebans = {
        user_id: cheban_length
        for user_id, cheban_length in user_chebans.items()
        if user_id in member_ids
    }

    if not filtered_chebans:
        bot.send_message(message.chat.id, "В этом чате еще нет чебанов.")
        return

    # Сортируем пользователей по длине чебана в чате
    sorted_chebans = sorted(filtered_chebans.items(),
                            key=lambda x: x[1],
                            reverse=True)

    # Формируем сообщение
    top_message = "Топ чебанов этого чата:\n"
    for idx, (user_id, cheban_length) in enumerate(sorted_chebans, start=1):
        user = bot.get_chat_member(chat_id, user_id).user
        username = user.username if user.username else "Unknown"
        top_message += f"{idx}. @{username} : *{cheban_length} см*\n"

    # Отправляем сообщение
    bot.send_message(message.chat.id, top_message, parse_mode='Markdown')


@bot.message_handler(commands=['top_global'])
def top_global(message):
    if not user_chebans:
        bot.send_message(message.chat.id, "Что такое чебан?.")
        return

    # Сортируем пользователей по глобальной длине чебана
    sorted_chebans = sorted(user_chebans.items(),
                            key=lambda x: x[1],
                            reverse=True)

    # Формируем сообщение
    top_message = "Все чебаны на планете:\n"
    for idx, (user_id, cheban_length) in enumerate(sorted_chebans, start=1):
        user = bot.get_chat_member(message.chat.id, user_id).user
        username = user.username if user.username else "Unknown"
        top_message += f"{idx}. @{username} : *{cheban_length} см*\n"

    # Отправляем сообщение
    bot.send_message(message.chat.id, top_message, parse_mode='Markdown')


@bot.message_handler(commands=['add_to_group'])
def add_to_group(message):
    # Замените ссылку на ссылку для добавления бота в вашу группу
    invite_link = "https://t.me/ilovecocks_bot?startgroup=invite"
    bot.send_message(
        message.chat.id,
        f"Вы можете добавить меня в свою группу, используя эту ссылку:\n{invite_link}"
    )

keep_alive()
# Запуск бота
bot.polling(none_stop=True)
