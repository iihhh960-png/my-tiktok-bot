import telebot
import yt_dlp
import os
from flask import Flask
from threading import Thread

# Render မသေအောင် Port ဖွင့်ပေးခြင်း
app = Flask('')
@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

# မင်းရဲ့ Token ကို ဒီမှာ အသေထည့်ထားတယ်
TOKEN = '8363499366:AAGts06O01JOmcd2WfM_hSorTtXf8WMGEDQ'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "TikTok Link ပို့ပေးပါ၊ ၂၄ နာရီလုံး အဆင်သင့်ပါပဲ။")

@bot.message_handler(func=lambda m: True)
def download_video(message):
    url = message.text
    if "tiktok.com" in url:
        msg = bot.reply_to(message, "ဒေါင်းလုဒ်ဆွဲနေပါတယ်...")
        ydl_opts = {'format': 'best', 'outtmpl': 'vid.mp4', 'quiet': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            with open('vid.mp4', 'rb') as video:
                bot.send_video(message.chat.id, video)
            os.remove('vid.mp4')
            bot.delete_message(message.chat.id, msg.message_id)
        except Exception as e:
            bot.reply_to(message, f"Error: {str(e)}")

# Web Server ကို Background မှာ Run မယ်
Thread(target=run_web).start()

# Bot ကို စတင်မယ်
bot.polling()
