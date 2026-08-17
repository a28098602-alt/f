import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# توکن ربات شما
TOKEN = "8983512909:AAEaeZ170QSAwwOWnipnrXtSukwwepInlrI"

# آیدی عددی کانال
CHANNEL_ID = -1001188593103
CHANNEL_LINK = "https://t.me/etemad_Rayan_gostar"
CHANNEL_USERNAME = "@Rayan_panel1bot"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            # عضویت تأیید شد - نمایش پیام اصلی
            text = (
                "⭐ <b>به بزرگترین مارکت خدمات تلگرام « رایان | Ryan » خوش آمدید!</b> ⭐\n\n"
                "✅ اینجا همه‌چیز با بالاترین کیفیت، ارزان‌ترین قیمت و تحویل آنی به دستت می‌رسه!\n\n"
                "⭐ استارز تلگرام  |  💎 ارز تون / Gram\n"
                "💎 پرمیوم تلگرام  |  🪙 شارژ آنی تون بالانس\n"
                "🎁 گیفت‌های استارزی  |  🪙 ارز ترون / TRX\n"
                "🎁 گیوای استارزی  |  ⭐ ری اکشن استارزی\n"
                "⚡ بوست تلگرام\n\n"
                "<b>برای خرید یکی از گزینه‌های منوی زیر رو انتخاب کن 👇</b>"
            )
            keyboard = [[InlineKeyboardButton("🛒 ثبت سفارش", callback_data="order")]]
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        else:
            await send_force_subscribe(update, context)
    except Exception:
        await send_force_subscribe(update, context)

async def send_force_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "⚠️ <b>برای استفاده از ربات ابتدا باید عضو کانال‌های زیر شوید:</b>"
    )
    keyboard = [
        [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ عضو شدم", callback_data="check_sub")]
    ]
    await update.message.reply_text(
        text, 
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            # عضویت تأیید شد - نمایش پیام اصلی
            text = (
                "⭐ <b>به بزرگترین مارکت خدمات تلگرام « رایان | Ryan » خوش آمدید!</b> ⭐\n\n"
                "✅ اینجا همه‌چیز با بالاترین کیفیت، ارزان‌ترین قیمت و تحویل آنی به دستت می‌رسه!\n\n"
                "⭐ استارز تلگرام  |  💎 ارز تون / Gram\n"
                "💎 پرمیوم تلگرام  |  🪙 شارژ آنی تون بالانس\n"
                "🎁 گیفت‌های استارزی  |  🪙 ارز ترون / TRX\n"
                "🎁 گیوای استارزی  |  ⭐ ری اکشن استارزی\n"
                "⚡ بوست تلگرام\n\n"
                "<b>برای خرید یکی از گزینه‌های منوی زیر رو انتخاب کن 👇</b>"
            )
            keyboard = [[InlineKeyboardButton("🛒 ثبت سفارش", callback_data="order")]]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        else:
            # پیام خطا برای کاربرانی که عضو نشده‌اند
            await query.edit_message_text(
                "❌ <b>هنوز عضو کانال نشده‌اید لطفاً ابتدا عضو کانال شوید.</b>",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_LINK)],
                    [InlineKeyboardButton("✅ عضو شدم", callback_data="check_sub")]
                ])
            )
    except Exception:
        await query.edit_message_text(
            "❌ <b>خطا در بررسی عضویت. لطفاً دوباره تلاش کنید.</b>",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 بررسی مجدد", callback_data="check_sub")]
            ])
        )

async def order_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            await query.edit_message_text(
                "🛒 <b>سفارش شما با موفقیت ثبت شد!</b>\n\n"
                "✅ سفارش شما در صف پردازش قرار گرفت.\n"
                "⏳ به زودی با شما تماس گرفته می‌شود.\n\n"
                "پشتیبانی: ViolexSup@",
                parse_mode='HTML'
            )
        else:
            await query.edit_message_text(
                "❌ <b>هنوز عضو کانال نشده‌اید لطفاً ابتدا عضو کانال شوید.</b>",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_LINK)],
                    [InlineKeyboardButton("✅ عضو شدم", callback_data="check_sub")]
                ])
            )
    except Exception:
        await query.edit_message_text(
            "❌ خطا در ثبت سفارش. لطفاً دوباره تلاش کنید.",
            parse_mode='HTML'
        )

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check_subscription, pattern="check_sub"))
    application.add_handler(CallbackQueryHandler(order_handler, pattern="order"))

    print("🤖 ربات Ryan با موفقیت روشن شد...")
    print(f"📢 کانال اجباری: {CHANNEL_LINK}")
    print(f"🆔 آیدی کانال: {CHANNEL_ID}")
    
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
