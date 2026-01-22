import telebot
import yt_dlp
import os
from flask import Flask
from threading import Thread

# Render Health Check server
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

# မင်းပေးထားတဲ့ Token အသစ်ကို ဒီမှာ ထည့်ထားပါတယ်
TOKEN = '8542512682:AAE_P51eSPOOu3LjlN-bKeSgvL3TG-2KWFA'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "%username% မင်္ဂလာပါ! TikTok Link ပို့ပေးပါ၊ ဒေါင်းလုဒ်ဆွဲပေးပါ့မယ် ခမျ🤗")

@bot.message_handler(func=lambda m: True)
def download_video(message):
    url = message.text
    if "tiktok.com" in url:
        msg = bot.reply_to(message, "ဒေါင်းလုဒ်ဆွဲနေပါတယ်... ခဏစောင့်ပေးပါ🥱 ")
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'vid.mp4',
            'quiet': True,
            'no_warnings': True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            with open('vid.mp4', 'rb') as video:
                bot.send_video(message.chat.id, video, caption="ဗီဒီယို ရပါပြီ ခမျ🥰 ")
            os.remove('vid.mp4')
            bot.delete_message(message.chat.id, msg.message_id)
        except Exception as e:
            bot.reply_to(message, f"အမှားအယွင်းတစ်ခု ရှိနေပါတယ်- {str(e)}")
    else:
        bot.reply_to(message, "TikTok Link ပဲ ပို့ပေးပါဗျာ။")

if __name__ == "__main__":
    # Start web server
    t = Thread(target=run_web)
    t.start()
    # Start bot
    print("Bot is starting...")
    bot.polling(none_stop=True)
