
import telebot
import requests
from telebot import types
from flask import Flask, request
import imaplib
import email
from email.header import decode_header
import datetime

# توكن البوت
TOKEN = "7801426148:AAERaD89BYEKegqGSi8qSQ-Xooj8yJs41I4"
bot = telebot.TeleBot(TOKEN)
# Flask app
app = Flask(__name__)

# بيانات البريد الإلكتروني
EMAIL = "azal12345zz@gmail.com"
PASSWORD = "pbnr pihp anhm vlxp"
IMAP_SERVER = "imap.gmail.com"

# حساب مالك البوت الأساسي
OWNER_USERNAME = "owner_username"

# روابط البيانات
URL_TELEGRAM_USERS = "https://github.com/Zahraa-sy/test/blob/main/allowed_names.json"

# تحميل بيانات مستخدمي تيليجرام
def load_json_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error loading data from {url}: {e}")
        return {}

telegram_users = load_json_data(URL_TELEGRAM_USERS).get("telegram_users", [])

# وظيفة لسحب رسائل البريد الإلكتروني
def fetch_emails(search_subjects):
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

            if any(keyword in subject for keyword in search_subjects):
                date = msg["Date"]
                payload = msg.get_payload(decode=True).decode()
                messages.append(f"{subject}\n{date}\n{payload}")

        mail.logout()
        return messages

    except Exception as e:
        return [f"Error fetching emails: {e}"]

# بدء البوت
@bot.message_handler(commands=['start'])
def start_message(message):
    telegram_username = message.from_user.username
    if telegram_username == OWNER_USERNAME:
        bot.send_message(message.chat.id, "أهلاً بك مالك البوت! سيتم إرسال الرسائل المهمة إليك.")
    elif telegram_username in telegram_users:
        markup = types.ReplyKeyboardMarkup(row_width=1)
        btn1 = types.KeyboardButton('طلب رابط تحديث السكن')
        btn2 = types.KeyboardButton('طلب رمز السكن')
        btn3 = types.KeyboardButton('طلب استعادة كلمة المرور')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, "اختر العملية المطلوبة:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "غير مصرح لك باستخدام هذا البوت.")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    telegram_username = message.from_user.username
    if message.text == 'طلب رابط تحديث السكن':
        emails = fetch_emails(["تحديث السكن"])
        for email_content in emails:
            bot.send_message(message.chat.id, email_content)

    elif message.text == 'طلب رمز السكن':
        emails = fetch_emails(["رمز السكن"])
        for email_content in emails:
            bot.send_message(message.chat.id, email_content)

    elif message.text == 'طلب استعادة كلمة المرور':
        emails = fetch_emails(["استعادة كلمة المرور"])
        for email_content in emails:
            bot.send_message(message.chat.id, email_content)

# إعداد مسار Webhook
@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '', 200

# تشغيل Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

