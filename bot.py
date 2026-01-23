import telebot
import requests
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
        bot.reply_to(message, "မင်္ဂလာပါ! Bot ကို အသုံးပြုနိုင်ပါပြီ။ TikTok Link ပို့ပေးပါခမျ🥰")
    else:
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text="Join Our Channel", url=f"https://t.me/musicfan11234")
        markup.add(btn)
        bot.send_message(
            message.chat.id, 
            "BOT ကိုအသုံး ပြုရန် ကျွန်​ေတာ်တို့၏ Channel ကို အရင် Join ပေးပါအုံးဗျ။Channel Join ပြီးသွားရင် /start ကိုပြန်ပို့ပေးပါဗျ🥰။", 
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
        msg = bot.reply_to(message, "Logo ဖျောက်နေပါတယ်...ခနစောင့်ပါဗျ🥱 ")
        
        try:
            # TikTok API သုံးပြီး Video Link ရှာခြင်း
            api_url = f"https://www.tikwm.com/api/?url={url}"
            response = requests.get(api_url).json()
            
            if response.get('code') == 0:
                video_url = response['data']['play'] # No Watermark video
                file_name = f"video_{uuid.uuid4().hex}.mp4"
                
                # ဗီဒီယိုကို ဒေါင်းလုဒ်ဆွဲခြင်း
                video_data = requests.get(video_url).content
                with open(file_name, 'wb') as f:
                    f.write(video_data)
                
                # ဗီဒီယိုပို့ခြင်း
                with open(file_name, 'rb') as video:
                    bot.send_video(message.chat.id, video, caption="ဗီဒီယို ရပါပြီ ခမျ ")
                
                os.remove(file_name)
                bot.delete_message(message.chat.id, msg.message_id)
            else:
                bot.edit_message_text(" ဗီဒီယို ဒေါင်းလုဒ်ဆွဲလို့ မရပါဘူး။ Link မှန်ရဲ့လား ပြန်စစ်ပေးပါ။", message.chat.id, msg.message_id)
                
        except Exception as e:
            bot.reply_to(message, f"အမှားတစ်ခုရှိနေပါတယ်😒- {str(e)}")
    else:
        bot.reply_to(message, "TikTok Link ပဲ ပို့ပေးပါဗျ😶။")

if __name__ == "__main__":
    t = Thread(target=run_web)
    t.start()
    bot.polling(none_stop=True)
