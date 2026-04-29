import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- কনফিগারেশন ---
# আপনার @BotFather থেকে পাওয়া টোকেন দিন
BOT_TOKEN = "8762302157:AAFYdQrIqJqNUy-I35QIbDsQ8RLNZapIb4o"

# আপনার Netlify থেকে পাওয়া লিঙ্কটি দিন
MINI_APP_URL = "https://statuesque-taffy-2abb67.netlify.app/"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """বট স্টার্ট করলে ইউজারকে এই মেসেজ দেবে"""
    keyboard = [
        [InlineKeyboardButton(
            "🚀 ওপেন ডাউনলোড অ্যাপ", 
            web_app=WebAppInfo(url=MINI_APP_URL)
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 **স্বাগতম!**\nটিকটক ভিডিও ওয়াটারমার্ক ছাড়া ডাউনলোড করতে নিচের বাটনে ক্লিক করে অ্যাপটি ওপেন করুন।",
        reply_markup=reply_markup
    )

async def handle_tiktok_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ইউজার যদি সরাসরি চ্যাটে লিঙ্ক দেয়, তবে তাকে অ্যাপে পাঠানোর বাটন দেবে"""
    tiktok_url = update.message.text
    if "tiktok.com" in tiktok_url:
        keyboard = [
            [InlineKeyboardButton(
                "📥 ভিডিওটি ডাউনলোড করুন", 
                web_app=WebAppInfo(url=MINI_APP_URL)
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "✅ ভিডিওটি প্রস্তুত! ডাউনলোড করতে নিচের বাটনে ক্লিক করুন।",
            reply_markup=reply_markup
        )

def main():
    # বট অ্যাপ্লিকেশন তৈরি
    app = Application.builder().token(BOT_TOKEN).build()

    # হ্যান্ডেলারগুলো যোগ করা
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tiktok_link))

    print("Bot is running on Railway...")
    app.run_polling()

if __name__ == "__main__":
    main()
