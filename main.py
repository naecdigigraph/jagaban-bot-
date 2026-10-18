import os
import json
import threading
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

# --- 🔐 BOT CONFIGURATION ---
TOKEN = "8575512512:AAEYG6ln7zhCRSqCI6UE9TIwT63T1"  # Ensure your complete Bot Token is active here
WEBAPP_URL = "https://naecdigigraph.github.io/jagaban-bot-/" # GitHub Pages Mini App Host URL

bot = telebot.TeleBot(TOKEN)
DATA_FILE = "players.json"

# --- 💾 PERSISTENT DATABASE ENGINE ---
def load_players():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading database: {e}")
            return {}
    return {}

def save_players():
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(players, f, indent=4)
    except Exception as e:
        print(f"Error saving database: {e}")

players = load_players()

def get_player(chat_id):
    chat_str = str(chat_id)
    if chat_str not in players:
        players[chat_str] = {
            "vault": 50000000,       # ₦50,000,000 starting cash
            "loyalty": 75,           # 75% Godfather / Party Loyalty
            "support": 60,           # 60% Public Support
            "influence": 20,         # 20 Political Influence Points
            "turn": 1,               # Current Political Month/Turn
            "rank": "Grassroots Mobilizer"
        }
        save_players()
    return players[chat_str]

# --- 🌐 RENDER HEALTH CHECK HTTP SERVER ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h1>Jagaban Sim: Kingmaker Backend Active</h1>")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# --- 📜 DYNAMIC POLITICAL EVENTS POOL ---
EVENTS = [
    {
        "title": "🚨 CRISIS AT THE PRIMARIES!",
        "desc": "Your key gubernatorial candidate in Lagos faces rebellion from disgruntled delegates claiming party favoritism!",
        "opt1": {"text": "💸 Pay off delegates (₦15M)", "cost": 15000000, "loyalty": 10, "support": -5, "inf": 5, "msg": "Delegates pacified! Loyalty increased."},
        "opt2": {"text": "🗣️ Deploy PR & Rallies (₦5M)", "cost": 5000000, "loyalty": -5, "support": 15, "inf": 2, "msg": "Public rally successful! Public support surged."}
    },
    {
        "title": "⚡ NATIONAL ASSEMBLY LOBBYING!",
        "desc": "A critical infrastructure bill needs approval to boost your regional economic influence.",
        "opt1": {"text": "🏛️ Lobby Lawmakers (₦20M)", "cost": 20000000, "loyalty": 15, "support": 5, "inf": 10, "msg": "Bill passed! Massive boost to Godfather influence."},
        "opt2": {"text": "📢 Mobilize Youth Movements (₦2M)", "cost": 2000000, "loyalty": -10, "support": 20, "inf": 3, "msg": "Youth mobilized! Public enthusiasm peaked."}
    },
    {
        "title": "📰 MEDIA SMEAR CAMPAIGN!",
        "desc": "Opposition news outlets have launched an investigative exposé targeting party financing!",
        "opt1": {"text": "🤐 Silence & Media Buyout (₦10M)", "cost": 10000000, "loyalty": 5, "support": 5, "inf": 4, "msg": "Exposé buried successfully."},
        "opt2": {"text": "🎙️ Press Conference Counter-Attack (₦1M)", "cost": 1000000, "loyalty": 0, "support": -10, "inf": 1, "msg": "Tense press conference held with mixed reactions."}
    }
]

# --- 🎮 TELEGRAM BOT HANDLERS ---
@bot.message_handler(commands=['start', 'dashboard'])
def start_game(message):
    chat_id = message.chat.id
    player = get_player(chat_id)
    
    # Pick current event based on turn
    event_idx = (player['turn'] - 1) % len(EVENTS)
    event = EVENTS[event_idx]
    
    markup = InlineKeyboardMarkup()
    
    # 🌟 Modern Web App Button (Opens full visual War Room UI inside Telegram)
    web_app_btn = InlineKeyboardButton(
        text="🏛️ Launch Political War Room (Mini App)", 
        web_app=WebAppInfo(url=WEBAPP_URL)
    )
    markup.add(web_app_btn)
    
    # Standard Action Choice Buttons
    btn1 = InlineKeyboardButton(event['opt1']['text'], callback_data=f"opt1_{event_idx}")
    btn2 = InlineKeyboardButton(event['opt2']['text'], callback_data=f"opt2_{event_idx}")
    markup.add(btn1)
    markup.add(btn2)

    dashboard_text = (
        f"👑 *JAGABAN SIM: KINGMAKER*\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📊 *POLITICAL DASHBOARD (Month {player['turn']})*\n"
        f"💰 *Vault:* ₦{player['vault']:,}\n"
        f"👑 *Network Loyalty:* {player['loyalty']}%\n"
        f"📈 *Public Support:* {player['support']}%\n"
        f"⚡ *Influence:* {player['influence']} PTS\n"
        f"🎖️ *Title:* {player['rank']}\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"*{event['title']}*\n"
        f"{event['desc']}\n\n"
        f"👇 *Choose your strategic move below or enter the War Room:* "
    )
    
    bot.send_message(chat_id, dashboard_text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_action(call):
    chat_id = call.message.chat.id
    player = get_player(chat_id)
    
    data = call.data
    if "_" in data:
        opt_type, event_idx = data.split("_")
        event_idx = int(event_idx)
        event = EVENTS[event_idx]
        choice = event['opt1'] if opt_type == "opt1" else event['opt2']
        
        # Check fund availability
        if player['vault'] < choice['cost']:
            bot.answer_callback_query(call.id, text="❌ Insufficient Vault Funds for this operation!", show_alert=True)
            return
            
        # Deduct / Update Player Metrics
        player['vault'] -= choice['cost']
        player['loyalty'] = min(100, max(0, player['loyalty'] + choice['loyalty']))
        player['support'] = min(100, max(0, player['support'] + choice['support']))
        player['influence'] += choice['inf']
        player['turn'] += 1
        
        # Title Progression Logic
        if player['influence'] >= 50:
            player['rank'] = "Regional Godfather"
        elif player['influence'] >= 100:
            player['rank'] = "National Kingmaker"
            
        save_players()
        
        bot.answer_callback_query(call.id, text=choice['msg'], show_alert=False)
        
        # Send Updated Dashboard with next turn
        start_game(call.message)

if __name__ == '__main__':
    print("Jagaban Sim Core Backend Running...")
    bot.infinity_polling()

