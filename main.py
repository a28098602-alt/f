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
            # پیام اصلی با منو
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
            
            keyboard = [
                [InlineKeyboardButton("🛒 خرید محصول", callback_data="buy")],
                [InlineKeyboardButton("👤 حساب کاربری", callback_data="account")],
                [InlineKeyboardButton("💰 افزایش موجودی", callback_data="charge")],
                [InlineKeyboardButton("👥 زیر مجموعه گیری", callback_data="referral")],
                [InlineKeyboardButton("📞 پشتیبانی", callback_data="support")],
                [InlineKeyboardButton("📋 وضعیت سفارشات", callback_data="orders")],
                [InlineKeyboardButton("📢 باب کره (کانال)", callback_data="channel")]
            ]
            
            await update.message.reply_text(
                text, 
                reply_markup=InlineKeyboardMarkup(keyboard), 
                parse_mode='HTML'
            )
        else:
            await send_force_subscribe(update, context)
    except Exception:
        await send_force_subscribe(update, context)

async def send_force_subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "⚠️ <b>برای استفاده از ربات ابتدا باید عضو کانال‌های زیر شوید:</b>"
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
                "⭐ <b>به بزرگترین مارکت خدمات تلگرام « رایان | Ryan » خوش آمدید!</b> ⭐\n\n"
                "✅ اینجا همه‌چیز با بالاترین کیفیت، ارزان‌ترین قیمت و تحویل آنی به دستت می‌رسه!\n\n"
                "⭐ استارز تلگرام  |  💎 ارز تون / Gram\n"
                "💎 پرمیوم تلگرام  |  🪙 شارژ آنی تون بالانس\n"
                "🎁 گیفت‌های استارزی  |  🪙 ارز ترون / TRX\n"
                "🎁 گیوای استارزی  |  ⭐ ری اکشن استارزی\n"
                "⚡ بوست تلگرام\n\n"
                "<b>برای خرید یکی از گزینه‌های منوی زیر رو انتخاب کن 👇</b>"
            )
            
            keyboard = [
                [InlineKeyboardButton("🛒 خرید محصول", callback_data="buy")],
                [InlineKeyboardButton("👤 حساب کاربری", callback_data="account")],
                [InlineKeyboardButton("💰 افزایش موجودی", callback_data="charge")],
                [InlineKeyboardButton("👥 زیر مجموعه گیری", callback_data="referral")],
                [InlineKeyboardButton("📞 پشتیبانی", callback_data="support")],
                [InlineKeyboardButton("📋 وضعیت سفارشات", callback_data="orders")],
                [InlineKeyboardButton("📢 باب کره (کانال)", callback_data="channel")]
            ]
            
            await query.edit_message_text(
                text, 
                reply_markup=InlineKeyboardMarkup(keyboard), 
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
            "❌ <b>خطا در بررسی عضویت. لطفاً دوباره تلاش کنید.</b>",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 بررسی مجدد", callback_data="check_sub")]
            ])
        )

# ============== هندلرهای دکمه‌های منو ==============

async def buy_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = (
        "🛒 <b>خرید محصول</b>\n\n"
        "⭐ استارز تلگرام\n"
        "💎 پرمیوم تلگرام\n"
        "🎁 گیفت‌های استارزی\n"
        "🎁 گیوای استارزی\n"
        "⚡ بوست تلگرام\n"
        "💎 ارز تون / Gram\n"
        "🪙 شارژ آنی تون بالانس\n"
        "🪙 ارز ترون / TRX\n\n"
        "برای خرید یکی از محصولات بالا، عدد مربوطه رو انتخاب کن:\n"
        "1️⃣ استارز\n"
        "2️⃣ پرمیوم\n"
        "3️⃣ گیفت استارزی\n"
        "4️⃣ گیوای استارزی\n"
        "5️⃣ بوست تلگرام\n"
        "6️⃣ ارز تون / Gram\n"
        "7️⃣ شارژ تون بالانس\n"
        "8️⃣ ارز ترون / TRX\n\n"
        "عدد مورد نظر رو به ربات بفرست."
    )
    
    await query.edit_message_text(text, parse_mode='HTML')

async def account_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = (
        "👤 <b>حساب کاربری</b>\n\n"
        "اطلاعات حساب کاربری شما:\n"
        "🆔 آیدی: {}\n"
        "📅 تاریخ عضویت: {}\n"
        "💰 موجودی: 0 تومان\n"
        "⭐ استارز خریداری شده: 0\n"
        "💎 پرمیوم خریداری شده: 0\n\n"
        "برای مشاهده جزئیات بیشتر با پشتیبانی تماس بگیرید."
    ).format(update.effective_user.id, "۱۴۰۵/۰۵/۲۶")
    
    await query.edit_message_text(text, parse_mode='HTML')

