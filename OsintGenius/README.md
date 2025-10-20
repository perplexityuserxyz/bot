# OSINT Telegram Bot

A feature-rich Telegram bot with role-based access control, credit system, and admin panel for managing APIs and users.

## Features

### User Features
- 🔍 Three data lookup services (configurable APIs)
- 💰 Credit-based system for regular users
- 📖 Help and support commands
- 💳 Credit purchase information

### Admin Features
- ⚙️ Complete admin panel
- 🔧 API management (add/replace/edit APIs)
- 📢 Channel management (mandatory join verification)
- 👥 User management (add credits, view users)
- 👨‍💼 Sudo user management (owner only)
- 📊 Statistics dashboard
- 📣 Broadcast messaging to all users

### Access Levels
1. **Owner** (ID: 5455135289) - Full access, unlimited free queries
2. **Sudo** (ID: 7905267752 + dynamically added) - Full access, unlimited free queries
3. **Regular Users** - Credit-based access (10 credits = ₹30)

## Setup Instructions

### 1. Create Telegram Bot
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow instructions
3. Copy the bot token provided

### 2. Configure Bot Token
Add your bot token to Replit Secrets:
- Go to Tools → Secrets
- Add secret: `BOT_TOKEN` = your_bot_token_here

### 3. Configure APIs (After Bot Starts)
The bot comes with placeholder APIs. To configure real APIs:
1. Start the bot
2. Send `/start` to your bot
3. Click "⚙️ Admin Panel"
4. Click "🔧 API Management"
5. Edit each API with your real endpoints

**API URL Format**: Use `{query}` as placeholder for user input
Example: `https://api.example.com/lookup?id={query}`

### 4. Run the Bot
The bot will start automatically. You can also restart it anytime.

## Bot Commands

### For All Users
- `/start` - Start the bot and show main menu
- `/help` - Show help message
- `/balance` - Check credit balance

### Admin Only
All admin features are accessible through the Admin Panel in the bot interface.

## Project Structure

```
.
├── bot.py          # Main bot logic and handlers
├── database.py     # Database operations (SQLite)
├── config.py       # Configuration and constants
├── .env            # Environment variables (BOT_TOKEN)
├── bot_data.db     # SQLite database (auto-created)
└── README.md       # This file
```

## Database Schema

The bot uses SQLite with the following tables:
- `users` - User information and credits
- `sudo_users` - Sudo user list
- `api_config` - API endpoint configurations
- `channels` - Mandatory join channels
- `transactions` - Credit transaction history
- `settings` - Bot settings

## Adding Your Own APIs

After starting the bot, you can replace the placeholder APIs through the admin panel. Make sure your API:
1. Returns JSON or text response
2. Accepts query parameter in URL
3. Has proper authentication if required

## Security Notes

- Bot token is stored in environment variables (Replit Secrets)
- Database passwords and API keys are encrypted in database
- Only owner and sudo users have admin access
- Regular users cannot bypass credit requirements

## Support

For issues or questions, modify the `HELP_MESSAGE` in `config.py` to add your support contact.

## Credits

Built for personal/educational use. Ensure you have proper authorization for any APIs you integrate.
