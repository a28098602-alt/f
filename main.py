import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# توکن ربات شما
TOKEN = "8983512909:AAEaeZ170QSAwwOWnipnrXtSukwwepInlrI"

# آیدی عددی کانال
CHANNEL_ID = -1001188593103
CHANNEL_LINK = "https://t.me/etemad_Rayan_gostar"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            # عضویت تأیید شد - نمایش پیام اصلی
            text = (
                "#Violex | خرید استارز و پرمیوم\n"
                "ربات Vincent\n\n"
                "بهترین و سریعترین ربات خرید استارز و پرمیوم و کیفیت تلگرام ✅\n\n"
                "✅ دارای اعتبار و اعتماد کاربران\n"
                "✅ ثبت سریع سفارش | تحویل آنی سفارش ها\n"
                "✅ پشتیبانی #24/7 آنلاین\n\n"
                "پشتیبانی : ViolexSup@\n"
                "ViolexReport@ : گزارشات ❤️\n\n"
                "روی Start بزن و سفارش مد نظرتو ثبت کن 🚀"
            )
            keyboard = [[InlineKeyboardButton("🛒 ثبت سفارش", callback_data="order")]]
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await send_force_subscribe(update, context)
    except Exception as e:
        print(f"Error: {e}")
        await send_force_subscribe(update, context)

async def send_force_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🔔 برای استفاده از ربات ابتدا باید عضو کانال‌های زیر شوید:\n\n"
        f"👉 {CHANNEL_LINK}"
    )
    keyboard = [
        [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_sub")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            # عضویت تأیید شد
            text = (
                "✅ عضویت شما تأیید شد!\n\n"
                "#Violex | خرید استارز و پرمیوم\n"
                "ربات Vincent\n\n"
                "بهترین و سریعترین ربات خرید استارز و پرمیوم و کیفیت تلگرام ✅\n\n"
                "✅ دارای اعتبار و اعتماد کاربران\n"
                "✅ ثبت سریع سفارش | تحویل آنی سفارش ها\n"
                "✅ پشتیبانی #24/7 آنلاین\n\n"
                "پشتیبانی : ViolexSup@\n"
                "ViolexReport@ : گزارشات ❤️\n\n"
                "روی Start بزن و سفارش مد نظرتو ثبت کن 🚀"
            )
            keyboard = [[InlineKeyboardButton("🛒 ثبت سفارش", callback_data="order")]]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(
                "❌ هنوز عضو کانال نشده‌اید.\n"
                f"لطفاً ابتدا عضو شوید: {CHANNEL_LINK}\n\n"
                "سپس روی دکمه 'بررسی مجدد' کلیک کنید.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_LINK)],
                    [InlineKeyboardButton("🔄 بررسی مجدد", callback_data="check_sub")]
                ])
            )
    except Exception as e:
        print(f"Error in check: {e}")
        await query.edit_message_text(
            "❌ خطا در بررسی عضویت. لطفاً دوباره تلاش کنید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 بررسی مجدد", callback_data="check_sub")]
            ])
        )

async def order_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # بررسی مجدد عضویت قبل از ثبت سفارش
    user_id = query.from_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            await query.edit_message_text(
                "🛒 سفارش شما با موفقیت ثبت شد!\n\n"
                "✅ سفارش شما در صف پردازش قرار گرفت.\n"
                "⏳ به زودی با شما تماس گرفته می‌شود.\n\n"
                "پشتیبانی: ViolexSup@"
            )
        else:
            await query.edit_message_text(
                "❌ شما عضو کانال نیستید!\n"
                f"لطفاً ابتدا عضو شوید: {CHANNEL_LINK}"
            )
    except Exception as e:
        await query.edit_message_text("❌ خطا در ثبت سفارش. لطفاً دوباره تلاش کنید.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 راهنمای ربات Violex\n\n"
        "/start - شروع مجدد ربات\n"
        "برای ثبت سفارش روی دکمه 'ثبت سفارش' کلیک کنید.\n"
        "پشتیبانی: ViolexSup@"
    )

def main():
    app = Application.builder().token(TOKEN).build()

    # اضافه کردن هندلرها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(check_subscription, pattern="check_sub"))
    app.add_handler(CallbackQueryHandler(order_handler, pattern="order"))

    print("🤖 ربات Violex با موفقیت روشن شد...")
    print(f"📢 کانال اجباری: {CHANNEL_LINK}")
    print(f"🆔 آیدی کانال: {CHANNEL_ID}")
    
    app.run_polling()

if __name__ == "__main__":
    main()