async def charge_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = (
        "💰 <b>افزایش موجودی</b>\n\n"
        "برای افزایش موجودی حساب خود، یکی از روش‌های زیر رو انتخاب کن:\n\n"
        "💳 کارت به کارت\n"
        "🪙 ارز دیجیتال (TRX/TON)\n"
        "🎁 کارت هدیه\n\n"
        "مبلغ مورد نظر رو به همراه روش پرداخت به ربات بفرست.\n"
        "مثال: `100,000 تومان - کارت به کارت`\n\n"
        "پشتیبانی: @ViolexSup"
    )
    
    await query.edit_message_text(text, parse_mode='HTML')

async def referral_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = (
        "👥 <b>زیر مجموعه گیری</b>\n\n"
        "با دعوت از دوستانت به ربات، از هر خرید آنها پورسانت دریافت کن!\n\n"
        "🔗 لینک دعوت شما:\n"
        f"https://t.me/{(await context.bot.get_me()).username}?start=ref_{update.effective_user.id}\n\n"
        "💰 پورسانت هر خرید: 10%\n"
        "🎁 پاداش ویژه: به ازای هر 10 زیر مجموعه فعال، 50,000 تومان پاداش نقدی!\n\n"
        "دوستانت رو دعوت کن و درآمدزایی کن! 🚀"
    )
    
    await query.edit_message_text(text, parse_mode='HTML')

async def support_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = (
        "📞 <b>پشتیبانی</b>\n\n"
        "برای ارتباط با پشتیبانی از یکی از راه‌های زیر استفاده کن:\n\n"
        "👤 پشتیبانی: @ViolexSup\n"
        "📢 گزارشات: @ViolexReport\n"
        "📧 ایمیل: support@violex.com\n\n"
        "⏰ ساعات پاسخگویی: ۲۴/۷\n\n"
        "سوالات خود را مطرح کن تا در سریع‌ترین زمان پاسخ داده بشه ✅"
    )
    
    await query.edit_message_text(text, parse_mode='HTML')

async def orders_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = (
        "📋 <b>وضعیت سفارشات</b>\n\n"
        "سفارشات شما:\n"
        "─────────────────\n"
        "🟢 سفارش #۱: استارز - تحویل شده\n"
        "🟡 سفارش #۲: پرمیوم - در حال پردازش\n"
        "🟢 سفارش #۳: گیفت استارزی - تحویل شده\n"
        "─────────────────\n\n"
        "برای مشاهده جزئیات هر سفارش، شماره آن رو به ربات بفرست.\n"
        "مثال: `سفارش 1`\n\n"
        "همچنین می‌تونی از پشتیبانی وضعیت سفارشات رو پیگیری کنی."
    )
    
    await query.edit_message_text(text, parse_mode='HTML')

async def channel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    text = (
        "📢 <b>باب کره (کانال)</b>\n\n"
        "به کانال رسمی رایان بپیوند:\n\n"
        "🔗 لینک کانال:\n"
        f"{CHANNEL_LINK}\n\n"
        "✅ با عضویت در کانال از آخرین اخبار، تخفیف‌ها و محصولات جدید مطلع شو!\n"
        "🎁 هدیه ویژه برای اعضای جدید کانال: ۱۰٪ تخفیف اولین خرید!\n\n"
        "همین الان عضو شو و از مزایای ویژه بهره‌مند شو! 🚀"
    )
    
    keyboard = [[InlineKeyboardButton("📢 عضویت در کانال", url=CHANNEL_LINK)]]
    await query.edit_message_text(
        text, 
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

# ============== تابع اصلی ==============

def main():
    application = Application.builder().token(TOKEN).build()

    # هندلر استارت
    application.add_handler(CommandHandler("start", start))
    
    # هندلرهای دکمه‌ها
    application.add_handler(CallbackQueryHandler(check_subscription, pattern="check_sub"))
    application.add_handler(CallbackQueryHandler(buy_handler, pattern="buy"))
    application.add_handler(CallbackQueryHandler(account_handler, pattern="account"))
    application.add_handler(CallbackQueryHandler(charge_handler, pattern="charge"))
    application.add_handler(CallbackQueryHandler(referral_handler, pattern="referral"))
    application.add_handler(CallbackQueryHandler(support_handler, pattern="support"))
    application.add_handler(CallbackQueryHandler(orders_handler, pattern="orders"))
    application.add_handler(CallbackQueryHandler(channel_handler, pattern="channel"))

    print("🤖 ربات Ryan با موفقیت روشن شد...")
    print(f"📢 کانال اجباری: {CHANNEL_LINK}")
    print(f"🆔 آیدی کانال: {CHANNEL_ID}")
    
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
