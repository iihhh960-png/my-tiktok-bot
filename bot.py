import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes, 
    CallbackQueryHandler,
    ConversationHandler
)
from yt_dlp import YoutubeDL

# --- RENDER KEEP ALIVE ---
app = Flask('')
@app.route('/')
def home(): return "Bot is running!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- CONFIG ---
TOKEN = '8542512682:AAE_P51eSPOOu3LjlN-bKeSgvL3TG-2KWFA'
CHOOSING, DOWNLOADING = range(2)

# Unicode Emoji Codes (Copy-Safe)
U_WAVE = "\U0001F44B"
U_VIDEO = "\U0001F3AC"
U_MUSIC = "\U0001F3B5"
U_PHOTO = "\U0001F4F8"
U_LINK = "\U0001F517"
U_WAIT = "\U000023F3"
U_CHECK = "\U00002705"
U_ERROR = "\U0000274C"
U_ROCKET = "\U0001F680"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(f"{U_VIDEO} Video No Logo", callback_data='video')],
        [InlineKeyboardButton(f"{U_MUSIC} MP3 Music", callback_data='music')],
        [InlineKeyboardButton(f"{U_PHOTO} Photos (Album)", callback_data='photo')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"{U_WAVE} **TikTok Downloader** မှ ကြိုဆိုပါတယ်။\nဘာကို ဒေါင်းလုဒ်ဆွဲချင်ပါသလဲ?"
    
    if update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    return CHOOSING

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['choice'] = query.data
    await query.edit_message_text(f"{U_ROCKET} **Selected: {query.data.upper()}**\n{U_LINK} TikTok Link ကို ပို့ပေးပါဗျာ။", parse_mode='Markdown')
    return DOWNLOADING

async def download_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    choice = context.user_data.get('choice')

    if "tiktok.com" not in url:
        await update.message.reply_text(f"{U_ERROR} TikTok Link မှန်အောင် ပြန်ပို့ပေးပါ။")
        return DOWNLOADING

    status = await update.message.reply_text(f"{U_WAIT} ပြင်ဆင်နေပါတယ်... ခဏစောင့်ပါ။")

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False) # အရင်ဆုံး အချက်အလက်ယူမယ်
            
            # --- ပုံများကို တစ်ပုံချင်းစီ Album ပို့မည့်အပိုင်း ---
            if choice == 'photo':
                images = info.get('thumbnails', [])
                # TikTok photo posts များတွင် များသောအားဖြင့် 'entries' သို့မဟုတ် 'thumbnails' တွင်ပုံပါသည်
                # ပုံစံအမျိုးမျိုးအတွက် စစ်ဆေးခြင်း
                image_urls = []
                
                # entries ရှိလျှင် (Slideshow)
                if 'entries' in info:
                    image_urls = [e['url'] for e in info['entries'] if 'url' in e]
                # thumbnails ထဲတွင် ပုံများရှိလျှင်
                elif images:
                    # အရည်အသွေးအကောင်းဆုံးပုံကို ယူရန်
                    image_urls = [images[-1]['url']]

                if image_urls:
                    media_group = [InputMediaPhoto(media=img_url) for img_url in image_urls[:10]] # အများဆုံး ၁၀ ပုံ
                    await update.message.reply_media_group(media=media_group)
                    await status.delete()
                else:
                    await status.edit_text(f"{U_ERROR} ပုံများကို ရှာမတွေ့ပါ။ Video အဖြစ် ဒေါင်းကြည့်ပါ။")

            # --- Video သို့မဟုတ် Music ပို့မည့်အပိုင်း ---
            else:
                ydl_opts['outtmpl'] = 'downloads/%(id)s.%(ext)s'
                ydl_opts['format'] = 'bestvideo+bestaudio/best' if choice == 'video' else 'bestaudio/best'
                
                # အမှန်တကယ် ဒေါင်းလုဒ်ဆွဲခြင်း
                info_download = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info_download)

                if choice == 'video':
                    await update.message.reply_video(video=open(file_path, 'rb'), caption=f"{U_CHECK} Success!")
                elif choice == 'music':
                    audio_path = file_path.rsplit('.', 1)[0] + ".mp3"
                    os.rename(file_path, audio_path)
                    await update.message.reply_audio(audio=open(audio_path, 'rb'), caption=f"{U_MUSIC} Success!")
                    file_path = audio_path
                
                if os.path.exists(file_path): os.remove(file_path)
                await status.delete()

    except Exception as e:
        await update.message.reply_text(f"{U_ERROR} အမှားအယွင်းရှိပါသည်- {str(e)}")
    
    return await start(update, context)

def main():
    if not os.path.exists('downloads'): os.makedirs('downloads')
    threading.Thread(target=run_web, daemon=True).start()
    
    app = Application.builder().token(TOKEN).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [CallbackQueryHandler(button_click)],
            DOWNLOADING: [MessageHandler(filters.TEXT & ~filters.COMMAND, download_process)],
        },
        fallbacks=[CommandHandler('start', start)],
    )
    app.add_handler(conv_handler)
    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
