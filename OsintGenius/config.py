import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN', '7927707262:AAHU_M12R7HSS1lieEn96jV_biAEi_W40jU')

OWNER_ID = 5455135289
SUDO_IDS = [7905267752]

CREDITS_PER_QUERY = 1

PAYMENT_INFO = """
💳 Payment Details:
10 Credits = ₹30

Payment Methods:
UPI: https://t.me/Diffferentiator
PhonePe: https://t.me/Diffferentiator
Paytm: https://t.me/Diffferentiator

After payment, send screenshot to admin for credit approval.
"""

WELCOME_MESSAGE = """
╔═══════════════════════════╗
║   🔍 OSINT LOOKUP BOT 🔍   ║
╚═══════════════════════════╝

Welcome to the most advanced OSINT data lookup service!

🎯 Available Services:
━━━━━━━━━━━━━━━━━━━━━
📱 Aadhar Lookup
📞 Number Info
👨‍👩‍👧‍👦 Family Details

💎 Access Levels:
━━━━━━━━━━━━━━━━━━━━━
👑 Owner & Sudo: Unlimited Free
💰 Users: Credit-based (10 credits = ₹30)

Choose an option from the menu below:
"""

HELP_MESSAGE = """
╔═════════════════════════╗
║   📖 BOT COMMANDS 📖    ║
╚═════════════════════════╝

🔍 LOOKUP SERVICES
━━━━━━━━━━━━━━━━━━━━
/aadhar - Aadhar to Details
/num - Number Information
/familyinfo - Family Details

💰 CREDIT MANAGEMENT
━━━━━━━━━━━━━━━━━━━━
/balance - Check Balance
/buy - Purchase Credits

ℹ️ GENERAL
━━━━━━━━━━━━━━━━━━━━
/start - Main Menu
/help - This Help Message

━━━━━━━━━━━━━━━━━━━━
💬 Need Help? Contact Admin
"""
