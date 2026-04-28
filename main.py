import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- কনফিগারেশন ---
BOT_TOKEN = "8762302157:AAFYdQrIqJqNUy-I35QIbDsQ8RLNZapIb4o"
MONETAG_LINK = "https://omg10.com/4/10936408"

# মেমোরি স্টোরেজ (টেম্পোরারি)
user_data_store = {}

def get_tiktok_video(tiktok_url):
    """
    TikTok API ব্যবহার করে ভিডিও লিঙ্ক বের করার ফাংশন
    """
    try:
        # টিকটক ভিডিও আইডি বা লিঙ্ক থেকে ডেটা নেওয়ার জন্য একটি ওপেন API
        api_url = f"https://www.tikwm.com/api/?url={tiktok_url}"
        response = requests.get(api_url, timeout=15).json()
        
        if response.get("code") == 0:
            # code 0 মানে ভিডিওটি সফলভাবে পাওয়া গেছে
            video_data = response.get("data")
            # play হলো ওয়াটারমার্ক ছাড়া ভিডিওর লিঙ্ক
            return video_data.get("play")
        else:
            print(f"API Error: {response.get('msg')}")
            return None
    except Exception as e:
        print(f"Server Error: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 **স্বাগতম!**\nযেকোনো টিকটক ভিডিওর লিঙ্ক দিন, আমি সেটি ওয়াটারমার্ক ছাড়া ডাউনলোড করে দিচ্ছি।"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    
    if "tiktok.com" not in url:
        await update.message.reply_text("❌ এটি সঠিক টিকটক লিঙ্ক নয়। দয়া করে ভিডিওর লিঙ্ক কপি করে পাঠান।")
        return

    user_id = update.message.from_user.id
    user_data_store[user_id] = url

    # বাটন সেটআপ
    keyboard = [
        [InlineKeyboardButton("✅ Step 1: Watch Ad (Click Here)", url=MONETAG_LINK)],
        [InlineKeyboardButton("📩 Step 2: Download Video", callback_data="dl_ready")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🚀 **আপনার ভিডিওটি প্রস্তুত!**\n\nপ্রথমে ১ নম্বর বাটনে ক্লিক করে অ্যাডটি দেখুন (১০-১৫ সেকেন্ড), তারপর ২ নম্বর বাটনে ক্লিক করুন ডাউনলোড করার জন্য।",
        reply_markup=reply_markup
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    # এরর এড়াতে সাথে সাথে কোয়েরি এনসার করা
    await query.answer()
    
    if query.data == "dl_ready":
        tiktok_url = user_data_store.get(user_id)
        
        if not tiktok_url:
            await query.edit_message_text("❌ সেশন শেষ হয়ে গেছে। দয়া করে আবার লিঙ্কটি পাঠান।")
            return

        status_msg = await query.edit_message_text("🔄 ভিডিওটি প্রসেস করছি... দয়া করে ৫-১০ সেকেন্ড অপেক্ষা করুন।")
        
        # API থেকে ভিডিও লিঙ্ক নেওয়া
        video_link = get_tiktok_video(tiktok_url)
        
        if video_link:
            try:
                # সরাসরি ভিডিও ফাইল পাঠানো
                await query.message.reply_video(
                    video=video_link, 
                    caption="✅ **ডাউনলোড সম্পন্ন হয়েছে!**\n\nআপনার যদি আরও ভিডিও লাগে তবে আবার লিঙ্ক দিন।"
                )
                await status_msg.delete()
                # মেমোরি ক্লিয়ার
                if user_id in user_data_store:
                    del user_data_store[user_id]
            except Exception as e:
                print(f"Telegram Send Error: {e}")
                await query.edit_message_text("❌ ফাইলটি টেলিগ্রামে পাঠাতে সমস্যা হয়েছে। ভিডিও সাইজ বড় হতে পারে।")
        else:
            await query.edit_message_text("❌ ভিডিওটি খুঁজে পাওয়া যায়নি। লিঙ্কটি চেক করে আবার পাঠান।")

def main():
    # বট অ্যাপ্লিকেশন চালু করা
    app = Application.builder().token(BOT_TOKEN).build()
    
    # কমান্ড ও মেসেজ হ্যান্ডেলার যোগ করা
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_click))
    
    print("Bot is running properly...")
    app.run_polling()

if __name__ == "__main__":
    main()
