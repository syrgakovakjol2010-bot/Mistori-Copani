import telebot
from telebot import types
from flask import Flask
import threading
import os

# --- ТВОИ ДАННЫЕ (ОБНОВЛЕННЫЕ) ---
TOKEN = "7345968875:AAHbwebgGGpv7l2d8vVFgXebVfaYe4RnwIo"
ADMIN_ID = 5385396977
PRICE_IMAGE = "IMG-20260130-WA0025.jpg"  # <-- Убедись, что файл с таким именем загружен на GitHub!

# Ссылка на твой Web App (сайт на GitHub Pages)
WEB_APP_URL = "https://syrgakovakjol2010-bot.github.io/Mistori-Copani/"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- ХРАНИЛИЩЕ ЧАТОВ ---
# {ID_Админа: ID_Клиента} — с кем сейчас говорит админ
admin_active_chat = {}
# {ID_Клиента: ID_Админа} — чтобы знать, кому пересылать сообщения клиента
user_active_chat = {}

# --- КОМАНДА /START ---
@bot.message_handler(commands=['start'])
def start(message):
    # Если пишет Админ
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, f"Привет, Шеф! Бот готов к работе.")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    # Кнопка с Web App
    webAppInfo = types.WebAppInfo(WEB_APP_URL) 
    
    btn_order = types.KeyboardButton(text="📱 Сделать заказ", web_app=webAppInfo)
    btn_price = types.KeyboardButton(text="💰 Прайс-лист")
    
    markup.add(btn_price, btn_order)
    
    bot.send_message(message.chat.id, 
                     "👋 Добро пожаловать в IT-студию!\nВыберите действие в меню ниже:", 
                     reply_markup=markup)

# --- ОБРАБОТКА ЗАКАЗА С САЙТА ---
@bot.message_handler(content_types=['web_app_data'])
def web_app_order(message):
    data = message.web_app_data.data # Текст заказа с сайта
    user_id = message.chat.id
    username = message.from_user.username or "Без ника"
    
    # Кнопка для админа "Принять"
    markup = types.InlineKeyboardMarkup()
    btn_accept = types.InlineKeyboardButton("✅ Принять и написать", callback_data=f"connect_{user_id}")
    markup.add(btn_accept)
    
    # Уведомление админу
    bot.send_message(ADMIN_ID, 
                     f"🚨 <b>НОВЫЙ ЗАКАЗ!</b>\n\n👤 Клиент: @{username}\n🆔 ID: {user_id}\n📝 Инфо: {data}", 
                     parse_mode="HTML",
                     reply_markup=markup)
    
    # Ответ клиенту
    bot.send_message(user_id, "✅ Ваш заказ принят! Администратор скоро свяжется с вами.")

# --- АДМИН НАЖАЛ "ПРИНЯТЬ" ---
@bot.callback_query_handler(func=lambda call: True)
def callback_admin(call):
    if call.data.startswith("connect_"):
        client_id = int(call.data.split("_")[1])
        
        # Создаем "мост" между админом и клиентом
        admin_active_chat[ADMIN_ID] = client_id
        user_active_chat[client_id] = ADMIN_ID
        
        bot.send_message(ADMIN_ID, f"✅ Чат начат с ID {client_id}.\nПиши сюда — он получит.\nДля выхода напиши /stop")
        bot.send_message(client_id, "👋 Администратор подключился к чату! Можете задавать вопросы.")
        
        # Убираем кнопку
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

# --- ГЛАВНАЯ ЛОГИКА (ПЕРЕПИСКА + УМНЫЕ ОТВЕТЫ) ---
@bot.message_handler(content_types=['text'])
def chat_logic(message):
    user_id = message.chat.id
    text = message.text.lower()

    # --- 1. ЕСЛИ ПИШЕТ АДМИН ---
    if user_id == ADMIN_ID:
        if ADMIN_ID in admin_active_chat:
            client_id = admin_active_chat[ADMIN_ID]
            if message.text == "/stop":
                # Разрываем связь
                if ADMIN_ID in admin_active_chat: del admin_active_chat[ADMIN_ID]
                if client_id in user_active_chat: del user_active_chat[client_id]
                bot.send_message(ADMIN_ID, "🔴 Чат завершен.")
                bot.send_message(client_id, "Диалог завершен. Спасибо!")
            else:
                # Пересылаем сообщение клиенту
                try:
                    bot.send_message(client_id, f"👨‍💻 Админ: {message.text}")
                except:
                    bot.send_message(ADMIN_ID, "❌ Ошибка: Не удалось отправить (клиент заблокировал бота).")
        else:
            bot.send_message(ADMIN_ID, "Ты не в режиме чата. Жди заказов!")
        return

    # --- 2. ЕСЛИ ПИШЕТ КЛИЕНТ (И ОН УЖЕ В ЧАТЕ) ---
    if user_id in user_active_chat:
        admin_id = user_active_chat[user_id]
        bot.send_message(admin_id, f"📩 Клиент: {message.text}")
        return

    # --- 3. АВТО-ОТВЕТЧИК (УМНЫЕ ОТВЕТЫ) ---
    
    # Прайс-лист
    if "цена" in text or "прайс" in text or "сколько стоит" in text:
        try:
            with open(PRICE_IMAGE, 'rb') as photo:
                bot.send_photo(user_id, photo, caption="💰 Актуальный прайс-лист")
        except:
            bot.send_message(user_id, "Ошибка: Файл прайса не найден (скажите админу загрузить картинку).")

    # Визитка
    elif "визитка" in text:
        bot.send_message(user_id, 
            "📄 <b>Сайт-визитка</b> — это ваш личный сайт.\n"
            "Подходит для экспертов, врачей, юристов.\n"
            "💵 Цена: 3 000 сом.", parse_mode="HTML")

    # Инфо-сайт
    elif "инфо" in text or "info" in text:
        bot.send_message(user_id, 
            "ℹ️ <b>Info-страница</b> — самый дешевый вариант.\n"
            "Одна страница с вашими контактами и описанием.\n"
            "💵 Цена: 1 500 сом.", parse_mode="HTML")

    # Про бота
    elif "бот" in text:
        bot.send_message(user_id, 
            "🤖 <b>Telegram-бот</b> работает 24/7 вместо менеджера.\n"
            "Принимает заказы, показывает товары, отвечает на вопросы.\n"
            "💵 Цена: от 5 000 сом.", parse_mode="HTML")

    # Web App
    elif "web" in text or "веб" in text or "app" in text:
        bot.send_message(user_id, 
            "📱 <b>Web App</b> — это сайт внутри Телеграма.\n"
            "Выглядит как приложение: с каталогом и корзиной.\n"
            "💵 Цена: 8 000 сом.", parse_mode="HTML")

    # Комбо
    elif "комбо" in text or "combo" in text:
        bot.send_message(user_id, 
            "🎁 <b>Комбо-пакеты</b> — это выгодно!\n"
            "🔥 Start: Визитка + Бот = 5 000 сом.\n"
            "🚀 Business: Сайт + Web App = 25 000 сом.", parse_mode="HTML")

    else:
        bot.send_message(user_id, 
            "🤖 Я пока не понял вопрос.\n"
            "Нажмите <b>«📱 Сделать заказ»</b> или спросите про <b>«Сайт»</b>, <b>«Бот»</b>, <b>«Комбо»</b>.", parse_mode="HTML")

# --- ЗАПУСК СЕРВЕРА RENDER ---
@app.route('/')
def index():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Запускаем Flask в фоне
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    # Запускаем бота
    bot.infinity_polling()
    
