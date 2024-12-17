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
admin_users = ["Ray2ak", "flix511","Lamak_8"]

# المستخدمون المصرح لهم وحساباتهم
allowed_users = {
    "Ray2ak": ["d41@flix1.me", "d42@flix1.me", "d43@flix1.me", "c15@flix1.me", "c23@flix1.me"],
    "flix511": ["d41@flix1.me", "d42@flix1.me", "d43@flix1.me", "c15@flix1.me", "c23@flix1.me"],
    "Lamak_8": ["d41@flix1.me", "d42@flix1.me", "d43@flix1.me", "c15@flix1.me", "c23@flix1.me"],
    "ZahraaKhabbaz": ["e2@flix1.me"]
}

user_accounts = {}

# دالة لتنظيف النص من الأحرف غير المرئية
def clean_text(text):
    return re.sub(r"[\u200f\u202c\u202b\u200e]", "", text).strip()

# دالة للاتصال بالبريد الإلكتروني وجلب الرسائل
def fetch_emails(account, subject_keywords, extract_type):
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")

        result, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()

        for mail_id in reversed(mail_ids[-20:]):
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
                        soup = BeautifulSoup(html_content, 'html.parser')

                        # استخراج الرابط أو الرمز حسب نوع العملية
                        if extract_type == "link":
                            for a in soup.find_all('a', href=True):
                                return a['href']
                        elif extract_type == "code":
                            code_match = re.search(r'\b\d{4}\b', soup.get_text())
                            if code_match:
                                return code_match.group(0)

        return "لم يتم العثور على الرسالة المطلوبة."

    except Exception as e:
        return f"Error fetching emails: {e}"

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

        # الأزرار المتاحة للزبائن
        btn1 = types.KeyboardButton('طلب رابط تحديث السكن')
        btn2 = types.KeyboardButton('طلب رمز السكن')
        btn3 = types.KeyboardButton('طلب استعادة كلمة المرور')
        markup.add(btn1, btn2, btn3)

        # إضافة أزرار خاصة للمالكين (Admins)
        if user_name in admin_users:
            btn4 = types.KeyboardButton('طلب رمز تسجيل الدخول')
            btn5 = types.KeyboardButton('طلب رابط العضوية المعلقة')
            markup.add(btn4, btn5)

        bot.send_message(message.chat.id, "اختر العملية المطلوبة:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "اسم الحساب غير موجود ضمن الحسابات المصرح بها. حاول مرة أخرى:")
        bot.register_next_step_handler(message, process_account_name)

# التعامل مع كل زر بشكل منفصل
@bot.message_handler(func=lambda message: message.text == 'طلب رابط تحديث السكن')
def handle_update_address(message):
    user_name = clean_text(message.from_user.username)
    account = user_accounts.get(user_name)
    response = fetch_emails(account, ["تحديث السكن"], "link")
    bot.send_message(message.chat.id, response)

@bot.message_handler(func=lambda message: message.text == 'طلب رمز السكن')
def handle_temporary_code(message):
    user_name = clean_text(message.from_user.username)
    account = user_accounts.get(user_name)
    response = fetch_emails(account, ["رمز الوصول المؤقت"], "link")
    bot.send_message(message.chat.id, response)

@bot.message_handler(func=lambda message: message.text == 'طلب استعادة كلمة المرور')
def handle_reset_password(message):
    user_name = clean_text(message.from_user.username)
    account = user_accounts.get(user_name)
    response = fetch_emails(account, ["إعادة تعيين كلمة المرور"], "link")
    bot.send_message(message.chat.id, response)

@bot.message_handler(func=lambda message: message.text == 'طلب رمز تسجيل الدخول')
def handle_login_code(message):
    user_name = clean_text(message.from_user.username)
    account = user_accounts.get(user_name)
    response = fetch_emails(account, ["إدخال الرمز التالي لتسجيل الدخول"], "code")
    bot.send_message(message.chat.id, response)

@bot.message_handler(func=lambda message: message.text == 'طلب رابط العضوية المعلقة')
def handle_suspended_membership(message):
    user_name = clean_text(message.from_user.username)
    account = user_accounts.get(user_name)
    response = fetch_emails(account, ["عضويتك في Netflix معلّقة"], "link")
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
