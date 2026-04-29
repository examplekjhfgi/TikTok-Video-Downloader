import time
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- কনফিগারেশন ---
BOT_TOKEN = "8762302157:AAFYdQrIqJqNUy-I35QIbDsQ8RLNZapIb4o"
MONETAG_LINK = "https://omg10.com/4/10936408"

# ইউজার ডেটা ও টাইমার স্টোরেজ
user_sessions = {}

def get_video_from_multiple_sources(tiktok_url):
    """একাধিক সোর্স থেকে ভিডিও খোঁজা"""
    # সোর্স ১: TikWM
    try:
        res = requests.get(f"https://www.tikwm.com/api/?url={tiktok_url}").json()
        if res.get("code") == 0:
            data = res['data']
            options = []
            if data.get("play"): options.append({"label": "🎥 Download MP4 (HD)", "url": data['play'], "type": "video"})
            if data.get("music"): options.append({"label": "🎵 Download MP3", "url": data['music'], "type": "audio"})
            return options
    except: pass

    # সোর্স ২: অন্য একটি ওপেন API (বিকল্প)
    try:
        res = requests.get(f"https://api.tiklydown.eu.org/api/download?url={tiktok_url}").json()
        if res.get("video"):
            return [{"label": "🎥 Download HD (Server 2)", "url": res['video']['noWatermark'], "type": "video"}]
    except: pass

    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 টিকটক ভিডিও লিঙ্ক দিন। ৬০ সেকেন্ড অ্যাড দেখার পর ডাউনলোড করতে পারবেন।")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "tiktok.com" not in url:
        await update.message.reply_text("❌ সঠিক লিঙ্ক দিন।")
        return

    user_id = update.message.from_user.id
    # ইউজারের সেশন শুরু এবং টাইমার সেট করা (৬০ সেকেন্ড)
    user_sessions[user_id] = {
        "url": url,
        "start_time": time.time(),
        "ad_watched": False
    }

    keyboard = [
        [InlineKeyboardButton("🔗 ১. এখানে ক্লিক করে অ্যাড দেখুন (৬০ সেকেন্ড)", url=MONETAG_LINK)],
        [InlineKeyboardButton("⏳ ২. ডাউনলোড অপশন চেক করুন", callback_data="check_ad")]
    ]
    
    await update.message.reply_text(
        "⏳ **অ্যাড গেট সক্রিয়!**\n\nপ্রথমে উপরের লিঙ্কে ক্লিক করে ৬০ সেকেন্ড অপেক্ষা করুন। তারপর নিচের বাটনে ক্লিক করুন।",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    session = user_sessions.get(user_id)
    if not session:
        await query.edit_message_text("❌ সেশন শেষ। আবার লিঙ্ক দিন।")
        return

    if query.data == "check_ad":
        elapsed_time = time.time() - session["start_time"]
        remaining = 60 - int(elapsed_time)

        if remaining > 0:
            # ৬০ সেকেন্ড হয়নি, তাই আবার বাটন পাঠানো হলো
            keyboard = [
                [InlineKeyboardButton("🔗 আবার অ্যাডে ক্লিক করুন", url=MONETAG_LINK)],
                [InlineKeyboardButton(f"⏳ অপেক্ষা করুন ({remaining}s)", callback_data="check_ad")]
            ]
            await query.edit_message_text(
                f"⚠️ **অ্যাড দেখা শেষ হয়নি!**\nআপনাকে আরও {remaining} সেকেন্ড অপেক্ষা করতে হবে।",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            # ৬০ সেকেন্ড শেষ, এখন ভিডিওর ফরম্যাটগুলো দেখানো হবে
            await query.edit_message_text("🔍 ভিডিও ফরম্যাটগুলো খোঁজা হচ্ছে...")
            formats = get_video_from_multiple_sources(session["url"])
            
            if formats:
                keyboard = []
                for fmt in formats:
                    # এখানে সরাসরি ফাইল না পাঠিয়ে ডাউনলোডের জন্য নতুন কলব্যাক দেওয়া হয়েছে
                    keyboard.append([InlineKeyboardButton(fmt['label'], callback_data=f"get|{fmt['type']}|{fmt['url'][:40]}")]) # লিঙ্ক ছোট রাখা হয়েছে
                
                # সেশনে ফরম্যাটগুলো সেভ করে রাখা যাতে পরে পাঠানো যায়
                session["formats"] = formats
                
                # আসল ডাউনলোড বাটনগুলো দেখানো
                dl_keyboard = []
                for i, f in enumerate(formats):
                    dl_keyboard.append([InlineKeyboardButton(f['label'], callback_data=f"final_dl|{i}")])

                await query.edit_message_text("✅ ৬০ সেকেন্ড পূর্ণ হয়েছে! আপনার পছন্দের ফরম্যাটটি বেছে নিন:", 
                                             reply_markup=InlineKeyboardMarkup(dl_keyboard))
            else:
                await query.edit_message_text("❌ দুঃখিত, সব সোর্স ট্রাই করেও ভিডিওটি পাওয়া যায়নি।")

    elif query.data.startswith("final_dl"):
        index = int(query.data.split("|")[1])
        format_info = session["formats"][index]
        
        await query.edit_message_text("📤 ফাইলটি পাঠানো হচ্ছে...")
        
        if format_info['type'] == "video":
            await query.message.reply_video(video=format_info['url'], caption="Enjoy your video!")
        else:
            await query.message.reply_audio(audio=format_info['url'], caption="Enjoy your audio!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_click))
    print("Bot started with 60s Ad-Gate...")
    app.run_polling()

if __name__ == "__main__":
    main()
