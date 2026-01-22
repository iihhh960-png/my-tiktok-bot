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
    # Render အတွက် Port 10000 ကို သုံးထားပါတယ်
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
        # စာသားကို ရှင်းလင်းအောင် ပြင်ထားပါတယ်
        bot.reply_to(message, " မင်္ဂလာပါဗျာ! Bot ကို အသုံးပြုနိုင်ပါပြီ။\nTikTok Link ပို့ပေးပါခင်ဗျာ။🥰 ")
    else:
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text=" Join Our Channel", url=f"https://t.me/musicfan11234")
        markup.add(btn)
        # Force Join စာသားကို အမှားအယွင်းမရှိအောင် ပြင်ထားပါတယ်
        bot.send_message(
            message.chat.id, 
            " Bot ကို အသုံးပြုရန် ကျွန်တော်တို့ရဲ့  Channel ကို အရင် Join ပေးပါဦးဗျ။\n\nJoin ပြီးသွားရင် /start ကို ပြန်နှိပ်ပေးပါဗျ🥰။ ", 
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
        msg = bot.reply_to(message, " Logo ဖျောက်နေပါတယ်... ခဏစောင့်ပါဗျာ🥱။ ")
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'vid.mp4',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True
        }
        
        try:
            if os.path.exists('vid.mp4'): os.remove('vid.mp4')
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            with open('vid.mp4', 'rb') as video:
                bot.send_video(message.chat.id, video, caption=" ဗီဒီယို ရပါပြီ ခင်ဗျာ။ ")
            
            os.remove('vid.mp4')
            bot.delete_message(message.chat.id, msg.message_id)
        except Exception as e:
            bot.reply_to(message, f" တစ်ခုခု မှားယွင်းနေပါတယ်ဗျာ😐။\nError: {str(e)}")
    else:
        bot.reply_to(message, " TikTok Link ပဲ ပို့ပေးပါဗျာ🤧။ ")

if __name__ == "__main__":
    t = Thread(target=run_web)
    t.start()
    print("Bot is starting...")
    bot.polling(none_stop=True)
