import os
import threading
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

TOKEN = "8575512512:AAEYG6ln7zhCRSqCI6UE9TIwT63T1..."  # Make sure your full bot token is inside these quotes!

bot = telebot.TeleBot(TOKEN)

# In-memory Game State Database
players = {}

def get_player(chat_id):
    if chat_id not in players:
        players[chat_id] = {
            "vault": 50000000,      # ₦50M starting funds
            "loyalty": 75,          # 75% Godfather loyalty
            "support": 60,          # 60% Public support
            "influence": 20,        # 20 Influence points
            "turn": 1,              # Turn/Month index
            "title": "Grassroots Mobilizer"
        }
    return players[chat_id]

# --- 🌐 HTTP Health Check Server for Render Free Tier ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>Jagaban Sim Server Active</h1>")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# --- 🎮 Telegram Bot Handlers ---
@bot.message_handler(commands=['start'])
def start_game(message):
    chat_id = message.chat.id
    player = get_player(chat_id)
    
    markup = InlineKeyboardMarkup()
    
    # Web App button for our upcoming visual frontend
    web_app_btn = InlineKeyboardButton(
        text="🏛️ Open Political War Room", 
        web_app=WebAppInfo(url="https://naecdigigraph.github.io/jagaban-bot-/")
    )
    markup.add(web_app_btn)

    welcome_text = (
        f"👑 *WELCOME TO JAGABAN SIM: KINGMAKER*\n\n"
        f"You step into the shoes of the ultimate political strategist.\n\n"
        f"📊 *Current Status (Turn {player['turn']}):*\n"
        f"💰 *Vault:* ₦{player['vault']:,}\n"
        f"👑 *Godfather Loyalty:* {player['loyalty']}%\n"
        f"📈 *Public Support:* {player['support']}%\n"
        f"⚡ *Influence Points:* {player['influence']}\n\n"
        f"Tap below to open your interactive **Political War Room**!"
    )
    
    bot.send_message(chat_id, welcome_text, parse_mode="Markdown", reply_markup=markup)

if __name__ == '__main__':
    print("Jagaban Sim Bot is running...")
    bot.infinity_polling()

