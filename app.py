from flask import Flask,request
from config import TOKEN
from bot import bot, telebot

app = Flask(__name__)

# Webhook endpoint
@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    print("Received update:", json_string)  # Print received updates
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '', 200

if __name__ == '__main__':

    # Running the Flask app
    app.run(host='0.0.0.0', port=5000)
