import telebot
import yt_dlp
import os
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
        bot.reply_to(message, "မင်္ဂလာပါ! Bot ကို အသုံးပြုနိုင်ပါပြီ။ TikTok Link ပို့ပေးပါခမျ")
    else:
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text="Join Our Channel", url=f"https://t.me/musicfan11234")
        markup.add(btn)
        bot.send_message(
            message.chat.id, 
            "BOT ကိုအသုံး ပြုရန် ကြှနျုပျတို့၏ Channel ကို အရင် Join ပေးပါအုံးဗျ။Channel Join ပြီးသွားရင် /start ကိုပြန်ပို့ပေးပါဗျ။", 
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
        msg = bot.reply_to(message, "Logo ဖျောက်နေပါတယ်...ခနစောင့်ပါဗျ ")
        
        # Slideshow ရော Video ရော အဆင်ပြေအောင် Option ကို ပြင်ထားတယ်
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': 'vid.mp4',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        try:
            if os.path.exists('vid.mp4'): os.remove('vid.mp4')
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            with open('vid.mp4', 'rb') as video:
                bot.send_video(message.chat.id, video, caption="ဗီဒီယို ရပါပြီ ခမျ ")
            
            os.remove('vid.mp4')
            bot.delete_message(message.chat.id, msg.message_id)
        except Exception as e:
            # Slideshow ဖြစ်နေရင် သီးသန့် error ပြပေးမယ်
            if "extract_info" in str(e) or "7593" in str(e):
                bot.edit_message_text(" ဒါက Image Slideshow ဖြစ်နေလို့ Video အနေနဲ့ ဒေါင်းလို့မရပါဘူးဗျ။ Video လင့်ခ်နဲ့ ပြန်စမ်းပေးပါဦး။", message.chat.id, msg.message_id)
            else:
                bot.reply_to(message, f"တစ်ခုခု မှားနေပါတယ်😒- {str(e)}")
    else:
        bot.reply_to(message, "TikTok Link ပဲ ပို့ပေးပါဗျ။")

if __name__ == "__main__":
    t = Thread(target=run_web)
    t.start()
    bot.polling(none_stop=True)
