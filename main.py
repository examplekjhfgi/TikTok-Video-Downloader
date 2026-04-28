import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from playwright.sync_api import sync_playwright

# --- কনফিগারেশন ---
BOT_TOKEN = "8762302157:AAFYdQrIqJqNUy-I35QIbDsQ8RLNZapIb4o"
MONETAG_LINK = "https://omg10.com/4/10936408"

# মেমোরি স্টোরেজ
user_data_store = {}

def get_ssstik_video(tiktok_url):
    try:
        with sync_playwright() as p:
            # Railway এর জন্য এই অপশনগুলো জরুরি
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
            page = browser.new_page()
            page.goto("https://ssstik.io/en", timeout=60000, wait_until="networkidle")
            
            page.fill('input[id="main_page_text"]', tiktok_url)
            page.click('button[id="submit"]')
            
            # ডাউনলোড বাটন আসা পর্যন্ত অপেক্ষা
            page.wait_for_selector('.download_link', timeout=20000)
            
            video_link = page.query_selector('.download_link').get_attribute('href')
            browser.close()
            return video_link
    except Exception as e:
        print(f"Scraping Error: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 স্বাগতম! টিকটক ভিডিও লিঙ্ক দিন, আমি ডাউনলোড করে দেব।")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "tiktok.com" not in url:
        await update.message.reply_text("❌ এটি সঠিক টিকটক লিঙ্ক নয়।")
        return

    user_id = update.message.from_user.id
    user_data_store[user_id] = url

    # বাটন তৈরি - এখানে callback_data একদম ছোট রাখা হয়েছে
    keyboard = [
        [InlineKeyboardButton("✅ Step 1: Click for Ads", url=MONETAG_LINK.strip())],
        [InlineKeyboardButton("📩 Step 2: Download Now", callback_data="dl_btn")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await update.message.reply_text(
            "🚀 আপনার ভিডিওটি প্রসেস করার জন্য প্রস্তুত।\n\nপ্রথমে ১ নম্বর বাটনে ক্লিক করে অ্যাডটি দেখুন, তারপর ২ নম্বর বাটনে ক্লিক করুন।",
            reply_markup=reply_markup
        )
    except Exception as e:
        print(f"Reply Error: {e}")
        await update.message.reply_text("❌ বাটন তৈরিতে সমস্যা হচ্ছে। অ্যাড লিঙ্কটি চেক করুন।")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    if query.data == "dl_btn":
        await query.answer("ভিডিও প্রসেস করা হচ্ছে...")
        
        tiktok_url = user_data_store.get(user_id)
        if not tiktok_url:
            await query.edit_message_text("❌ সেশন শেষ! আবার লিঙ্কটি পাঠান।")
            return

        status_msg = await query.edit_message_text("🔄 ব্যাকএন্ডে কাজ চলছে... দয়া করে ১০ সেকেন্ড অপেক্ষা করুন।")
        
        video_url = get_ssstik_video(tiktok_url)
        
        if video_url:
            try:
                await query.message.reply_video(video=video_url, caption="✅ ডাউনলোড সফল হয়েছে!")
                await status_msg.delete()
            except Exception as e:
                await query.edit_message_text(f"❌ ভিডিও ফাইলটি পাঠাতে সমস্যা হয়েছে।")
        else:
            await query.edit_message_text("❌ ভিডিওটি পাওয়া যায়নি। সাইটটি ব্যস্ত থাকতে পারে।")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_click))
    
    print("Bot is live...")
    app.run_polling()

if __name__ == "__main__":
    main()
