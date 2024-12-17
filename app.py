import telebot
import requests
from telebot import types
from flask import Flask, request
import imaplib
import email
from email.header import decode_header
import re  # لإزالة الأحرف الغريبة

# توكن البوت
TOKEN = "7801426148:AAERaD89BYEKegqGSi8qSQ-Xooj8yJs41I4"
bot = telebot.TeleBot(TOKEN)

# Flask app
app = Flask(__name__)

# بيانات البريد الإلكتروني
EMAIL = "azal12345zz@gmail.com"
PASSWORD = "pbnr pihp anhm vlxp"
IMAP_SERVER = "imap.gmail.com"

# رابط JSON الخاص بالمستخدمين المصرح بهم
URL_ALLOWED_USERS = "https://raw.githubusercontent.com/Zahraa-sy/test/main/allowed_names.json"

# دالة لتنظيف النص من الأحرف غير المرئية
def clean_text(text):
    return re.sub(r"[\u200f\u202c\u202b\u200e]", "", text).strip()

# تحميل البيانات مع تنظيفها
def load_json_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        raw_data = response.json()
        cleaned_data = {
            clean_text(user['username']).lower(): [clean_text(account).lower() for account in user['accounts']]
            for user in raw_data.get("allowed_names", [])
        }
        return cleaned_data
    except Exception as e:
        print(f"Error loading data from {url}: {e}")
        return {}

# تحميل بيانات المستخدمين
allowed_users = load_json_data(URL_ALLOWED_USERS)
user_accounts = {}

# بدء البوت
@bot.message_handler(commands=['start'])
def start_message(message):
    telegram_username = clean_text(message.from_user.username).lower()

    if telegram_username in allowed_users:
        bot.send_message(message.chat.id, "يرجى إدخال اسم الحساب الذي ترغب في العمل عليه:")
        bot.register_next_step_handler(message, process_account_name)
    else:
        bot.send_message(message.chat.id, "غير مصرح لك باستخدام هذا البوت.")

def process_account_name(message):
    user_name = clean_text(message.from_user.username).lower()
    account_name = clean_text(message.text).lower()

    if account_name in allowed_users.get(user_name, []):
        user_accounts[user_name] = account_name
        markup = types.ReplyKeyboardMarkup(row_width=1)
        btn1 = types.KeyboardButton('طلب رابط تحديث السكن')
        btn2 = types.KeyboardButton('طلب رمز السكن')
        btn3 = types.KeyboardButton('طلب استعادة كلمة المرور')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, "اختر العملية المطلوبة:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "اسم الحساب غير موجود ضمن الحسابات المصرح بها. حاول مرة أخرى:")
        bot.register_next_step_handler(message, process_account_name)

# إعداد Webhook
@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
