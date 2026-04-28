import os
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from playwright.sync_api import sync_playwright

# --- কনফিগারেশন ---
BOT_TOKEN = "8762302157:AAFYdQrIqJqNUy-I35QIbDsQ8RLNZapIb4o"
MONETAG_LINK = "https://omg10.com/4/10936408"

# ভিডিও ইউআরএল জমা রাখার জন্য একটি ডিকশনারি (টেম্পোরারি স্টোরেজ)
user_data_store = {}

def get_ssstik_video(tiktok_url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            # সাইট লোড হওয়ার সময় একটু বেশি দেওয়া হয়েছে
            page.goto("https://ssstik.io/en", timeout=60000)
            
            page.fill('input[id="main_page_text"]', tiktok_url)
            page.click('button[id="submit"]')
            
            # ডাউনলোড বাটন না আসা পর্যন্ত অপেক্ষা
            page.wait_for_selector('.download_link', timeout=15000)
            
            video_link = page.query_selector('.download_link').get_attribute('href')
            browser.close()
            return video_link
    except Exception as e:
        print(f"Scraping Error: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 স্বাগতম! টিকটক ভিডিওর লিঙ্ক দিন, আমি ওয়াটারমার্ক ছাড়া ডাউনলোড করে দেব।")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "tiktok.com" not in url:
        await update.message.reply_text("❌ দয়া করে একটি সঠিক টিকটক লিঙ্ক দিন।")
        return

    # এরর এড়াতে ইউজার আইডি দিয়ে লিঙ্কটি স্টোর করা হচ্ছে
    user_id = update.message.from_user.id
    user_data_store[user_id] = url

    keyboard = [
        [InlineKeyboardButton("✅ Step 1: Watch Ad", url=MONETAG_LINK)],
        [InlineKeyboardButton("📩 Step 2: Download Video", callback_data="download_now")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🚀 ভিডিওটি প্রস্তুত! প্রথমে উপরের বাটনে ক্লিক করে অ্যাডটি দেখুন, তারপর নিচের ডাউনলোড বাটনে ক্লিক করুন।",
        reply_markup=reply_markup
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    
    if query.data == "download_now":
        # স্টোর থেকে লিঙ্কটি খুঁজে বের করা
        tiktok_url = user_data_store.get(user_id)
        
        if not tiktok_url:
            await query.edit_message_text("❌ সেশন শেষ হয়ে গেছে। আবার লিঙ্কটি পাঠান।")
            return

        sent_message = await query.edit_message_text("🔄 ভিডিও প্রসেস করা হচ্ছে... (৫-১০ সেকেন্ড সময় লাগতে পারে)")
        
        video_download_url = get_ssstik_video(tiktok_url)
        
        if video_download_url:
            try:
                await query.message.reply_video(video=video_download_url, caption="✅ ওয়াটারমার্ক ছাড়া ডাউনলোড সম্পন্ন!")
                await sent_message.delete()
                # কাজ শেষে মেমোরি ক্লিয়ার করা
                if user_id in user_data_store:
                    del user_data_store[user_id]
            except Exception as e:
                await query.edit_message_text(f"❌ ভিডিও পাঠাতে সমস্যা হয়েছে: {e}")
        else:
            await query.edit_message_text("❌ ভিডিও লিঙ্কটি পাওয়া যায়নি। আবার চেষ্টা করুন।")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_click))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
