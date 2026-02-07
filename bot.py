import telebot
import requests
import os
import uuid
import time
from flask import Flask
from threading import Thread

# --- Bot Configuration ---
TOKEN = '8542512682:AAE_P51eSPOOu3LjlN-bKeSgvL3TG-2KWFA'
CHANNEL_ID = "https://t.me/JoKeR_FaN1"
bot = telebot.TeleBot(TOKEN)
app = Flask('')

# --- Unicode Emojis (Code ပြောင်းထားသော စာသားများ) ---
EMOJI_SMILE = "\U0001F917"   # 🤗
EMOJI_WAIT = "\U0001F971"    # 🥱
EMOJI_LOVE = "\U0001F970"    # 🥰
EMOJI_WARNING = "\u26A0\uFE0F" # ⚠️

@app.route('/')
def home():
    return "Bot is running perfectly!"

def run_web():
    app.run(host='0.0.0.0', port=10000)

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
        bot.reply_to(message, f"မင်္ဂလာပါ{EMOJI_SMILE}! Bot ကို အသုံးပြုနိုင်ပါပြီ။ TikTok Link ပို့ပေးပါခမျ")
    else:
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text="Join Our Channel", url=f"https://t.me/musicfan11234")
        markup.add(btn)
        bot.send_message(message.chat.id, f"BOT ကိုအသုံး ပြုရန် ကျွန်ုပ်တို့၏ Channel ကို အရင် Join ပေးပါအုံးဗျ။Channel Join ပြီးသွားရင် /start ကိုပြန်ပို့ပေးပါဗျ{EMOJI_LOVE}။", reply_markup=markup)

@bot.message_handler(func=lambda m: True)
def download_video(message):
    user_id = message.from_user.id
    if not is_subscribed(user_id):
        start(message)
        return

    url = message.text
    if "tiktok.com" in url:
        msg = bot.reply_to(message, f"Logo ဖျောက်နေပါတယ်...ခနစောင့်ပါဗျ{EMOJI_WAIT}")
        
        video_url = None
        
        # နည်းလမ်း (၁)
        try:
            r = requests.get(f"https://www.tikwm.com/api/?url={url}", timeout=10).json()
            video_url = r.get('data', {}).get('play')
        except: pass

        # နည်းလမ်း (၂)
        if not video_url:
            try:
                r = requests.get(f"https://api.tiklydown.eu.org/api/download?url={url}", timeout=10).json()
                video_url = r.get('video', {}).get('noWatermark')
            except: pass

        if video_url:
            file_name = f"v_{uuid.uuid4().hex[:5]}.mp4"
            try:
                with requests.get(video_url, stream=True, timeout=30) as r:
                    r.raise_for_status()
                    with open(file_name, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                
                with open(file_name, 'rb') as video:
                    bot.send_video(message.chat.id, video, caption=f"ဗီဒီယို ရပါပြီ ခမျ{EMOJI_LOVE}")
                
                bot.delete_message(message.chat.id, msg.message_id)
            except:
                bot.edit_message_text(f"{EMOJI_WARNING} လိုင်းမကောင်းလို့ နောက်တစ်ခေါက် ပြန်ပို့ပေးပါဗျ။", message.chat.id, msg.message_id)
            finally:
                if os.path.exists(file_name): os.remove(file_name)
        else:
            bot.edit_message_text(f"{EMOJI_WARNING} TikTok ဘက်က တုံ့ပြန်မှု နှေးနေလို့ ခဏနေမှ ပြန်စမ်းပေးပါဗျ။", message.chat.id, msg.message_id)
    else:
        bot.reply_to(message, f"TikTok Link ပဲ ပို့ပေးပါဗျ{EMOJI_SMILE}။")

if __name__ == "__main__":
    Thread(target=run_web).start()
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except:
            time.sleep(5)
