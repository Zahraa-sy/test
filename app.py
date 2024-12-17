import telebot
from telebot import types
from flask import Flask, request
import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
import re

# توكن البوت
TOKEN = "7801426148:AAERaD89BYEKegqGSi8qSQ-Xooj8yJs41I4"
bot = telebot.TeleBot(TOKEN)

# Flask app
app = Flask(__name__)

# بيانات البريد الإلكتروني
EMAIL = "azal12345zz@gmail.com"
PASSWORD = "pbnr pihp anhm vlxp"
IMAP_SERVER = "imap.gmail.com"

# مالك البوت
OWNER_USERNAME = "Ray2ak"

# المستخدمون المصرح لهم وحساباتهم
allowed_users = {
    "Ray2ak": ["d41@flix1.me", "d42@flix1.me", "d43@flix1.me", "c15@flix1.me", "c23@flix1.me"],
    "Lamak_8": ["d41@flix1.me", "d42@flix1.me", "d43@flix1.me", "c15@flix1.me", "c23@flix1.me"],
    "flix511": ["e2@flix1.me"],
    "ZahraaKhabbaz": ["e2@flix1.me"]
}

user_accounts = {}

# دالة لتنظيف النص من الأحرف غير المرئية
def clean_text(text):
    return re.sub(r"[\u200f\u202c\u202b\u200e]", "", text).strip()

# دالة لجلب الرسائل من البريد الإلكتروني
def fetch_emails(search_keywords):
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")

        result, data = mail.search(None, "ALL")
        mail_ids = data[0].split()

        messages = []
        for mail_id in mail_ids[-20:]:
            result, msg_data = mail.fetch(mail_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")

            if any(keyword in subject for keyword in search_keywords):
                payload = msg.get_payload(decode=True)
                if payload:
                    soup = BeautifulSoup(payload, "html.parser")
                    text = soup.get_text()
                    messages.append(text)

        mail.logout()
        return messages

    except Exception as e:
        return [f"Error fetching emails: {e}"]

# بدء البوت
@bot.message_handler(commands=['start'])
def start_message(message):
    telegram_username = clean_text(message.from_user.username)

    if telegram_username in allowed_users:
        bot.send_message(message.chat.id, "يرجى إدخال اسم الحساب الذي ترغب في العمل عليه:")
        bot.register_next_step_handler(message, process_account_name)
    else:
        bot.send_message(message.chat.id, "غير مصرح لك باستخدام هذا البوت.")

def process_account_name(message):
    user_name = clean_text(message.from_user.username)
    account_name = clean_text(message.text)

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

# التعامل مع خيارات الأزرار
@bot.message_handler(func=lambda message: message.text in ['طلب رابط تحديث السكن', 'طلب رمز السكن', 'طلب استعادة كلمة المرور'])
def handle_requests(message):
    user_name = clean_text(message.from_user.username)
    account = user_accounts.get(user_name)

    if not account:
        bot.send_message(message.chat.id, "لم يتم تحديد حساب بعد. أعد تشغيل البوت وأدخل اسم الحساب.")
        return

    if message.text == 'طلب رابط تحديث السكن':
        emails = fetch_emails(["تحديث السكن"])
    elif message.text == 'طلب رمز السكن':
        emails = fetch_emails(["رمز الوصول المؤقت"])
    elif message.text == 'طلب استعادة كلمة المرور':
        emails = fetch_emails(["إعادة تعيين كلمة المرور"])

    for email_content in emails:
        if account in email_content:
            bot.send_message(message.chat.id, email_content)
            return

    bot.send_message(message.chat.id, "لم يتم العثور على رسائل مطابقة لهذا الحساب.")

# إعداد Webhook
@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '', 200

# تشغيل Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
