import telebot
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8575512512:AAEYG6ln7zhCRSqCI6UE9TIwT63T17F0JtU"

bot = telebot.TeleBot(TOKEN)
players = {}

@bot.message_handler(commands=['start'])
def start_game(message):
    chat_id = message.chat.id
    players[chat_id] = {
        "vault": 50000000,
        "loyalty": 75,
        "support": 60,
        "turn": 1
    }
    send_dashboard(chat_id, "🏛️ *WELCOME TO JAGABAN SIM: KINGMAKER!*\n\nYou are the ultimate political Godfather. Your goal is to navigate party politics, secure delegates, and maintain your empire across Nigeria without getting betrayed or ousted!")

def send_dashboard(chat_id, text_prefix):
    stats = players[chat_id]
    msg = f"{text_prefix}\n\n"
    msg += f"📊 *YOUR POLITICAL DASHBOARD (Turn {stats['turn']})*\n"
    msg += f"------------------------------------\n"
    msg += f"💰 Party Vault: *₦{stats['vault']:,}*\n"
    msg += f"🤝 Network Loyalty: *{stats['loyalty']}%*\n"
    msg += f"🗳️ Public Support: *{stats['support']}%*\n"
    msg += f"------------------------------------\n\n"
    msg += f"🚨 *CRISIS AT THE PRIMARIES!*\n"
    msg += f"Your key gubernatorial candidate in Lagos is facing a rebellion from disgruntled delegates claiming party favoritism!"

    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("💵 Pay off delegates (₦15M)", callback_data="choice_pay"))
    markup.row(InlineKeyboardButton("👑 Replace with loyalist", callback_data="choice_replace"))
    markup.row(InlineKeyboardButton("📢 Deploy PR & Rallies (₦5M)", callback_data="choice_pr"))

    bot.send_message(chat_id, msg, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_choice(call):
    chat_id = call.message.chat.id
    if chat_id not in players:
        bot.answer_callback_query(call.id, "Please restart with /start")
        return

    stats = players[chat_id]
    stats['turn'] += 1

    if call.data == "choice_pay":
        stats['vault'] -= 15000000
        stats['loyalty'] += 10
        response = "✅ *Result:* You settled the delegates with ₦15M. Loyalty rose, but your vault took a hit!"
    elif call.data == "choice_replace":
        stats['loyalty'] -= 15
        stats['support'] -= 10
        response = "⚠️ *Result:* You replaced the candidate! Disgruntled members defected to the opposition."
    elif call.data == "choice_pr":
        stats['vault'] -= 5000000
        stats['support'] += 15
        response = "🔥 *Result:* Your PR campaign went viral! Public enthusiasm jumped!"

    bot.answer_callback_query(call.id, "Decision recorded!")
    send_dashboard(chat_id, response)

# Resilient polling loop that automatically reconnects if network drops
while True:
    try:
        print("⚡ Jagaban Sim Bot is running live...")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Network error caught: {e}. Retrying in 5 seconds...")
        time.sleep(5)

