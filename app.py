import telebot
from telebot import types
from flask import Flask, request
import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
import re
import time
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
    "oscar_hrb": [
        "good20@flix1.me",
        "good18@flix1.me",
        "good19@flix1.me",
        "c91@flix1.me ",
"a94@flix1.me"
    ],
    "lp_o1": [
        "good45@flix1.me",
        "good46@flix1.me",
        "good47@flix1.me",
        "good48@flix1.me",
        "good49@flix1.me",
        "good50@flix1.me",
        "good51@flix1.me",
        "good52@flix1.me",
        "good53@flix1.me",
        "good54@flix1.me"
    ],
    "naserc5":[],
      "FaisalAli": [
        "good45@flix1.me", "good46@flix1.me", "good47@flix1.me", "good48@flix1.me",
        "good49@flix1.me", "good50@flix1.me", "good51@flix1.me", "good52@flix1.me",
        "good53@flix1.me", "good54@flix1.me"
    ],
    "Ray2ak": ["d41@flix1.me", "d42@flix1.me", "d43@flix1.me", "c15@flix1.me", "c23@flix1.me"],
    "flix511": ["d41@flix1.me", "d42@flix1.me", "d43@flix1.me", "c15@flix1.me", "c23@flix1.me", "e49@flix1.me", "d87@flix1.me", "d7@flix1.me", "yes34@flix1.me", "yes33@flix1.me",
        "good25@flix1.me", "good26@flix1.me", "good27@flix1.me", "good28@flix1.me", "good29@flix1.me",
        "good30@flix1.me", "good31@flix1.me", "good32@flix1.me", "good33@flix1.me", "good34@flix1.me",
        "a54@flix1.me", "b18@flix1.me", "e39@flix1.me", "c9@flix1.me", "c25@flix1.me",
        "d80@flix1.me", "vv3@flix1.me", "d23@flix1.me", "d57@flix1.me", "d49@flix1.me",
        "c93@flix1.me", "d19@flix1.me", "d46@flix1.me", "d18@flix1.me", "d14@flix1.me",
        "d64@flix1.me", "a61@flix1.me", "a35@flix1.me", "d24@flix1.me", "c29@flix1.me",
        "d100@flix1.me", "c11@flix1.me", "c10@flix1.me", "b23@flix1.me", "a52@flix1.me", "a53@flix1.me",    "c16@flix1.me", "d91@flix1.me", "e42@flix1.me", "a97@flix1.me", 
        "d34@flix1.me", "yes35@flix1.me", "a78@flix1.me", 
        "yes40@flix1.me", "yes39@flix1.me", "d59@flix1.me", 
        "vv1@flix1.me",  "good11@flix1.me", "good12@flix1.me", "good13@flix1.me", "good14@flix1.me", "good15@flix1.me",
        "good16@flix1.me", "good17@flix1.me", "good18@flix1.me", "good19@flix1.me", "good20@flix1.me",
        "good55@flix1.me", "good56@flix1.me", "good57@flix1.me", "good58@flix1.me", "good59@flix1.me",
        "good60@flix1.me", "good61@flix1.me", "good62@flix1.me", "good63@flix1.me", "good64@flix1.me",
        "good65@flix1.me", "good66@flix1.me", "good67@flix1.me", "good68@flix1.me", "good69@flix1.me",
        "good70@flix1.me", "good71@flix1.me", "good72@flix1.me", "good73@flix1.me", "good74@flix1.me",
        "good75@flix1.me", "good76@flix1.me", "good77@flix1.me", "good78@flix1.me", "good79@flix1.me",
        "good80@flix1.me", "good81@flix1.me", "good82@flix1.me", "good83@flix1.me", "good84@flix1.me",
        "good85@flix1.me", "good86@flix1.me", "good87@flix1.me", "good88@flix1.me", "good89@flix1.me",
        "good90@flix1.me", "yes14@flix1.me", "c44@flix1.me", "e14@flix1.me", "b4@flix1.me",
        "e57@flix1.me", "b16@flix1.me", "e27@flix1.me", "b30@flix1.me", "b31@flix1.me",
        "c80@flix1.me", "good21@flix1.me", "good22@flix1.me", "good23@flix1.me", "a38@flix1.me", "good35@flix1.me", "good36@flix1.me", "good37@flix1.me", "good38@flix1.me",
        "good39@flix1.me", "good40@flix1.me", "good41@flix1.me", "good42@flix1.me",
        "good43@flix1.me", "good44@flix1.me", "e29@flix1.me", "e23@flix1.me", "e24@flix1.me",
        "e25@flix1.me", "c24@flix1.me", "c26@flix1.me", "c27@flix1.me", "c28@flix1.me",
        "c12@flix1.me", "c8@flix1.me", "e28@flix1.me", "c13@flix1.me", "d78@flix1.me",
        "d76@flix1.me", "d97@flix1.me", "d98@flix1.me", "b73@flix1.me", "b74@flix1.me",
        "e31@flix1.me", "e32@flix1.me", "e36@flix1.me", "e37@flix1.me", "e38@flix1.me",
        "e40@flix1.me", "c63@flix1.me", "yes1@flix1.me", "d95@flix1.me", "b17@flix1.me",
        "c73@flix1.me", "c74@flix1.me", "c75@flix1.me", "c76@flix1.me", "c77@flix1.me",
        "a60@flix1.me", "b5@flix1.me", "b6@flix1.me", "b7@flix1.me", "b8@flix1.me",
        "b70@flix1.me", "b9@flix1.me", "yes2@flix1.me", "yes4@flix1.me", "yes5@flix1.me",
        "a80@flix1.me", "e44@flix1.me", "e48@flix1.me", "a51@flix1.me", "a85@flix1.me",
        "a23@flix1.me", "a86@flix1.me", "a28@flix1.me", "a29@flix1.me", "a30@flix1.me",
        "a31@flix1.me", "a32@flix1.me", "a33@flix1.me", "a34@flix1.me", "a36@flix1.me",
        "a37@flix1.me", "a1@flix1.me", "a2@flix1.me", "a3@flix1.me", "a4@flix1.me",
        "a5@flix1.me", "a6@flix1.me", "a7@flix1.me", "a8@flix1.me", "a9@flix1.me",
        "a10@flix1.me", "a12@flix1.me", "a13@flix1.me", "a14@flix1.me", "a15@flix1.me",
        "a62@flix1.me", "a63@flix1.me", "a64@flix1.me", "a66@flix1.me", "a67@flix1.me",
        "a68@flix1.me", "a69@flix1.me", "a70@flix1.me", "a71@flix1.me", "a72@flix1.me",
        "a73@flix1.me", "a75@flix1.me", "a76@flix1.me", "d72@flix1.me", "d73@flix1.me",
        "d74@flix1.me", "a16@flix1.me", "b24@flix1.me", "b26@flix1.me", "d29@flix1.me",
        "yes41@flix1.me", "yes44@flix1.me", "b27@flix1.me", "a48@flix1.me", "a49@flix1.me",
        "d51@flix1.me", "d4@flix1.me", "d5@flix1.me", "d20@flix1.me", "b85@flix1.me",
        "b87@flix1.me", "c31@flix1.me", "a27@flix1.me", "c33@flix1.me", "a20@flix1.me",
        "c41@flix1.me", "d82@flix1.me", "d84@flix1.me", "e12@flix1.me", "e13@flix1.me",
        "e15@flix1.me", "c48@flix1.me", "c62@flix1.me", "a17@flix1.me", "a18@flix1.me",
        "c79@flix1.me", "b10@flix1.me", "a46@flix1.me", "b84@flix1.me", "a47@flix1.me",
        "a93@flix1.me", "c87@flix1.me", "a42@flix1.me", "a44@flix1.me", "a45@flix1.me",
        "d8@flix1.me", "a25@flix1.me", "d11@flix1.me", "d12@flix1.me", "d53@flix1.me",
        "d55@flix1.me", "b83@flix1.me", "e26@flix1.me", "a95@flix1.me", "a96@flix1.me",
        "b11@flix1.me", "b19@flix1.me", "b20@flix1.me", "b21@flix1.me", "b22@flix1.me",
        "yes30@flix1.me", "yes31@flix1.me", "e46@flix1.me", "c55@flix1.me", "c56@flix1.me"],
    "Lamak_8": ["d41@flix1.me", "d42@flix1.me", "d43@flix1.me", "c15@flix1.me", "c23@flix1.me"],
      "mo123123mm":[
    "good35@flix1.me", "good36@flix1.me", "good37@flix1.me", "good38@flix1.me", "good39@flix1.me",
    "good40@flix1.me", "good41@flix1.me", "good42@flix1.me", "good43@flix1.me", "good44@flix1.me",
    "e29@flix1.me", "e23@flix1.me", "e24@flix1.me", "e25@flix1.me", "c24@flix1.me", "c26@flix1.me",
    "c27@flix1.me", "c28@flix1.me", "c12@flix1.me", "c8@flix1.me", "e28@flix1.me", "c13@flix1.me",
    "d78@flix1.me", "d76@flix1.me", "d97@flix1.me", "d98@flix1.me", "b73@flix1.me", "b74@flix1.me",
    "e31@flix1.me", "e32@flix1.me", "e36@flix1.me", "e37@flix1.me", "e38@flix1.me", "e40@flix1.me",
    "c63@flix1.me", "yes1@flix1.me", "d95@flix1.me", "b17@flix1.me", "c73@flix1.me", "c74@flix1.me",
    "c75@flix1.me", "c76@flix1.me", "c77@flix1.me", "a60@flix1.me", "b5@flix1.me", "b6@flix1.me",
    "b7@flix1.me", "b8@flix1.me", "b70@flix1.me", "b9@flix1.me", "yes2@flix1.me", "yes4@flix1.me",
    "yes5@flix1.me", "a80@flix1.me", "e44@flix1.me", "e48@flix1.me", "a51@flix1.me", "a85@flix1.me",
    "a23@flix1.me", "a86@flix1.me", "a28@flix1.me", "a29@flix1.me", "a30@flix1.me", "a31@flix1.me",
    "a32@flix1.me", "a33@flix1.me", "a34@flix1.me", "a36@flix1.me", "a37@flix1.me", "a1@flix1.me",
    "a2@flix1.me", "a3@flix1.me", "a4@flix1.me", "a5@flix1.me", "a6@flix1.me", "a7@flix1.me",
    "a8@flix1.me", "a9@flix1.me", "a10@flix1.me", "a12@flix1.me", "a13@flix1.me", "a14@flix1.me",
    "a15@flix1.me", "a62@flix1.me", "a63@flix1.me", "a64@flix1.me", "a66@flix1.me", "a67@flix1.me",
    "a68@flix1.me", "a69@flix1.me", "a70@flix1.me", "a71@flix1.me", "a72@flix1.me", "a73@flix1.me",
    "a75@flix1.me", "a76@flix1.me", "d72@flix1.me", "d73@flix1.me", "d74@flix1.me", "a16@flix1.me",
    "b24@flix1.me", "b26@flix1.me", "d29@flix1.me", "yes41@flix1.me", "yes44@flix1.me", "b27@flix1.me",
    "a48@flix1.me", "a49@flix1.me", "d51@flix1.me", "d4@flix1.me", "d5@flix1.me", "d20@flix1.me",
    "b85@flix1.me", "b87@flix1.me", "c31@flix1.me", "a27@flix1.me", "c33@flix1.me", "a20@flix1.me",
    "c41@flix1.me", "d82@flix1.me", "d84@flix1.me", "e12@flix1.me", "e13@flix1.me", "e15@flix1.me",
    "c48@flix1.me", "c62@flix1.me", "a17@flix1.me", "a18@flix1.me", "c79@flix1.me", "b10@flix1.me",
    "a46@flix1.me", "b84@flix1.me", "a47@flix1.me", "a93@flix1.me", "c87@flix1.me", "a42@flix1.me",
    "a44@flix1.me", "a45@flix1.me", "d8@flix1.me", "a25@flix1.me", "d11@flix1.me", "d12@flix1.me",
    "d53@flix1.me", "d55@flix1.me", "b83@flix1.me", "e26@flix1.me", "a95@flix1.me", "a96@flix1.me",
    "b11@flix1.me", "b19@flix1.me", "b20@flix1.me", "b21@flix1.me", "b22@flix1.me", "yes30@flix1.me",
    "yes31@flix1.me", "e46@flix1.me", "c55@flix1.me", "c56@flix1.me", "a55@flix1.me", "a56@flix1.me",
    "a57@flix1.me", "a58@flix1.me", "a59@flix1.me", "a84@flix1.me", "a87@flix1.me", "a89@flix1.me",
    "a88@flix1.me", "a90@flix1.me", "a91@flix1.me", "a92@flix1.me", "b2@flix1.me", "b3@flix1.me",
    "b33@flix1.me", "b34@flix1.me", "b35@flix1.me", "b36@flix1.me", "b37@flix1.me", "b38@flix1.me",
    "b39@flix1.me", "b40@flix1.me", "b41@flix1.me", "b42@flix1.me", "b43@flix1.me", "b44@flix1.me",
    "b45@flix1.me", "b46@flix1.me", "b47@flix1.me", "b48@flix1.me", "b49@flix1.me", "b50@flix1.me",
    "b51@flix1.me", "b52@flix1.me", "b62@flix1.me", "b63@flix1.me", "b64@flix1.me", "b65@flix1.me",
    "b66@flix1.me", "c94@flix1.me", "c95@flix1.me", "c96@flix1.me", "c97@flix1.me", "c98@flix1.me",
    "c99@flix1.me", "d1@flix1.me", "d2@flix1.me", "d77@flix1.me", "d6@flix1.me", "d3@flix1.me",
    "c67@flix1.me", "d60@flix1.me", "d62@flix1.me", "d64@flix1.me", "d65@flix1.me", "b78@flix1.me",
    "b79@flix1.me", "d41@flix1.me", "d42@flix1.me", "d43@flix1.me", "c15@flix1.me", "c23@flix1.me",
    "e1@flix1.me", "e2@flix1.me", "b75@flix1.me", "b76@flix1.me", "e33@flix1.me", "e34@flix1.me",
    "e35@flix1.me", "e16@flix1.me", "e17@flix1.me", "e18@flix1.me", "e19@flix1.me", "yes6@flix1.me",
    "yes7@flix1.me", "yes8@flix1.me", "c3@flix1.me", "c4@flix1.me", "c5@flix1.me", "b96@flix1.me",
    "b100@flix1.me", "a79@flix1.me", "b14@flix1.me", "d35@flix1.me", "d36@flix1.me", "d37@flix1.me",
    "d15@flix1.me", "d16@flix1.me", "d13@flix1.me", "d38@flix1.me", "d39@flix1.me", "e52@flix1.me",
    "d63@flix1.me", "a61@flix1.me", "a35@flix1.me"
],
    "shebak007": [
    "good55@flix1.me", "good56@flix1.me", "good57@flix1.me", "good58@flix1.me", "good59@flix1.me",
    "good60@flix1.me", "good61@flix1.me", "good62@flix1.me", "good63@flix1.me", "good64@flix1.me",
    "good65@flix1.me", "good66@flix1.me", "good67@flix1.me", "good68@flix1.me", "good69@flix1.me",
    "good70@flix1.me", "good71@flix1.me", "good72@flix1.me", "good73@flix1.me", "good74@flix1.me",
    "good75@flix1.me", "good76@flix1.me", "good77@flix1.me", "good78@flix1.me", "good79@flix1.me",
    "good80@flix1.me", "good81@flix1.me", "good82@flix1.me", "good83@flix1.me", "good84@flix1.me",
    "good85@flix1.me", "good86@flix1.me", "good87@flix1.me", "good88@flix1.me", "good89@flix1.me",
    "good90@flix1.me", "yes14@flix1.me", "c44@flix1.me", "e14@flix1.me", "b4@flix1.me",
    "e57@flix1.me", "b16@flix1.me", "e27@flix1.me", "b30@flix1.me", "b31@flix1.me",
    "c80@flix1.me", "good21@flix1.me", "good22@flix1.me", "good23@flix1.me", "good24@flix1.me",
    "a11@flix1.me", "a38@flix1.me", "b11@flix1.me", "c54@flix1.me", "b88@flix1.me",
    "c45@flix1.me", "yes38@flix1.me", "d62@flix1.me", "b99@flix1.me", "b97@flix1.me",
    "b94@flix1.me", "b95@flix1.me", "a50@flix1.me", "yes24@flix1.me", "d79@flix1.me",
    "yes37@flix1.me", "d83@flix1.me", "d10@flix1.me", "b55@flix1.me", "c85@flix1.me",
    "d54@flix1.me", "a43@flix1.me", "c53@flix1.me", "e11@flix1.me", "c34@flix1.me",
    "c65@flix1.me", "b86@flix1.me", "a82@flix1.me", "c78@flix1.me", "a40@flix1.me",
    "c61@flix1.me", "yes10@flix1.me", "e3@flix1.me", "e53@flix1.me", "good1@flix1.me",
    "good2@flix1.me", "good3@flix1.me", "good4@flix1.me", "good5@flix1.me", "good6@flix1.me",
    "good8@flix1.me", "good9@flix1.me", "d99@flix1.me", "a77@flix1.me", "e47@flix1.me",
    "b54@flix1.me", "b61@flix1.me", "b72@flix1.me", "b29@flix1.me", "b67@flix1.me",
    "c86@flix1.me"
],
    "madm0nn": [
        "c16@flix1.me",
        "d91@flix1.me",
        "e42@flix1.me",
        "a97@flix1.me",
        "d34@flix1.me",
        "yes35@flix1.me",
        "a78@flix1.me",
        "yes40@flix1.me",
        "yes39@flix1.me",
        "d59@flix1.me",
        "vv1@flix1.me"
    ],
      "o707mar": [
        "good25@flix1.me",
        "good26@flix1.me",
        "good27@flix1.me",
        "good28@flix1.me",
        "good29@flix1.me",
        "good30@flix1.me",
        "good31@flix1.me",
        "good32@flix1.me",
        "good33@flix1.me",
        "good34@flix1.me",
        "a54@flix1.me",
        "b18@flix1.me",
        "e39@flix1.me",
        "c9@flix1.me",
        "c25@flix1.me",
        "d80@flix1.me",
        "vv3@flix1.me",
        "d23@flix1.me",
        "d57@flix1.me",
        "d49@flix1.me",
        "c93@flix1.me",
        "d19@flix1.me",
        "d46@flix1.me",
        "d18@flix1.me",
        "d14@flix1.me",
        "d64@flix1.me",
        "a61@flix1.me",
        "a35@flix1.me",
        "d24@flix1.me",
        "c29@flix1.me",
        "d100@flix1.me",
        "c11@flix1.me",
        "c10@flix1.me",
        "e49@flix1.me",
        "d87@flix1.me",
        "d7@flix1.me",
        "yes34@flix1.me",
        "yes33@flix1.me",
        "b23@flix1.me",
        "a52@flix1.me",
        "a53@flix1.me"
    ],
}
accounts_for_sale = []
user_accounts = {}
subscribers =  [7304537096,7177902677, 7242814551,502281152,6766780038, 971651970,5520714242]

