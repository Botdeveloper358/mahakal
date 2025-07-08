import json
import datetime
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# === CONFIG ===
TOKEN = "7408316421:AAFqxaB39EtKCepdAO-8X-4uJMna92OfecM"
bot = Bot(token=TOKEN)
USERS_FILE = "users.json"
ADMIN_ID = 7098681454
GST_PREFIX = "GSTX"

# === CHANNELS ===
REQUIRED_CHANNELS = [
    ("@SF_RESET", "🧠 NODE - ZERO"),
    ("@Teencarder", "💻 NODE - ONE"),
    ("@webhubkl", "🌐 NODE - TWO"),
    ("@botclubhu", "🎯 NODE - THREE")
]

# === QUIZ LIST ===
QUIZ_QUESTIONS = [
    {"question": "Which tool is used for port scanning?\n\nA. Nmap\nB. Hydra\nC. SQLmap\nD. Wireshark", "answer": "a"},
    {"question": "Which one is a packet sniffer?\n\nA. John\nB. Wireshark\nC. Nikto\nD. Nessus", "answer": "b"},
    {"question": "Which tool is used for brute-force?\n\nA. Nmap\nB. Hydra\nC. Sqlmap\nD. Nikto", "answer": "b"},
]

# === HELPERS ===
def load_json(filename):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        return {}

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def get_today_question():
    index = datetime.datetime.utcnow().timetuple().tm_yday % len(QUIZ_QUESTIONS)
    return QUIZ_QUESTIONS[index]

# === HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_json(USERS_FILE)
    if user_id not in users:
        users[user_id] = {"referrals": 0, "wallet": "", "gst": ""}
        save_json(USERS_FILE, users)

    keyboard = [
        [InlineKeyboardButton(name, url=f"https://t.me/{channel[1:]}")] for channel, name in REQUIRED_CHANNELS
    ]
    keyboard.append([InlineKeyboardButton("✅ I Have Joined", callback_data="check_join")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🔐 ACCESS REQUIRED 🔐\n\n"
        "Join all hacker nodes to unlock the bot.\n\n"
        "👨‍💻 Developer: @teamtoxic009",
        reply_markup=reply_markup
    )

async def check_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("✅ ACCESS GRANTED. Use /register to start.")

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send your wallet address using:\n\n`/wallet your_address`")

async def wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_json(USERS_FILE)

    if len(context.args) == 0:
        await update.message.reply_text("❌ Usage: /wallet your_address")
        return

    address = context.args[0]
    if user_id in users:
        users[user_id]["wallet"] = address
        save_json(USERS_FILE, users)
        await update.message.reply_text("✅ Wallet address saved.")
    else:
        await update.message.reply_text("❌ Please use /start first.")

async def refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_json(USERS_FILE)
    if user_id not in users:
        await update.message.reply_text("Use /start first.")
        return
    link = f"https://t.me/{context.bot.username}?start={user_id}"
    await update.message.reply_text(f"👥 Invite link:\n{link}\nReferrals: {users[user_id]['referrals']}")

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = get_today_question()
    await update.message.reply_text(f"🧠 DAILY QUIZ 🧠\n\n{q['question']}\n\nReply with A, B, C, or D")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.lower().strip()
    correct = get_today_question()["answer"]
    if msg in ["a", "b", "c", "d"]:
        if msg == correct:
            await update.message.reply_text("✅ Correct Answer!")
        else:
            await update.message.reply_text("❌ Wrong Answer!")

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_json(USERS_FILE)
    user = users.get(user_id, {})

    if user.get("referrals", 0) < 100:
        await update.message.reply_text("❌ You need at least 100 referrals to withdraw.")
        return

    if not user.get("wallet"):
        await update.message.reply_text("❌ Set your wallet first using /wallet")
        return

    if not user.get("gst"):
        await update.message.reply_text("❌ You must generate GST ID first using /gst")
        return

    await update.message.reply_text(f"✅ Withdraw requested for wallet: {user['wallet']}\nGST ID: {user['gst']}")

async def gst(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    users = load_json(USERS_FILE)
    user = users.get(user_id, {})

    if user.get("gst"):
        await update.message.reply_text(f"Your GST ID: `{user['gst']}`", parse_mode="Markdown")
        return

    new_gst = f"{GST_PREFIX}{random.randint(100000, 999999)}"
    user["gst"] = new_gst
    users[user_id] = user
    save_json(USERS_FILE, users)
    await update.message.reply_text(f"✅ Your GST ID: `{new_gst}`\nUse it during withdrawal.", parse_mode="Markdown")

# === START BOT ===
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("register", register))
application.add_handler(CommandHandler("wallet", wallet))
application.add_handler(CommandHandler("refer", refer))
application.add_handler(CommandHandler("quiz", quiz))
application.add_handler(CommandHandler("withdraw", withdraw))
application.add_handler(CommandHandler("gst", gst))
application.add_handler(CallbackQueryHandler(check_join, pattern="check_join"))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == "__main__":
    application.run_polling()
