import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler
)
from telegram.error import TelegramError
import requests
import urllib3
from database import Database
from config import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

db = Database()

WAITING_API_URL, WAITING_API_KEY, WAITING_CHANNEL_ID, WAITING_USER_ID, WAITING_CREDITS, WAITING_BROADCAST, WAITING_QUERY = range(7)

def is_owner(user_id):
    return user_id == OWNER_ID

def is_sudo(user_id):
    return user_id in SUDO_IDS or db.is_sudo(user_id)

def is_admin(user_id):
    return is_owner(user_id) or is_sudo(user_id)

def has_free_access(user_id):
    return is_owner(user_id) or is_sudo(user_id)

async def check_user_in_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    channels = db.get_all_channels()
    
    if not channels:
        return True
    
    for channel_id, channel_name in channels:
        try:
            member = await context.bot.get_chat_member(channel_id, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                keyboard = [[InlineKeyboardButton("Join Channel", url=f"https://t.me/{channel_id.replace('@', '')}")]]
                await update.message.reply_text(
                    f"⚠️ Please join our channel first:\n{channel_name}",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return False
        except Exception as e:
            logger.error(f"Error checking channel membership: {e}")
            continue
    
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.username, user.first_name)
    db.update_last_used(user.id)
    
    if db.is_banned(user.id):
        await update.message.reply_text("❌ You are banned from using this bot.")
        return
    
    if not await check_user_in_channels(update, context):
        return
    
    keyboard = [
        [InlineKeyboardButton("🔍 Lookup 1", callback_data="lookup_1"),
         InlineKeyboardButton("🔍 Lookup 2", callback_data="lookup_2")],
        [InlineKeyboardButton("🔍 Lookup 3", callback_data="lookup_3")],
        [InlineKeyboardButton("💰 My Balance", callback_data="balance"),
         InlineKeyboardButton("💳 Buy Credits", callback_data="buy_credits")],
        [InlineKeyboardButton("📖 Help", callback_data="help")]
    ]
    
    if is_admin(user.id):
        keyboard.append([InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel")])
    
    await update.message.reply_text(
        WELCOME_MESSAGE,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if db.is_banned(user_id):
        await query.edit_message_text("❌ You are banned from using this bot.")
        return
    
    if data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("🔍 Lookup 1", callback_data="lookup_1"),
             InlineKeyboardButton("🔍 Lookup 2", callback_data="lookup_2")],
            [InlineKeyboardButton("🔍 Lookup 3", callback_data="lookup_3")],
            [InlineKeyboardButton("💰 My Balance", callback_data="balance"),
             InlineKeyboardButton("💳 Buy Credits", callback_data="buy_credits")],
            [InlineKeyboardButton("📖 Help", callback_data="help")]
        ]
        
        if is_admin(user_id):
            keyboard.append([InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel")])
        
        await query.edit_message_text(
            WELCOME_MESSAGE,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "balance":
        credits = db.get_credits(user_id)
        status = "♾️ Unlimited" if has_free_access(user_id) else f"{credits} Credits"
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
        await query.edit_message_text(
            f"💰 Your Balance: {status}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "buy_credits":
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
        await query.edit_message_text(
            PAYMENT_INFO,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "help":
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
        await query.edit_message_text(
            HELP_MESSAGE,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data.startswith("lookup_"):
        lookup_type = data.split("_")[1]
        context.user_data['lookup_type'] = lookup_type
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
        await query.edit_message_text(
            f"🔍 Enter query for Lookup {lookup_type}:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return WAITING_QUERY
    
    elif data == "admin_panel":
        if not is_admin(user_id):
            await query.edit_message_text("❌ Access Denied")
            return
        
        keyboard = [
            [InlineKeyboardButton("🔧 API Management", callback_data="api_management"),
             InlineKeyboardButton("📢 Channels", callback_data="channel_management")],
            [InlineKeyboardButton("👥 User Management", callback_data="user_management"),
             InlineKeyboardButton("📊 Statistics", callback_data="stats")],
            [InlineKeyboardButton("📣 Broadcast", callback_data="broadcast")],
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ]
        
        if is_owner(user_id):
            keyboard.insert(2, [InlineKeyboardButton("👨‍💼 Sudo Management", callback_data="sudo_management")])
        
        await query.edit_message_text(
            "⚙️ Admin Panel\n\nSelect an option:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "api_management":
        if not is_admin(user_id):
            await query.edit_message_text("❌ Access Denied")
            return
        
        apis = db.get_all_apis()
        text = "🔧 API Management\n\n"
        for api_name, api_url, is_active in apis:
            status = "✅" if is_active else "❌"
            text += f"{status} {api_name}: {api_url[:50]}...\n"
        
        keyboard = [
            [InlineKeyboardButton("✏️ Edit Lookup 1", callback_data="edit_api_lookup_1")],
            [InlineKeyboardButton("✏️ Edit Lookup 2", callback_data="edit_api_lookup_2")],
            [InlineKeyboardButton("✏️ Edit Lookup 3", callback_data="edit_api_lookup_3")],
            [InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data.startswith("edit_api_"):
        if not is_admin(user_id):
            await query.edit_message_text("❌ Access Denied")
            return
        
        api_name = data.replace("edit_api_", "")
        context.user_data['editing_api'] = api_name
        
        keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data="api_management")]]
        await query.edit_message_text(
            f"✏️ Editing {api_name}\n\nSend new API URL:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return WAITING_API_URL
    
    elif data == "channel_management":
        if not is_admin(user_id):
            await query.edit_message_text("❌ Access Denied")
            return
        
        channels = db.get_all_channels()
        text = "📢 Channel Management\n\n"
        if channels:
            for channel_id, channel_name in channels:
                text += f"• {channel_name} ({channel_id})\n"
        else:
            text += "No channels configured."
        
        keyboard = [
            [InlineKeyboardButton("➕ Add Channel", callback_data="add_channel")],
            [InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "add_channel":
        if not is_admin(user_id):
            await query.edit_message_text("❌ Access Denied")
            return
        
        keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data="channel_management")]]
        await query.edit_message_text(
            "➕ Add Channel\n\nSend channel ID (e.g., @channelname or -100123456789):",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return WAITING_CHANNEL_ID
    
    elif data == "user_management":
        if not is_admin(user_id):
            await query.edit_message_text("❌ Access Denied")
            return
        
        keyboard = [
            [InlineKeyboardButton("➕ Add Credits", callback_data="add_credits_menu")],
            [InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]
        ]
        
        await query.edit_message_text(
            "👥 User Management\n\nSelect an option:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "add_credits_menu":
        if not is_admin(user_id):
            await query.edit_message_text("❌ Access Denied")
            return
        
        keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data="user_management")]]
        await query.edit_message_text(
            "➕ Add Credits\n\nSend user ID:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return WAITING_USER_ID
    
    elif data == "sudo_management":
        if not is_owner(user_id):
            await query.edit_message_text("❌ Access Denied")
            return
        
        sudo_users = db.get_all_sudo()
        text = "👨‍💼 Sudo Management\n\n"
        if sudo_users:
            for sudo_id in sudo_users:
                text += f"• {sudo_id}\n"
        else:
            text += "No sudo users."
        
        keyboard = [
            [InlineKeyboardButton("➕ Add Sudo", callback_data="add_sudo")],
            [InlineKeyboardButton("➖ Remove Sudo", callback_data="remove_sudo")],
            [InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]
        ]
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "add_sudo":
        if not is_owner(user_id):
            await query.edit_message_text("❌ Access Denied")
            return
        
        keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data="sudo_management")]]
        await query.edit_message_text(
            "➕ Add Sudo\n\nSend user ID:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data['sudo_action'] = 'add'
        return WAITING_USER_ID
    
    elif data == "remove_sudo":
        if not is_owner(user_id):
            await query.edit_message_text("❌ Access Denied")
            return
        
        keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data="sudo_management")]]
        await query.edit_message_text(
            "➖ Remove Sudo\n\nSend user ID:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data['sudo_action'] = 'remove'
        return WAITING_USER_ID
    
    elif data == "stats":
        if not is_admin(user_id):
            await query.edit_message_text("❌ Access Denied")
            return
        
        total_users = db.get_total_users()
        sudo_count = len(db.get_all_sudo())
        
        text = f"""
📊 Bot Statistics

👥 Total Users: {total_users}
👨‍💼 Sudo Users: {sudo_count}
📢 Active Channels: {len(db.get_all_channels())}
🔧 Active APIs: {len([a for a in db.get_all_apis() if a[2] == 1])}
"""
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "broadcast":
        if not is_admin(user_id):
            await query.edit_message_text("❌ Access Denied")
            return
        
        keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data="admin_panel")]]
        await query.edit_message_text(
            "📣 Broadcast Message\n\nSend the message you want to broadcast:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return WAITING_BROADCAST

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if 'lookup_type' in context.user_data:
        lookup_type = context.user_data['lookup_type']
        
        if not has_free_access(user_id):
            credits = db.get_credits(user_id)
            if credits < CREDITS_PER_QUERY:
                await update.message.reply_text("❌ Insufficient credits. Please buy credits first.")
                return ConversationHandler.END
        
        api_config = db.get_api_config(f'lookup_{lookup_type}')
        
        if not api_config:
            await update.message.reply_text("❌ API not configured. Please contact admin.")
            return ConversationHandler.END
        
        await update.message.reply_text("🔍 Processing your query...")
        
        try:
            final_url = api_config['url'].replace('{query}', text)
            logger.info(f"Making API request to: {final_url}")
            
            response = requests.get(
                final_url,
                timeout=15,
                verify=False
            )
            
            logger.info(f"API Response Status: {response.status_code}")
            logger.info(f"API Response: {response.text[:200]}")
            
            if response.status_code == 200:
                result_text = f"✅ Results for: {text}\n\n"
                result_text += f"{response.text[:4000]}"
                
                if not has_free_access(user_id):
                    db.deduct_credits(user_id, CREDITS_PER_QUERY, f"Lookup {lookup_type}")
                    remaining = db.get_credits(user_id)
                    result_text += f"\n\n💰 Credits remaining: {remaining}"
            else:
                result_text = f"❌ API returned status code: {response.status_code}\n\n{response.text[:500]}"
                logger.error(f"API Error - Status: {response.status_code}, Response: {response.text}")
        
        except Exception as e:
            logger.error(f"API Error: {e}")
            result_text = f"❌ Error: {str(e)}"
        
        keyboard = [[InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]]
        await update.message.reply_text(result_text, reply_markup=InlineKeyboardMarkup(keyboard))
        
        del context.user_data['lookup_type']
        return ConversationHandler.END
    
    return ConversationHandler.END

async def handle_api_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        return ConversationHandler.END
    
    api_url = update.message.text
    context.user_data['api_url'] = api_url
    
    keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data="api_management")]]
    await update.message.reply_text(
        "✏️ Now send API Key (or send 'skip' if not required):",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return WAITING_API_KEY

async def handle_api_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        return ConversationHandler.END
    
    api_key = update.message.text if update.message.text.lower() != 'skip' else ''
    api_name = context.user_data.get('editing_api')
    api_url = context.user_data.get('api_url')
    
    db.update_api_config(api_name, api_url, api_key)
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="api_management")]]
    await update.message.reply_text(
        f"✅ API {api_name} updated successfully!",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    context.user_data.clear()
    return ConversationHandler.END

async def handle_channel_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        return ConversationHandler.END
    
    channel_id = update.message.text
    
    try:
        chat = await context.bot.get_chat(channel_id)
        db.add_channel(channel_id, chat.title or channel_id)
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="channel_management")]]
        await update.message.reply_text(
            f"✅ Channel added: {chat.title}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="channel_management")]]
        await update.message.reply_text(
            f"❌ Error: {str(e)}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    return ConversationHandler.END

async def handle_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        return ConversationHandler.END
    
    target_user_id = update.message.text
    
    try:
        target_user_id = int(target_user_id)
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID")
        return ConversationHandler.END
    
    if context.user_data.get('sudo_action') == 'add':
        db.add_sudo(target_user_id, user_id)
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="sudo_management")]]
        await update.message.reply_text(
            f"✅ User {target_user_id} added as sudo",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data.clear()
        return ConversationHandler.END
    
    elif context.user_data.get('sudo_action') == 'remove':
        db.remove_sudo(target_user_id)
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="sudo_management")]]
        await update.message.reply_text(
            f"✅ User {target_user_id} removed from sudo",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data.clear()
        return ConversationHandler.END
    
    else:
        context.user_data['target_user_id'] = target_user_id
        keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data="user_management")]]
        await update.message.reply_text(
            "➕ How many credits to add?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return WAITING_CREDITS

async def handle_credits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        return ConversationHandler.END
    
    try:
        credits = int(update.message.text)
        target_user_id = context.user_data.get('target_user_id')
        
        db.add_user(target_user_id, None, None)
        db.add_credits(target_user_id, credits, f"Added by admin {user_id}")
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="user_management")]]
        await update.message.reply_text(
            f"✅ {credits} credits added to user {target_user_id}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        try:
            await context.bot.send_message(
                target_user_id,
                f"🎉 You received {credits} credits from admin!"
            )
        except:
            pass
        
    except ValueError:
        await update.message.reply_text("❌ Invalid credit amount")
    
    context.user_data.clear()
    return ConversationHandler.END

async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        return ConversationHandler.END
    
    broadcast_message = update.message.text
    user_ids = db.get_all_user_ids()
    
    success = 0
    failed = 0
    
    status_msg = await update.message.reply_text("📣 Broadcasting...")
    
    for uid in user_ids:
        try:
            await context.bot.send_message(uid, broadcast_message)
            success += 1
        except Exception as e:
            failed += 1
            logger.error(f"Broadcast failed for {uid}: {e}")
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]]
    await status_msg.edit_text(
        f"✅ Broadcast Complete\n\nSuccess: {success}\nFailed: {failed}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    return ConversationHandler.END

def main():
    if not BOT_TOKEN:
        print("❌ Error: BOT_TOKEN not found in environment variables!")
        print("Please set BOT_TOKEN in your .env file or Replit Secrets")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(button_handler),
            CommandHandler("start", start)
        ],
        states={
            WAITING_API_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_api_url)],
            WAITING_API_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_api_key)],
            WAITING_CHANNEL_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_channel_id)],
            WAITING_USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_id)],
            WAITING_CREDITS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_credits)],
            WAITING_BROADCAST: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_broadcast)],
            WAITING_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        },
        fallbacks=[
            CallbackQueryHandler(button_handler),
            CommandHandler("start", start)
        ],
        allow_reentry=True
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot started successfully!")
    print("🤖 Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