# دالة لتنظيف النص
def clean_text(text):
    return text.strip()

# فتح اتصال البريد مرة واحدة
mail = imaplib.IMAP4_SSL(IMAP_SERVER)
mail.login(EMAIL, PASSWORD)
# دالة إعادة المحاولة عند حدوث أخطاء
def retry_imap_connection():
    global mail
    for attempt in range(3):
        try:
            mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            mail.login(EMAIL, PASSWORD)
            print("✅ اتصال IMAP ناجح.")
            return
        except Exception as e:
            print(f"❌ فشل الاتصال (المحاولة {attempt + 1}): {e}")
            time.sleep(2)
    print("❌ فشل إعادة الاتصال بعد عدة محاولات.")

# دالة إعادة المحاولة عند حدوث أخطاء
def retry_on_error(func):
    def wrapper(*args, **kwargs):
        retries = 3
        for attempt in range(retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if "EOF occurred" in str(e) or "socket" in str(e):
                    time.sleep(2)
                    print(f"Retrying... Attempt {attempt + 1}/{retries}")
                else:
                    return f"Error fetching emails: {e}"
        return "Error: Failed after multiple retries."
    return wrapper

# تغليف دوال جلب البيانات بدالة إعادة المحاولة
@retry_on_error
def fetch_email_with_link(account, subject_keywords, button_text):
    retry_imap_connection()
    try:
        mail.select("inbox")
        _, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()[-5:]

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
    retry_imap_connection()
    try:
        mail.select("inbox")
        _, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()[-5:]

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
        
# توابع معالجة الطلبات
def handle_request_async(chat_id, account, message_text):
    if message_text == 'طلب رابط تحديث السكن':
        response = fetch_email_with_link(account, ["تحديث السكن"], "نعم، أنا قدمت الطلب")
    elif message_text == 'طلب رمز السكن':
        response = fetch_email_with_link(account, ["رمز الوصول المؤقت"], "الحصول على الرمز")
    elif message_text == 'طلب استعادة كلمة المرور':
        response = fetch_email_with_link(account, ["إعادة تعيين كلمة المرور"], "إعادة تعيين كلمة المرور")
    elif message_text == 'طلب رمز تسجيل الدخول':
        response = fetch_email_with_code(account, ["رمز تسجيل الدخول"])
    elif message_text == 'طلب رابط عضويتك معلقة':
        response = fetch_email_with_link(account, ["عضويتك في Netflix معلّقة"], "إضافة معلومات الدفع")
    else:
        response = "ليس لديك صلاحية لتنفيذ هذا الطلب."

    bot.send_message(chat_id, response)

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
            types.KeyboardButton('عرض الحسابات المرتبطة بي'),
            types.KeyboardButton('عرض الحسابات المعروضة للبيع')
        ]
        if user_name in admin_users:
            btns.extend([
                types.KeyboardButton('طلب رمز تسجيل الدخول'),
                types.KeyboardButton('طلب رابط عضويتك معلقة'),
                types.KeyboardButton('إضافة حسابات للبيع'),
                types.KeyboardButton('عرض الحسابات للبيع'),
                types.KeyboardButton('إضافة حسابات لمستخدم'),
                types.KeyboardButton('حذف حسابات من المعروضة للبيع'),
                types.KeyboardButton('حذف حسابات من مستخدم'), 
                types.KeyboardButton('إرسال رسالة جماعية')  # زر جديد لإرسال رسالة جماعية
            ])
        markup.add(*btns)
        bot.send_message(message.chat.id, "اختر العملية المطلوبة:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "اسم الحساب غير موجود ضمن الحسابات المصرح بها.")


@bot.message_handler(func=lambda message: message.text in [
    'طلب رابط تحديث السكن', 'طلب رمز السكن', 'طلب استعادة كلمة المرور',
    'طلب رمز تسجيل الدخول', 'طلب رابط عضويتك معلقة', 'إرسال رسالة جماعية'
])
def handle_requests(message):
    user_name = clean_text(message.from_user.username)
    account = user_accounts.get(user_name)
    if message.text == 'إرسال رسالة جماعية' and user_name in admin_users:
        handle_broadcast_request(message)
        return

    if not account:
        bot.send_message(message.chat.id, "لم يتم تحديد حساب بعد.")
        return

    bot.send_message(message.chat.id, "جاري الطلب...")
    thread = threading.Thread(target=handle_request_async, args=(message.chat.id, account, message.text))
    thread.start()
@bot.message_handler(func=lambda message: message.text == 'إضافة حسابات للبيع' and message.from_user.username in admin_users)
def add_accounts_for_sale(message):
    bot.send_message(message.chat.id, "📝 الرجاء إدخال الحسابات (كل حساب في سطر):")
    bot.register_next_step_handler(message, save_accounts_for_sale)

def save_accounts_for_sale(message):
    new_accounts = message.text.strip().split('\n')  # فصل الحسابات بناءً على السطور
    accounts_for_sale.extend(new_accounts)  # إضافة الحسابات إلى القائمة
    bot.send_message(message.chat.id, "✅ تم إضافة الحسابات إلى قائمة البيع بنجاح.")

@bot.message_handler(func=lambda message: message.text == 'عرض الحسابات للبيع' and message.from_user.username in admin_users)
def show_accounts_for_sale(message):
    if not accounts_for_sale:
        bot.send_message(message.chat.id, "❌ لا توجد حسابات متوفرة للبيع حاليًا.")
    else:
        accounts_text = "\n".join(accounts_for_sale)  # تحويل القائمة إلى سلسلة نصوص
        bot.send_message(message.chat.id, f"📋 الحسابات المتوفرة للبيع:\n{accounts_text}")
# التعامل مع إرسال الرسائل الجماعية من قبل الأدمن
@bot.message_handler(func=lambda message: message.text == 'إرسال رسالة جماعية' and message.from_user.username in admin_users)
def handle_broadcast_request(message):
    bot.send_message(message.chat.id, "اكتب الرسالة التي تريد إرسالها لجميع المشتركين:")
    bot.register_next_step_handler(message, send_broadcast_message)

def send_broadcast_message(message):
    broadcast_text = message.text
    for chat_id in subscribers:
        try:
            bot.send_message(chat_id, f"📢 رسالة من الإدارة:\n{broadcast_text}")
        except Exception as e:
            print(f"فشل الإرسال إلى {chat_id}: {e}")
    bot.send_message(message.chat.id, "✅ تم إرسال الرسالة إلى جميع المشتركين بنجاح.")
@bot.message_handler(func=lambda message: message.text == 'حذف حسابات من مستخدم' and message.from_user.username in admin_users)
def delete_user_accounts_start(message):
    bot.send_message(message.chat.id, "📝 الرجاء إدخال اسم المستخدم:")
    bot.register_next_step_handler(message, handle_user_deletion_choice)

def handle_user_deletion_choice(message):
    user_to_edit = message.text.strip()
    if user_to_edit not in allowed_users:
        bot.send_message(message.chat.id, "❌ المستخدم غير موجود في قائمة المستخدمين المسموح لهم.")
        return

    # عرض الخيارات للأدمن
    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    btns = [
        types.KeyboardButton('حذف جميع الحسابات'),
        types.KeyboardButton('حذف حسابات محددة')
    ]
    markup.add(*btns)
    bot.send_message(message.chat.id, "⚙️ اختر الإجراء المطلوب:", reply_markup=markup)
    bot.register_next_step_handler(message, handle_deletion_action, user_to_edit)

def handle_deletion_action(message, user_to_edit):
    if message.text == 'حذف جميع الحسابات':
        delete_all_accounts(user_to_edit, message.chat.id)
    elif message.text == 'حذف حسابات محددة':
        bot.send_message(message.chat.id, "📝 الرجاء إدخال الحسابات التي تريد حذفها (كل حساب في سطر):")
        bot.register_next_step_handler(message, delete_specific_accounts, user_to_edit)
    else:
        bot.send_message(message.chat.id, "❌ خيار غير صحيح. الرجاء المحاولة مجددًا.")

def delete_all_accounts(user_to_edit, chat_id):
    allowed_users.pop(user_to_edit, None)  # حذف المستخدم وكل حساباته
    bot.send_message(chat_id, f"✅ تم حذف المستخدم {user_to_edit} وجميع حساباته بنجاح.")

def delete_specific_accounts(message, user_to_edit):
    accounts_to_delete = message.text.strip().split('\n')  # فصل الحسابات بناءً على السطور
    if user_to_edit in allowed_users:
        current_accounts = allowed_users[user_to_edit]
        for account in accounts_to_delete:
            if account in current_accounts:
                current_accounts.remove(account)  # حذف الحساب من قائمة المستخدم

        # تحديث القائمة
        if not current_accounts:  # إذا أصبحت القائمة فارغة، حذف المستخدم
            allowed_users.pop(user_to_edit, None)
            bot.send_message(message.chat.id, f"✅ تم حذف جميع الحسابات من المستخدم {user_to_edit} وحذف المستخدم من القائمة.")
        else:
            allowed_users[user_to_edit] = current_accounts
            bot.send_message(message.chat.id, f"✅ تم حذف الحسابات المحددة من المستخدم {user_to_edit}.")
    else:
        bot.send_message(message.chat.id, "❌ المستخدم غير موجود أو لا يملك أي حسابات.")


@bot.message_handler(func=lambda message: message.text == 'عرض الحسابات المرتبطة بي')
def show_user_accounts(message):
    user_name = clean_text(message.from_user.username)
    if user_name in allowed_users and allowed_users[user_name]:
        accounts = allowed_users[user_name]
        response = "✅ الحسابات المرتبطة بك:\n" + "\n".join(accounts)
    else:
        response = "❌ لا توجد حسابات مرتبطة بحسابك."
    bot.send_message(message.chat.id, response)


@bot.message_handler(func=lambda message: message.text == 'عرض الحسابات المعروضة للبيع')
def show_accounts_for_sale(message):
    if accounts_for_sale:
        response = "📋 الحسابات المعروضة للبيع:\n" + "\n".join(accounts_for_sale)
    else:
        response = "❌ لا توجد حسابات معروضة للبيع حاليًا."
    bot.send_message(message.chat.id, response)

@bot.message_handler(func=lambda message: message.text == 'حذف حسابات من المعروضة للبيع' and message.from_user.username in admin_users)
def remove_accounts_from_sale(message):
    bot.send_message(message.chat.id, "📝 أرسل الحسابات التي تريد حذفها من المعروضة للبيع (حساب بكل سطر):")
    bot.register_next_step_handler(message, process_accounts_removal)

def process_accounts_removal(message):
    accounts_to_remove = message.text.split("\n")  # قراءة الحسابات كمجموعة نصوص
    removed_accounts = []
    not_found_accounts = []

    for account in accounts_to_remove:
        account = account.strip()
        if account in accounts_for_sale:
            accounts_for_sale.remove(account)
            removed_accounts.append(account)
        else:
            not_found_accounts.append(account)

    # إعداد الرد
    response = "✅ الحسابات التالية تم حذفها بنجاح:\n" + "\n".join(removed_accounts) if removed_accounts else "❌ لم يتم حذف أي حساب."
    if not_found_accounts:
        response += "\n\n⚠️ الحسابات التالية لم يتم العثور عليها:\n" + "\n".join(not_found_accounts)

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
