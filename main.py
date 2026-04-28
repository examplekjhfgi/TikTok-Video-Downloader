import os
import time
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from playwright.sync_api import sync_playwright

# --- কনফিগারেশন ---
BOT_TOKEN = "8762302157:AAFYdQrIqJqNUy-I35QIbDsQ8RLNZapIb4o"
MONETAG_LINK = "https://omg10.com/4/10936408"

# টিকটক ভিডিও লিঙ্ক স্ক্র্যাপ করার ফাংশন
def get_ssstik_video(tiktok_url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://ssstik.io/en", timeout=60000)
            
            # লিঙ্ক ইনপুট এবং সার্চ
            page.fill('input[id="main_page_text"]', tiktok_url)
            page.press('input[id="main_page_text"]', 'Enter')
            
            # ডাউনলোড বাটন আসা পর্যন্ত অপেক্ষা
            page.wait_for_selector('.download_link', timeout=10000)
            
            # প্রথম ডাউনলোড বাটন (Without Watermark) এর লিঙ্ক নেওয়া
            video_link = page.query_selector('.download_link').get_attribute('href')
            browser.close()
            return video_link
    except Exception as e:
        print(f"Error: {e}")
        return None

# স্টার্ট কমান্ড
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 স্বাগতম! যেকোনো টিকটক ভিডিওর লিঙ্ক দিন, আমি ওয়াটারমার্ক ছাড়া ডাউনলোড করে দেব।"
    )

# মেসেজ হ্যান্ডেলার
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "tiktok.com" not in url:
        await update.message.reply_text("❌ দয়া করে একটি সঠিক টিকটক ভিডিও লিঙ্ক দিন।")
        return

    # ইউজারকে অ্যাড দেখানোর বাটন
    keyboard = [
        [InlineKeyboardButton("✅ Get Download Link (Watch Ad)", url=MONETAG_LINK)],
        [InlineKeyboardButton("📩 Download Video", callback_data=f"dl|{url}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🚀 ভিডিওটি প্রস্তুত! নিচের লিংকে ক্লিক করে ১টি অ্যাড দেখুন, তারপর 'Download Video' বাটনে ক্লিক করুন।",
        reply_markup=reply_markup
    )

# ডাউনলোড বাটন ক্লিক হ্যান্ডেলার
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split("|")
    if data[0] == "dl":
        tiktok_url = data[1]
        sent_message = await query.edit_message_text("🔄 প্রসেসিং হচ্ছে... দয়া করে অপেক্ষা করুন।")
        
        video_download_url = get_ssstik_video(tiktok_url)
        
        if video_download_url:
            await query.message.reply_video(video=video_download_url, caption="✅ ওয়াটারমার্ক ছাড়া ভিডিও ডাউনলোড সম্পন্ন!")
            await sent_message.delete()
        else:
            await query.edit_message_text("❌ দুঃখিত! ভিডিওটি পাওয়া যায়নি। আবার চেষ্টা করুন।")

# মেইন ফাংশন
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_click))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
