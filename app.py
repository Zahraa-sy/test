import telebot
from telebot import types
from flask import Flask, request
import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
import re
import time  # مكتبة لتأخير المحاولات

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

# دالة إعادة المحاولة للاتصال بالخادم
def retry_on_error(func):
    def wrapper(*args, **kwargs):
        retries = 3  # عدد المحاولات
        for attempt in range(retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if "EOF occurred" in str(e) or "socket" in str(e):
                    time.sleep(2)  # تأخير قبل إعادة المحاولة
                    print(f"إعادة المحاولة... المحاولة {attempt + 1}/{retries}")
                else:
                    return f"Error fetching emails: {e}"
        return "فشل الاتصال بالخادم بعد عدة محاولات."
    return wrapper

# توابع استخراج البيانات
@retry_on_error
def fetch_update_address_link(account):
    return fetch_email_with_link(account, ["تحديث السكن"], "نعم، أنا قدمت الطلب")

@retry_on_error
def fetch_temporary_code_link(account):
    return fetch_email_with_link(account, ["رمز الوصول المؤقت"], "الحصول على الرمز")

@retry_on_error
def fetch_reset_password_link(account):
    return fetch_email_with_link(account, ["إعادة تعيين كلمة المرور"], "إعادة تعيين كلمة المرور")

@retry_on_error
def fetch_login_code(account):
    return fetch_email_with_code(account, ["رمز تسجيل الدخول"])

@retry_on_error
def fetch_suspended_membership_link(account):
    return fetch_email_with_link(account, ["عضويتك في Netflix معلّقة"], "إضافة معلومات الدفع")

# دوال مساعدة
def fetch_email_with_link(account, subject_keywords, button_text):
    with imaplib.IMAP4_SSL(IMAP_SERVER) as mail:
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")
        _, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()[-10:]

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
        return None

def fetch_email_with_code(account, subject_keywords):
    with imaplib.IMAP4_SSL(IMAP_SERVER) as mail:
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")
        _, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()[-10:]

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
        return None

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

    bot.send_message(message.chat.id, "جاري الطلب...")
    response = {
        'طلب رابط تحديث السكن': fetch_update_address_link(account),
        'طلب رمز السكن': fetch_temporary_code_link(account),
        'طلب استعادة كلمة المرور': fetch_reset_password_link(account),
        'طلب رمز تسجيل الدخول': fetch_login_code(account) if user_name in admin_users else None,
        'طلب رابط عضويتك معلقة': fetch_suspended_membership_link(account) if user_name in admin_users else None
    }.get(message.text, "ليس لديك صلاحية.")

    bot.send_message(message.chat.id, response if response else "طلبك غير موجود.")
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
