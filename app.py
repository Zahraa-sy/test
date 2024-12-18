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

# دالة لتنظيف النص
def clean_text(text):
    return text.strip()

# التوابع لاستخراج المعلومات بناءً على الحساب والطلب
def fetch_update_address_link(account):
    return fetch_email_with_link(account, ["تحديث السكن"], "نعم، أنا قدمت الطلب")

def fetch_temporary_code_link(account):
    return fetch_email_with_link(account, ["رمز الوصول المؤقت"], "الحصول على الرمز")

def fetch_reset_password_link(account):
    return fetch_email_with_link(account, ["إعادة تعيين كلمة المرور"], "إعادة تعيين كلمة المرور")

def fetch_login_code(account):
    return fetch_email_with_code(account, ["رمز تسجيل الدخول"])

def fetch_suspended_membership_link(account):
    return fetch_email_with_link(account, ["عضويتك في Netflix معلّقة"], "إضافة معلومات الدفع")

# دالة مساعدة لجلب الرابط
def fetch_email_with_link(account, subject_keywords, button_text):
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")

        result, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()

        for mail_id in reversed(mail_ids):
            result, msg_data = mail.fetch(mail_id, "(RFC822)")
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
                                    mail.logout()
                                    return a['href']

        mail.logout()
        return "لم يتم العثور على الرابط المطلوب."

    except Exception as e:
        return f"Error fetching emails: {e}"

# دالة مساعدة لجلب رمز مكون من 4 أرقام
def fetch_email_with_code(account, subject_keywords):
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")

        result, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()

        for mail_id in reversed(mail_ids):
            result, msg_data = mail.fetch(mail_id, "(RFC822)")
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
                                mail.logout()
                                return code_match.group(0)

        mail.logout()
        return "لم يتم العثور على رمز تسجيل الدخول."

    except Exception as e:
        return f"Error fetching emails: {e}"

# بدء البوت
@bot.message_handler(commands=['start'])
def start_message(message):
    telegram_username = clean_text(message.from_user.username)
    if telegram_username in allowed_users or telegram_username in admin_users:
        bot.send_message(message.chat.id, "يرجى إدخال اسم الحساب الذي ترغب في العمل عليه:")
        bot.register_next_step_handler(message, process_account_name)
    else:
        bot.send_message(message.chat.id, "غير مصرح لك باستخدام هذا البوت.")

def process_account_name(message):
    user_name = clean_text(message.from_user.username)
    account_name = clean_text(message.text)

    if account_name in allowed_users.get(user_name, []) or user_name in admin_users:
        user_accounts[user_name] = account_name
        markup = types.ReplyKeyboardMarkup(row_width=1)
        btn1 = types.KeyboardButton('طلب رابط تحديث السكن')
        btn2 = types.KeyboardButton('طلب رمز السكن')
        btn3 = types.KeyboardButton('طلب استعادة كلمة المرور')
        if user_name in admin_users:
            btn4 = types.KeyboardButton('طلب رمز تسجيل الدخول')
            btn5 = types.KeyboardButton('طلب رابط عضويتك معلقة')
            markup.add(btn4, btn5)
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, "اختر العملية المطلوبة:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "اسم الحساب غير موجود ضمن الحسابات المصرح بها. حاول مرة أخرى:")
        bot.register_next_step_handler(message, process_account_name)

# التعامل مع الطلبات
@bot.message_handler(func=lambda message: message.text in [
    'طلب رابط تحديث السكن', 'طلب رمز السكن', 'طلب استعادة كلمة المرور',
    'طلب رمز تسجيل الدخول', 'طلب رابط عضويتك معلقة'
])
def handle_requests(message):
    user_name = clean_text(message.from_user.username)
    account = user_accounts.get(user_name)

    if not account:
        bot.send_message(message.chat.id, "لم يتم تحديد حساب بعد. أعد تشغيل البوت وأدخل اسم الحساب.")
        return

    if message.text == 'طلب رابط تحديث السكن':
        response = fetch_update_address_link(account)
    elif message.text == 'طلب رمز السكن':
        response = fetch_temporary_code_link(account)
    elif message.text == 'طلب استعادة كلمة المرور':
        response = fetch_reset_password_link(account)
    elif message.text == 'طلب رمز تسجيل الدخول' and user_name in admin_users:
        response = fetch_login_code(account)
    elif message.text == 'طلب رابط عضويتك معلقة' and user_name in admin_users:
        response = fetch_suspended_membership_link(account)
    else:
        response = "ليس لديك صلاحية لتنفيذ هذا الطلب."

    bot.send_message(message.chat.id, response)

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
