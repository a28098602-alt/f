import asyncio
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8983512909:AAEaeZ170QSAwwOWnipnrXtSukwwepInlrI"
CHANNEL_ID = -1001188593103
CHANNEL_LINK = "https://t.me/etemad_Rayan_gostar"
CHANNEL_USERNAME = "@Rayan_panel1bot"

# حذف Webhook قبلی
try:
    requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
    print("✅ Webhook حذف شد")
except:
    pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
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
    except Exception:
        await send_force_subscribe(update, context)

async def send_force_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "⚠️ <b>برای استفاده از ربات ابتدا باید عضو کانال‌های زیر شوید:</b>\n\n"
        f"📢 عضویت در {CHANNEL_USERNAME}"
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
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(
                "❌ <b>هنوز عضو کانال نشده‌اید.</b>\n"
                f"لطفاً ابتدا عضو شوید: {CHANNEL_LINK}",
                parse_mode='HTML'
            )
    except Exception:
        await query.edit_message_text(
            "❌ خطا در بررسی عضویت. لطفاً دوباره تلاش کنید.",
            parse_mode='HTML'
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
                "❌ <b>شما عضو کانال نیستید!</b>\n"
                f"لطفاً ابتدا عضو شوید: {CHANNEL_LINK}",
                parse_mode='HTML'
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

    print("🤖 ربات Violex با موفقیت روشن شد...")
    print(f"📢 کانال اجباری: {CHANNEL_LINK}")
    print(f"🆔 آیدی کانال: {CHANNEL_ID}")
    
    # استفاده از drop_pending_updates برای جلوگیری از Conflict
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
