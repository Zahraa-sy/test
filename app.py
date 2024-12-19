import telebot
from telebot import types
from flask import Flask, request
import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
import re
import threading  # مكتبة الخيوط لتحسين الأداء

# توكن البوت
TOKEN = "7801426148:AAERaD89BYEKegqGSi8qSQ-Xooj8yJs41I4"
bot = telebot.TeleBot(TOKEN)

# Flask app
app = Flask(__name__)

# بيانات البريد الإلكتروني
EMAIL = "azal12345zz@gmail.com"
PASSWORD = "pbnr pihp anhm vlxp"
IMAP_SERVER = "imap.gmail.com"

# قائمة المالكين (Admins)
admin_users = ["Ray2ak", "flix511", "Lamak_8"]

# المستخدمون المصرح لهم وحساباتهم
allowed_users = {
    "Ray2ak": ["d41@flix1.me", "d42@flix1.me", "d43@flix1.me", "c15@flix1.me", "c23@flix1.me"],
    "flix511": ["d41@flix1.me", "d42@flix1.me", "d43@flix1.me", "c15@flix1.me", "c23@flix1.me"],
    "Lamak_8": ["d41@flix1.me", "d42@flix1.me", "d43@flix1.me", "c15@flix1.me", "c23@flix1.me"],
    "ZahraaKhabbaz": ["e2@flix1.me"]
}

user_accounts = {}
subscribers = []  # قائمة لتخزين معرفات (chat IDs) المشتركين

# دالة لتنظيف النص
def clean_text(text):
    return text.strip()

# دوال مساعدة لجلب البيانات
def fetch_email_with_link(account, subject_keywords, button_text):
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")
        _, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()[-5:]  # البحث في آخر 5 رسائل فقط

        for mail_id in reversed(mail_ids):
            _, msg_data = mail.fetch(mail_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")

            if any(keyword in subject for keyword in subject_keywords):
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        html_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        if account in html_content:
                            soup = BeautifulSoup(html_content, 'html.parser')
                            for a in soup.find_all('a', href=True):
                                if button_text in a.get_text():
                                    return a['href']
        return "طلبك غير موجود."
    except Exception as e:
        return f"Error fetching emails: {e}"

def fetch_email_with_code(account, subject_keywords):
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")
        _, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()[-5:]  # البحث في آخر 5 رسائل فقط

        for mail_id in reversed(mail_ids):
            _, msg_data = mail.fetch(mail_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")

            if any(keyword in subject for keyword in subject_keywords):
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        html_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        if account in html_content:
                            code_match = re.search(r'\b\d{4}\b', BeautifulSoup(html_content, 'html.parser').get_text())
                            if code_match:
                                return code_match.group(0)
        return "طلبك غير موجود."
    except Exception as e:
        return f"Error fetching emails: {e}"

# بدء البوت
@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id
    telegram_username = clean_text(message.from_user.username)

    if chat_id not in subscribers:  # تسجيل المستخدم إذا لم يكن موجودًا بالفعل
        subscribers.append(chat_id)

    if telegram_username in allowed_users or telegram_username in admin_users:
        bot.send_message(chat_id, "يرجى إدخال اسم الحساب الذي ترغب في العمل عليه:")
        bot.register_next_step_handler(message, process_account_name)
    else:
        bot.send_message(chat_id, "غير مصرح لك باستخدام هذا البوت.")

def process_account_name(message):
    user_name = clean_text(message.from_user.username)
    account_name = clean_text(message.text)

    if account_name in allowed_users.get(user_name, []) or user_name in admin_users:
        user_accounts[user_name] = account_name
        markup = types.ReplyKeyboardMarkup(row_width=1)
        btns = [
            types.KeyboardButton('طلب رابط تحديث السكن'),
            types.KeyboardButton('طلب رمز السكن'),
            types.KeyboardButton('طلب استعادة كلمة المرور'),
        ]
        if user_name in admin_users:
            btns.extend([
                types.KeyboardButton('طلب رمز تسجيل الدخول'),
                types.KeyboardButton('طلب رابط عضويتك معلقة')
            ])
        markup.add(*btns)
        bot.send_message(message.chat.id, "اختر العملية المطلوبة:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "اسم الحساب غير موجود ضمن الحسابات المصرح بها.")

@bot.message_handler(func=lambda message: message.text in [
    'طلب رابط تحديث السكن', 'طلب رمز السكن', 'طلب استعادة كلمة المرور',
    'طلب رمز تسجيل الدخول', 'طلب رابط عضويتك معلقة'
])
def handle_requests(message):
    user_name = clean_text(message.from_user.username)
    account = user_accounts.get(user_name)
    if not account:
        bot.send_message(message.chat.id, "لم يتم تحديد حساب بعد.")
        return

    bot.send_message(message.chat.id, "جاري الطلب...")  # عرض الرسالة فورًا
    response = {
        'طلب رابط تحديث السكن': fetch_email_with_link(account, ["تحديث السكن"], "نعم، أنا قدمت الطلب"),
        'طلب رمز السكن': fetch_email_with_link(account, ["رمز الوصول المؤقت"], "الحصول على الرمز"),
        'طلب استعادة كلمة المرور': fetch_email_with_link(account, ["إعادة تعيين كلمة المرور"], "إعادة تعيين كلمة المرور"),
        'طلب رمز تسجيل الدخول': fetch_email_with_code(account, ["رمز تسجيل الدخول"]) if user_name in admin_users else None,
        'طلب رابط عضويتك معلقة': fetch_email_with_link(account, ["عضويتك في Netflix معلّقة"], "إضافة معلومات الدفع") if user_name in admin_users else None
    }.get(message.text, "ليس لديك صلاحية.")
    bot.send_message(message.chat.id, response if response else "طلبك غير موجود.")

# إرسال رسالة جماعية
@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_name = clean_text(message.from_user.username)
    if user_name not in admin_users:
        bot.send_message(message.chat.id, "هذا الأمر مخصص للمسؤولين فقط.")
        return

    msg = message.text.replace('/broadcast', '').strip()
    if not msg:
        bot.send_message(message.chat.id, "يرجى إدخال الرسالة التي ترغب في إرسالها بعد الأمر.")
        return

    for subscriber in subscribers:
        try:
            bot.send_message(subscriber, msg)
        except Exception as e:
            print(f"فشل الإرسال للمشترك {subscriber}: {e}")

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
