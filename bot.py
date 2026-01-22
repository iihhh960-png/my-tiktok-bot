import telebot
import yt_dlp
import os
from flask import Flask
from threading import Thread

# --- ဒီေနရာမွာ မင္းရဲ႕ Channel Username ကို ေျပာင္းထည့္ပါ ---
CHANNEL_ID = "@musicfan11234" 
# --------------------------------------------------

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    app.run(host='0.0.0.0', port=10000) # Render အတြက္ port 10000 က ပိုအဆင္ေျပပါတယ္

TOKEN = '8542512682:AAE_P51eSPOOu3LjlN-bKeSgvL3TG-2KWFA'
bot = telebot.TeleBot(TOKEN)

# User က Join ထားျခင္း ရွိ/မရွိ စစ္ေဆးတဲ့ function
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        # Error တက္ရင္ (ဥပမာ Bot က Admin မဟုတ္ရင္) လူတိုင္းသုံးလို႔ရေအာင္ True ေပးထားမယ္
        return True

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if is_subscribed(user_id):
        bot.reply_to(message, " မင်္ဂလာပါ🤗! Bot ကို အသုံးပြုနိုင်ပါပြီ။ TikTok Link ပို့ပေးပါခမျ")
    else:
        # Join ရေသးတဲ့ User ကိုပဲ ခလုတ္ျပမယ္
        markup = telebot.types.InlineKeyboardMarkup()
        btn = telebot.types.InlineKeyboardButton(text=" Join Our Channel", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}")
        markup.add(btn)
        bot.send_message(
            message.chat.id, 
            " BOT ကိုအသုံး ပြုရန် ကျွန်ုပ်တို့၏ Channel ကို အရင် Join ပေးပါအုံးဗျ။Channel Join ပြီးသွားရင် /statt ကိုပြန်ပို့ပေးပါဗျ🥰။", 
            reply_markup=markup
        )

@bot.message_handler(func=lambda m: True)
def download_video(message):
    user_id = message.from_user.id
    
    # User က Join ထားမွ ဗီဒီယိုေဒါင္းေပးမယ္
    if not is_subscribed(user_id):
        start(message)
        return

    url = message.text
    if "tiktok.com" in url:
        msg = bot.reply_to(message, "Logo ဖျောက်နေပါတယ်...ခနစောင့်ပါဗျ🥱 ")
        
        # yt-dlp option မ်ားကို error ကင္းေအာင္ ျပင္ထားပါတယ္
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'vid.mp4',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True
        }
        
        try:
            if os.path.exists('vid.mp4'): os.remove('vid.mp4') # ဖိုင္ေဟာင္းရွိေနရင္ ဖ်က္မယ္
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            with open('vid.mp4', 'rb') as video:
                bot.send_video(message.chat.id, video, caption="ဗီဒီယို ရပါပြီ ခမျ🥰 ")
            
            os.remove('vid.mp4')
            bot.delete_message(message.chat.id, msg.message_id)
        except Exception as e:
            bot.reply_to(message, f"တစ်ခုခု မှားနေပါတယ်😒- {str(e)}")
    else:
        bot.reply_to(message, "TikTok Link ပဲ ပို့ပေးပါဗျ🤗။")

if __name__ == "__main__":
    t = Thread(target=run_web)
    t.start()
    print("Bot is starting...")
    bot.polling(none_stop=True)
