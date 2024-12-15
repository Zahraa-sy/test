import telebot
from telebot import types
import requests
from config import TOKEN, url_telegram_users, url_allowed_names, url_extract_messages, url_messages

bot = telebot.TeleBot(TOKEN)


# Function to load JSON data from a URL
def load_json_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error loading data from {url}: {e}")
        return {}


# تحميل أسماء مستخدمي تيليجرام
data_telegram_users = load_json_data(url_telegram_users)
telegram_users = [item['username'] for item in data_telegram_users.get('telegram_users', [])]

# تحميل الأسماء المصرح بها
data_allowed_names = load_json_data(url_allowed_names)
allowed_names_accounts = data_allowed_names.get('allowed_names', [])

@bot.message_handler(commands=['start'])
def start_message(message):
    telegram_username = message.from_user.username.strip()  
    if telegram_username in telegram_users:
        bot.send_message(message.chat.id, "مرحبًا بك في البوت!")
        bot.send_message(message.chat.id, "يرجى إدخال اسم الحساب")
        bot.register_next_step_handler(message, process_name)
    else:
        bot.send_message(message.chat.id, "غير مصرح لك للاستخدام هذا البوت.")

def process_name(message):
    user_name = message.from_user.username.strip()
    user_account = message.text.strip()
    
    # تحقق مما إذا كان الحساب موجودًا
    for account in allowed_names_accounts:
        if account['username'].lower() == user_name.lower() and user_account in account['accounts']:
            bot.send_message(message.chat.id, f"شكرًا، {user_name}")
            markup = types.ReplyKeyboardMarkup(row_width=1)
            btn_get_message = types.KeyboardButton('الحصول على الرسالة')
            markup.add(btn_get_message)
            bot.send_message(message.chat.id, "اضغط على الزر للحصول على الرسالة:", reply_markup=markup)
            return
#---------
    # إذا لم يكن الحساب صالحًا، اطلب إعادة المحاولة
    bot.send_message(message.chat.id, "الحساب ليس لك. يرجى إدخال اسم حساب جديد.")
    bot.send_message(message.chat.id, "يرجى استخدام الأمر /start لإعادة البدء.")
    #  المستخدم يستخدم الأمر /start لإعادة البدء

#-------
@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_name = message.from_user.username.strip()
    
    if user_name not in telegram_users:
        bot.send_message(message.from_user.id, "عذرًا، ليس لديك إذن لاستخدام هذا البوت.")
        return

    if message.text == 'الحصول على الرسالة':
        response = requests.get(url_extract_messages)
        
        if response.status_code == 200:
            bot.send_message(message.chat.id, "تم استيراد الرسائل بنجاح.")
            markup = types.ReplyKeyboardMarkup(row_width=2)
            btn1 = types.KeyboardButton('استكمل طلب إعادة تعيين كلمة المرور الخاصة بك')
            btn2 = types.KeyboardButton('مهم: كيفية تحديث السكن الذي يستخدم Netflix')
            btn3 = types.KeyboardButton('رمز الوصول المؤقت من Netflix')
            markup.add(btn1, btn2, btn3)
            bot.send_message(message.chat.id, "يرجى اختيار الزر المناسب لك", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "فشل في استيراد الرسائل.")
    
    elif message.text in [
        'استكمل طلب إعادة تعيين كلمة المرور الخاصة بك',
        'مهم: كيفية تحديث السكن الذي يستخدم Netflix',
        'رمز الوصول المؤقت من Netflix'
    ]:
        data_messages = load_json_data(url_messages)
        messages_data = data_messages.get('messages', [])
        user_account = message.text.strip()
        
        user_messages = [item for item in messages_data if item['to'] == user_account]
        
        if user_messages:
            relevant_messages = [item for item in user_messages if item['subject'] == message.text]
            if relevant_messages:
                latest_relevant_message = relevant_messages[-1]
                bot.send_message(message.chat.id, f"{latest_relevant_message['body']}\n{latest_relevant_message['date']}")
            else:
                bot.send_message(message.chat.id, "ليس لديك رسالة بالعنوان المطلوب.")
        else:
            bot.send_message(message.chat.id, "ليس لديك رسائل.")