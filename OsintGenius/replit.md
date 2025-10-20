# Overview

This is a Telegram bot application that provides OSINT (Open Source Intelligence) data lookup services with a sophisticated access control system. The bot implements a role-based hierarchy (Owner → Sudo → Regular Users) and uses a credit-based economy for regular users. It features an admin panel for managing APIs, channels, users, and broadcasting messages.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Application Structure

**Core Technology**: Python-based Telegram bot using `python-telegram-bot` library

**Architecture Pattern**: Event-driven with conversation handlers for multi-step interactions

The application uses a modular structure with clear separation of concerns:
- `bot.py` - Main application logic, command handlers, and conversation flows
- `config.py` - Configuration management and environment variables
- `database.py` - Data persistence layer with SQLite
- `README.md` - Documentation and setup instructions

## Access Control System

**Three-tier role hierarchy**:

1. **Owner** (hardcoded ID: 5455135289) - Superuser with complete system access
2. **Sudo Users** (base ID: 7905267752 + dynamically added) - Admin privileges with unlimited queries
3. **Regular Users** - Credit-based access requiring payment

**Design Decision**: Hardcoded owner ID ensures unchangeable root access, while sudo users can be dynamically managed through the database. This provides flexibility without compromising security.

## Credit System

**Economic Model**: Pay-per-query system where regular users consume credits for each lookup

- 1 credit = 1 query
- 10 credits = ₹30 (Indian Rupees)
- Owner and Sudo users bypass credit checks entirely

**Rationale**: Creates a sustainable monetization model while rewarding admins with free access. The credit system is enforced at the query execution level rather than the command level for precise tracking.

## Conversation Flow Architecture

**Multi-step operations** using ConversationHandler states:
- `WAITING_API_URL`, `WAITING_API_KEY` - API configuration
- `WAITING_CHANNEL_ID` - Channel management
- `WAITING_USER_ID`, `WAITING_CREDITS` - User credit management
- `WAITING_BROADCAST` - Mass messaging
- `WAITING_QUERY` - Data lookup input

**Design Pattern**: Stateful conversations allow complex admin operations through guided interactions, making the bot more user-friendly while maintaining data integrity through validation steps.

## Data Persistence

**Technology**: SQLite database with schema-defined tables

**Core Tables**:
1. `users` - User profiles, credit balances, ban status, usage tracking
2. `sudo_users` - Dynamic sudo user registry with audit trail
3. `api_config` - Configurable API endpoints with activation flags
4. `channels` - Mandatory join verification for channel list
5. `transactions` - Payment and credit history (schema partially shown)

**Design Decision**: SQLite chosen for simplicity and zero-configuration deployment. Single-file database is sufficient for Telegram bot scale, and the schema supports future analytics through transaction logging.

## API Management System

**Dynamic API Configuration**: Admins can add/edit/replace API endpoints without code changes

**URL Template System**: APIs use `{query}` placeholder that gets replaced with user input at runtime
- Example: `https://api.example.com/lookup?id={query}`

**Multi-service Architecture**: Three separate lookup services (lookup1, lookup2, lookup3) allow different data providers or query types

**Activation Control**: APIs can be toggled active/inactive without deletion, enabling temporary service suspension

## Channel Verification

**Mandatory Join Feature**: Bot can enforce channel membership before allowing access

**Verification Flow**:
1. Check user membership across all active channels
2. Block access if not member of any required channel
3. Provide join links for missing channels

**Design Decision**: Channel verification serves dual purpose - community building and quality control. The verification is checked before query execution rather than at bot start to handle dynamic membership changes.

## Admin Panel Interface

**Inline Keyboard Navigation**: Nested menu system for all admin operations
- Main Admin Panel → Category-specific panels → Action selection
- Breadcrumb-style navigation with back buttons

**Feature Categories**:
- API Management (CRUD operations on endpoints)
- Channel Management (add/remove required channels)
- User Management (credit allocation, user listing)
- Sudo Management (owner-only privilege delegation)
- Statistics Dashboard (user counts, system metrics)
- Broadcast System (mass messaging)

**Security**: Admin functions check `is_admin()` or `is_owner()` before execution

## Payment Integration

**Manual Payment Processing**: Payment info displayed through bot, verification handled by admin

**Payment Flow**:
1. User requests to buy credits (`/buy` command)
2. Bot displays payment methods (UPI, PhonePe, Paytm)
3. User sends payment screenshot to admin
4. Admin manually adds credits through admin panel

**Rationale**: Manual approval prevents automated fraud and allows flexibility in payment methods without complex integration. Suitable for small-scale operations with manageable transaction volumes.

# External Dependencies

## Telegram Bot API

**Library**: `python-telegram-bot` (primary framework)

**Key Features Used**:
- Application framework for bot lifecycle
- Command handlers for text commands
- Callback query handlers for inline keyboard interactions
- Message handlers for text input collection
- Conversation handlers for multi-step flows
- Error handling through TelegramError

**Authentication**: Requires `BOT_TOKEN` stored in environment variables/Replit Secrets

## HTTP Client

**Library**: `requests` (for API calls to external OSINT services)

**Usage**: Makes GET/POST requests to configured API endpoints with user query substitution

## Database

**Technology**: SQLite3 (built-in Python library)

**File**: `bot_data.db` (auto-created in application directory)

**No external database service required** - fully self-contained

## Environment Management

**Library**: `python-dotenv` (for environment variable loading)

**Configuration Source**: 
- `.env` file (local development)
- Replit Secrets (production deployment)

**Required Variables**:
- `BOT_TOKEN` - Telegram bot authentication token from BotFather

## Logging

**Built-in**: Python `logging` module configured for INFO level

**Purpose**: Tracks bot operations, errors, and user interactions for debugging and monitoring

## External OSINT APIs

**Configurable Third-party Services**: The bot integrates with external data lookup APIs (user-configured)

**Integration Pattern**: 
- URL template stored in database
- Runtime query substitution
- Optional API key support
- Response forwarded directly to user

**Examples**: Phone number lookup, email verification, social media OSINT, etc. (specific APIs configured post-deployment)

**Note**: No specific external APIs are hardcoded - all are dynamically configured through the admin panel.