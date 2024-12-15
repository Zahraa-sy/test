from flask import Flask, requests,request
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
    # Setting the webhook URL before running the Flask app
    webhook_url = f"https://mybot-bml5.onrender.com/{TOKEN}"  # Replace with your actual domain
    set_webhook_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={webhook_url}"
    response = requests.get(set_webhook_url)
    if response.status_code == 200:
        print("Webhook has been set successfully!")
    else:
        print("Failed to set webhook. Please check your API token and URL.")
    
    # Running the Flask app
    app.run(host='0.0.0.0', port=5000)
