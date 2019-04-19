import json
import requests
import time
# we need to encode any special characters in our message
import urllib
from dbhelper import DBHelper
# import telebot
# from telebot import types


TOKEN = "811868926:AAF0u4eXGd59vh4e6QHTZFJ9Sz3XmDLSDL0"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
db = DBHelper()
# bot = telebot.TeleBot(TOKEN)


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


# downloads the content from a URL and gives us a string
def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js


# function that calculates the highest ID of all the updates we receive from getUpdates
def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


# function to send an echo reply for each message that we receive
# def echo_all(updates):
#     for update in updates["result"]:
#         try:
#             text = update["message"]["text"]
#             chat = update["message"]["chat"]["id"]
#             send_message(text, chat)
#         except Exception as e:
#             print(e)

def handle_updates(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        items = db.get_items(chat)
        if text == "/done":
            keyboard = build_keyboard(items)
            send_message("Select an item to delete", chat, keyboard)
        elif text in items:
            db.delete_item(text, chat)
            items = db.get_items(chat)
            keyboard = build_keyboard(items)
            send_message("Select an item to delete", chat, keyboard)
        elif text == "/start":
            send_message("Welcome to your personal To Do list. Send any text to me and I'll store it as an item. Send "
                         "/done to remove items", chat)
        elif text.startswith("/"):
            continue
        else:
            db.add_item(text, chat)
            items = db.get_items(chat)
            message = "\n".join(items)
            send_message(message, chat)


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)


# take a list of items and construct a keyboard to allow the user to easily delete the items
def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)


# @bot.message_handler(content_types=["text"])
# def default_test(message):
#     keyboard = types.InlineKeyboardMarkup()
#     url_button = types.InlineKeyboardButton(text="Перейти", url="https://www.codecademy.com")
#     keyboard.add(url_button)
#     bot.send_message(message.chat.id, "Привет! Нажми на кнопку и перейди в поисковик.", reply_markup=keyboard)


def main():
    db.setup()
    last_update_id = None
    while True:
        # print("getting updates")
        # we have to always send an update ID which is one bigger than the previous one we've seen
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        # gets the most recent messages from Telegram every half second
        time.sleep(0.5)


# we could import our functions into another script without running anything
if __name__ == '__main__':
    main()
