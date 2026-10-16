import os
import telebot
from telebot import types
import yt_dlp

# جلب البيانات السرية من إعدادات السيرفر السحابي لحمايتها
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
CHANNEL_URL = os.getenv("CHANNEL_URL")

bot = telebot.TeleBot(BOT_TOKEN)

# فحص هل المستخدم مشترك في القناة أم لا
def is_user_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception:
        return False

# رسالة الترحيب /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if not is_user_subscribed(user_id):
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(text="اضغط هنا للاشتراك في القناة 📢", url=CHANNEL_URL)
        markup.add(btn)
        bot.send_message(message.chat.id, "⚠️ عذراً! يجب عليك الاشتراك في قناتنا أولاً لتتمكن من استخدام البوت وتحميل الفيديوهات مجاناً.\n\nبعد الاشتراك، أرسل أمر /start مجدداً.", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "🎉 أهلاً بك في بوت التحميل الذكي!\n\nأرسل لي الآن أي رابط فيديو من (إنستغرام ريلز، تيك توك، أو يوتيوب) وسأقوم بتحميله وإرساله لك فوراً! 🎬")

# استقبال الروابط وتحميلها تلقائياً
@bot.message_handler(func=lambda message: True)
def handle_links(message):
    user_id = message.from_user.id
    url = message.text

    if not is_user_subscribed(user_id):
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(text="اضغط هنا للاشتراك في القناة 📢", url=CHANNEL_URL)
        markup.add(btn)
        bot.send_message(message.chat.id, "⚠️ يرجى الاشتراك في القناة أولاً لتفعيل ميزة التحميل!", reply_markup=markup)
        return

    if "instagram.com" in url or "tiktok.com" in url or "youtube.com" in url or "youtu.be" in url:
        msg = bot.send_message(message.chat.id, "⏳ جاري معالجة الرابط وتحميل الفيديو، يرجى الانتظار ثوانٍ...")
        
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': 'video.mp4',
            'quiet': True,
            'no_warnings': True
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            with open('video.mp4', 'rb') as video:
                bot.send_video(message.chat.id, video, caption="✨ تم التحميل بنجاح عبر بوت التحميل الخاص بك!")
            
            os.remove('video.mp4')
            bot.delete_message(message.chat.id, msg.message_id)
            
        except Exception as e:
            bot.edit_message_text(f"❌ عذراً، حدث خطأ أثناء تحميل هذا الرابط. قد يكون الفيديو خاصاً أو تم حظر العملية مؤقتاً.", message.chat.id, msg.message_id)
            if os.path.exists('video.mp4'):
                os.remove('video.mp4')
    else:
        bot.send_message(message.chat.id, "❓ هذا الرابط غير مدعوم. يرجى إرسال رابط صحيح من إنستغرام، تيك توك، أو يوتيوب.")

if __name__ == "__main__":
    print("البوت يعمل الآن بنجاح...")
    bot.infinity_polling()
  
