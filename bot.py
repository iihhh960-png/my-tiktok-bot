import telebot
import yt_dlp
import os
import uuid
from flask import Flask
from threading import Thread

# --- Channel Username ---
CHANNEL_ID = "@musicfan11234" 

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    app.run(host='0.0.0.0', port=10000)

TOKEN = '8542512682:AAE_P51eSPOOu3LjlN-bKeSgvL3TG-2KWFA'
bot = telebot.TeleBot(TOKEN)

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return True

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if is_subscribed(user_id):
        bot.reply_to(message, "မဂၤလာပါ! Bot ကို အသုံးျပဳနိုင္ပါၿပီ။ TikTok Link ပို႔ေပးပါခမ်")
    else:
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text="Join Our Channel", url=f"https://t.me/musicfan11234")
        markup.add(btn)
        bot.send_message(
            message.chat.id, 
            "BOT ကိုအသုံး ျပဳရန္ ကျွန်ုပ်တို့၏ Channel ကို အရင္ Join ေပးပါအုံးဗ်။Channel Join ၿပီးသြားရင္ /start ကိုျပန္ပို႔ေပးပါဗ်။", 
            reply_markup=markup
        )

@bot.message_handler(func=lambda m: True)
def download_video(message):
    user_id = message.from_user.id
    if not is_subscribed(user_id):
        start(message)
        return

    url = message.text
    if "tiktok.com" in url:
        msg = bot.reply_to(message, "Logo ေဖ်ာက္ေနပါတယ္...ခနေစာင့္ပါဗ် ")
        
        # ဖိုင္နာမည္ကို တစ္ခါနဲ႕တစ္ခါ မတူေအာင္ Random ေပးလိုက္တာပါ
        file_name = f"video_{uuid.uuid4().hex}.mp4"
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': file_name,
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            if os.path.exists(file_name):
                with open(file_name, 'rb') as video:
                    bot.send_video(message.chat.id, video, caption="ဗီဒီယို ရပါၿပီ ခမ် ")
                
                # ပို႔ၿပီးတာနဲ႕ ဖိုင္ကို ခ်က္ခ်င္းျပန္ဖ်က္မယ္
                os.remove(file_name)
                bot.delete_message(message.chat.id, msg.message_id)
            else:
                bot.edit_message_text(" ဗီဒီယိုဖိုင္ ရွာမေတြ႕ပါဘူး။ ျပန္စမ္းၾကည့္ေပးပါ။", message.chat.id, msg.message_id)
                
        except Exception as e:
            if os.path.exists(file_name): os.remove(file_name)
            bot.reply_to(message, f"တစ္ခုခု မွားေနပါတယ္😒- {str(e)}")
    else:
        bot.reply_to(message, "TikTok Link ပဲ ပို႔ေပးပါဗ်။")

if __name__ == "__main__":
    t = Thread(target=run_web)
    t.start()
    bot.polling(none_stop=True)
