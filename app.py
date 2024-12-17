import telebot
from telebot import types
from flask import Flask, request
import imaplib
import email
from email.header import decode_header
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

# المستخدمون المصرح بهم مع حساباتهم
allowed_users = {
    "Ray2ak": ["d41@flix1.me", "d42@flix1.me", "d43@flix1.me", "c15@flix1.me", "c23@flix1.me"],
    "Lamak_8": ["d41@flix1.me", "d42@flix1.me", "d43@flix1.me", "c15@flix1.me", "c23@flix1.me"],
    "flix511": ["e2@flix1.me"],
    "ZahraaKhabbaz": ["e2@flix1.me"]
}

# مالك البوت
OWNER_USERNAME = "Ray2ak"

user_accounts = {}

# دالة لتنظيف النص
def clean_text(text):
    return re.sub(r"[\u200f\u202c\u202b\u200e]", "", text).strip()
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

            date = msg["Date"]

            # التعامل مع الرسائل متعددة الأجزاء
            payload = None
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        payload = part.get_payload(decode=True)
                        break
            else:
                payload = msg.get_payload(decode=True)

            # فك ترميز المحتوى إذا كان موجودًا
            if payload:
                payload = payload.decode('utf-8', errors='ignore')
            else:
                payload = "لا يوجد محتوى نصي في الرسالة."

            # البحث في الموضوع
            if any(keyword in subject for keyword in search_subjects):
                messages.append(f"{subject}\n{date}\n{payload}")

        mail.logout()
        return messages

    except Exception as e:
        return [f"Error fetching emails: {e}"]

# بدء البوت
@bot.message_handler(commands=['start'])
def start_message(message):
    telegram_username = clean_text(message.from_user.username)

    if telegram_username in allowed_users or telegram_username == OWNER_USERNAME:
        bot.send_message(message.chat.id, "يرجى إدخال اسم الحساب الذي ترغب في العمل عليه:")
        bot.register_next_step_handler(message, process_account_name)
    else:
        bot.send_message(message.chat.id, "غير مصرح لك باستخدام هذا البوت.")

def process_account_name(message):
    user_name = clean_text(message.from_user.username)
    account_name = clean_text(message.text)

    if account_name in allowed_users.get(user_name, []) or user_name == OWNER_USERNAME:
        user_accounts[user_name] = account_name
        markup = types.ReplyKeyboardMarkup(row_width=1)
        btn1 = types.KeyboardButton('طلب رابط تحديث السكن')
        btn2 = types.KeyboardButton('طلب رمز السكن')
        btn3 = types.KeyboardButton('طلب استعادة كلمة المرور')
        markup.add(btn1, btn2, btn3)

        if user_name == OWNER_USERNAME:
            btn4 = types.KeyboardButton('طلب رمز تسجيل الدخول')
            btn5 = types.KeyboardButton('طلب رابط عضويتك معلقة')
            markup.add(btn4, btn5)

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
    user_email = user_accounts.get(user_name)

    if not user_email:
        bot.send_message(message.chat.id, "لم يتم تسجيل حساب. يرجى إعادة إدخال اسم الحساب.")
        return

    if message.text == 'طلب رابط تحديث السكن':
        response = fetch_emails(["مهم: كيفية تحديث السكن"], [r"نعم، أنا قدمت الطلب.*?(https?://\S+)"], user_email)
    elif message.text == 'طلب رمز السكن':
        response = fetch_emails(["رمز الوصول المؤقت من Netflix"], [r"الحصول على الرمز.*?(\d{6})"], user_email)
    elif message.text == 'طلب استعادة كلمة المرور':
        response = fetch_emails(["استكمل طلب إعادة تعيين كلمة المرور"], [r"إعادة تعيين كلمة المرور.*?(https?://\S+)"], user_email)
    elif message.text == 'طلب رمز تسجيل الدخول' and user_name == OWNER_USERNAME:
        response = fetch_emails(["Netflix: رمز تسجيل الدخول"], [r"إدخال الرمز التالي لتسجيل الدخول.*?(\d{6})"], user_email)
    elif message.text == 'طلب رابط عضويتك معلقة' and user_name == OWNER_USERNAME:
        response = fetch_emails(["عضويتك في Netflix معلّقة"], [r"إضافة معلومات الدفع.*?(https?://\S+)"], user_email)
    else:
        response = ["ليس لديك صلاحية لتنفيذ هذا الطلب."]

    if response:
        bot.send_message(message.chat.id, "\n".join(response))
    else:
        bot.send_message(message.chat.id, "لم يتم العثور على الرسالة المطلوبة.")

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
