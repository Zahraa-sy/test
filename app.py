import telebot
import requests
from telebot import types


TOKEN = "7801426148:AAERaD89BYEKegqGSi8qSQ-Xooj8yJs41I4"  # تأكد من أن التوكن صحيح
bot = telebot.TeleBot(TOKEN)


# Function to load JSON data from a URL
def load_json_data(url):
    response = requests.get(url)
    return response.json()


# رابط JSON يحتوي على أسماء مستخدمي تيليجرام
url_telegram_users = "https://script.google.com/macros/s/AKfycbwMF9ajqKdnX7m3caoympN5NxYc3RrSg7VJ5cbuDxQvIrlv9x575LLeitFkrGnN0g4ZiQ/exec"  # استبدل برابط JSON الخاص بأسماء مستخدمي تيليجرام
# رابط JSON يحتوي على الأسماء المصرح بها
url_allowed_names = "https://script.google.com/macros/s/AKfycbyLB7vThO7b5YOYn8dJS6iIM1DPHBXy51NNOa9qGPKYKz6X_eixIxEYqY5EKCw57KpyVg/exec"  # استبدل برابط JSON الخاص بالأسماء المصرح بها
url_extract_messages = "https://script.google.com/macros/s/AKfycbwzC864OmqKdb76i12j2-b6heUKSu6nhGqrRZuB-KaidsopI-ICI8_pWTehmHJFA6LC7Q/exec?action=importLatestMessagesFromToday"  # رابط extract_messages
# رابط JSON يحتوي على بيانات الرسائل
url_messages = "https://script.google.com/macros/s/AKfycbwzC864OmqKdb76i12j2-b6heUKSu6nhGqrRZuB-KaidsopI-ICI8_pWTehmHJFA6LC7Q/exec?action=getFirstTenMessages"  # استبدل برابط JSON الخاص بالرسائل

# تحميل أسماء مستخدمي تيليجرام عند بدء تشغيل البوت
data_telegram_users = load_json_data(url_telegram_users)
telegram_users = [item['username'] for item in data_telegram_users['telegram_users']]

# تحميل الأسماء المصرح بها عند بدء تشغيل البوت
data_allowed_names = load_json_data(url_allowed_names)
allowed_names_accounts = data_allowed_names['allowed_names']

@bot.message_handler(commands=['start'])
def start_message(message):
    telegram_username = message.from_user.username.strip()  # الحصول على اسم المستخدم في تيليجرام

    if telegram_username in telegram_users:
        bot.send_message(message.chat.id, "مرحبًا بك في البوت!")
        bot.send_message(message.chat.id, "يرجى إدخال اسم الحساب")
        bot.register_next_step_handler(message, process_name)
    else:
        bot.send_message(message.chat.id, "غير مصرح لك للاستخدام هذا البوت.")

def process_name(message):
    global user_name, user_account  # استخدام المتغيرات العالمية لتخزين الاسم المدخل واسم الحساب

    user_name = message.from_user.username.strip()  # الحصول على اسم المستخدم
    user_account = message.text.strip()  # الحصول على الحساب المدخل

    # تحقق مما إذا كان اسم المستخدم والحساب موجودين في البيانات المصرح بها
    for account in allowed_names_accounts:
        if account['username'] == user_name and user_account in account['accounts']:
            bot.send_message(message.chat.id, f"شكرًا، {user_name}")
            
            # زر الحصول على الرسالة
            markup = types.ReplyKeyboardMarkup(row_width=1)
            btn_get_message = types.KeyboardButton('الحصول على الرسالة')
            markup.add(btn_get_message)

            bot.send_message(message.chat.id, "اضغط على الزر للحصول على الرسالة:", reply_markup=markup)
            return

    # إذا لم يكن الحساب صالحًا، اطلب إعادة المحاولة
    bot.send_message(message.chat.id, "الحساب ليس لك. يرجى إدخال اسم حساب جديد.")
    bot.register_next_step_handler(message, process_name)  # إعادة تسجيل الخطوة التالية

@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_name = message.from_user.username.strip()
    
    if user_name not in telegram_users:
        bot.send_message(message.from_user.id, "عذرًا، ليس لديك إذن لاستخدام هذا البوت.")
        return

    if message.text == 'الحصول على الرسالة':
        # استدعاء رابط extract_messages لتشغيل دالة importLatestMessagesFromToday في Google Apps Script
        response = requests.get(url_extract_messages)
        
        if response.status_code == 200:
            bot.send_message(message.chat.id, "تم استيراد الرسائل بنجاح.")
            
            # إنشاء الأزرار الثلاثة بعد استيراد الرسائل
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
        messages_data = data_messages['messages']  
        
        # ابحث عن الرسائل التي تتعلق بالاسم المدخل (user_account)
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

# ابدأ تشغيل البوت
if __name__ == '__main__':
    bot.polling(none_stop=True)