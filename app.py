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

# دالة لتنظيف النص من الأحرف غير المرئية
def clean_text(text):
    return re.sub(r"[\u200f\u202c\u202b\u200e]", "", text).strip()

# دالة للاتصال بالبريد الإلكتروني وجلب الرسائل
def fetch_latest_email(account, subject_keywords, extract_function):
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
                        soup = BeautifulSoup(html_content, 'html.parser')
                        result = extract_function(soup)
                        if result:
                            mail.logout()
                            return result

        mail.logout()
        return "لم يتم العثور على الرسالة المطلوبة."

    except Exception as e:
        return f"Error fetching emails: {e}"

# دوال استخراج البيانات
def extract_update_address_link(soup):
    for a in soup.find_all('a', href=True):
        if 'نعم، أنا قدمت الطلب' in a.get_text():
            return a['href']
    return "لم يتم العثور على رابط تحديث السكن."

def extract_temporary_code_link(soup):
    for a in soup.find_all('a', href=True):
        if 'الحصول على الرمز' in a.get_text():
            return a['href']
    return "لم يتم العثور على رابط رمز السكن."

def extract_reset_password_link(soup):
    for a in soup.find_all('a', href=True):
        if 'إعادة تعيين كلمة المرور' in a.get_text():
            return a['href']
    return "لم يتم العثور على رابط استعادة كلمة المرور."

def extract_login_code(soup):
    code_match = re.search(r'\b\d{4}\b', soup.get_text())
    return code_match.group(0) if code_match else "لم يتم العثور على رمز تسجيل الدخول."

def extract_suspended_membership_link(soup):
    for a in soup.find_all('a', href=True):
        if 'إضافة معلومات الدفع' in a.get_text():
            return a['href']
    return "لم يتم العثور على رابط العضوية المعلقة."

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
