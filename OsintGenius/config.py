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
👋 Welcome to OSINT Bot!

This bot provides various data lookup services.

🔹 Owner & Sudo: Free unlimited access
🔹 Regular Users: Credit-based system

Choose an option from below:
"""

HELP_MESSAGE = """
📖 Bot Commands:

🔍 Data Lookup:
/lookup1 - Data Lookup Service 1
/lookup2 - Data Lookup Service 2  
/lookup3 - Data Lookup Service 3

💰 Credits:
/balance - Check your credit balance
/buy - Purchase credits

ℹ️ Info:
/help - Show this message
/start - Main menu

For support, contact admin.
"""
