import telebot
from telebot import types
from flask import Flask
import threading
import os

# --- ТВОИ ДАННЫЕ ---
TOKEN = "7345968875:AAHbwebgGGpv7l2d8vVFgXebVfaYe4RnwIo"
ADMIN_ID = 5385396977  # <--- НЕ ЗАБУДЬ ПОСТАВИТЬ СВОЙ ID!
PRICE_IMAGE = "IMG-20260130-WA0025.jpg"

# СЮДА ВСТАВЬ ССЫЛКУ, КОТОРУЮ ДАЛ GITHUB (из этапа 1)
# Пример: "https://твой-ник.github.io/твое-название/"
WEB_APP_URL = "https://syrgakovakjol2010-bot.github.io/Mistori-Copani/" 

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- ГЛАВНОЕ МЕНЮ ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    # Кнопка теперь ведет на сайт GitHub
    webAppInfo = types.WebAppInfo(WEB_APP_URL) 
    
    btn_order = types.KeyboardButton(text="📱 Сделать заказ", web_app=webAppInfo)
    btn_price = types.KeyboardButton(text="💰 Прайс-лист")
    markup.add(btn_price, btn_order)
    
    bot.send_message(message.chat.id, "Меню открыто! Жмите кнопки 👇", reply_markup=markup)

# --- ПРИЕМ ЗАКАЗА (ДАННЫЕ С САЙТА) ---
@bot.message_handler(content_types=['web_app_data'])
def web_app_order(message):
    data = message.web_app_data.data
    username = message.from_user.username or "Неизвестный"
    
    # Уведомляем админа
    bot.send_message(ADMIN_ID, 
                     f"🔥 НОВЫЙ ЗАКАЗ!\n👤: @{username}\n📝: {data}")
    
    # Отвечаем клиенту
    bot.send_message(message.chat.id, "✅ Заказ принят! Скоро свяжемся.")

# --- ОТПРАВКА КАРТИНКИ (ПРАЙС) ---
@bot.message_handler(func=lambda message: message.text == "💰 Прайс-лист")
def send_price(message):
    try:
        with open(PRICE_IMAGE, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption="Наш прайс-лист")
    except:
        bot.send_message(message.chat.id, "Прайс временно недоступен.")

# --- ПРОСТОЙ ВЕБ-СЕРВЕР (ЧТОБЫ RENDER НЕ ВЫКЛЮЧАЛ БОТА) ---
@app.route('/')
def index():
    return "Бот работает! Сайт лежит на GitHub."

def run_flask():
    # Render сам даст порт
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Запускаем сервер, чтобы Render видел активность
    t = threading.Thread(target=run_flask)
    t.start()
    
    # Запускаем бота
    bot.infinity_polling()
