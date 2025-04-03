# Elk Facts Twitch Bot

A simple Twitch chat bot that responds to the `!elkfact` command with random elk-related facts.

## Features

- Responds to `!elkfact` command with random elk facts
- Asynchronous message handling
- Error logging and handling
- Easy configuration through environment variables
- Secure OAuth2 implementation with confidential client

## Prerequisites

- Python 3.7 or higher
- A Twitch account for the bot
- Twitch OAuth token and Client ID

## Installation

1. Clone this repository
2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill in your Twitch credentials:
```bash
cp .env.example .env
```

4. Edit the `.env` file with your Twitch credentials:

### Setting Up OAuth (Confidential Client)

1. Go to the Twitch Developer Console (https://dev.twitch.tv/console)
2. Log in with your Twitch account
3. Click "Register Your Application"
4. Fill in the following details:
   - Name: Choose a name for your twitch developer application (e.g., "MyElkFactBot")
   - OAuth Redirect URLs: Set to `http://localhost:3000/callback`
   - Category: Choose "Chat Bot"
   - **Application Type: Confidential Client** (Important for security!)
5. Required OAuth Scopes:
   - `chat:read` (allows reading chat messages)
   - `chat:edit` (allows sending chat messages)
6. Click "Create"
7. On the next page:
   - Copy the Client ID
   - Click "New Secret" to generate a Client Secret
   - Store both values securely - you won't be able to see the secret again

### Security Best Practices

1. Token Storage:
   - Never commit your .env file or token cache
   - Store credentials only in environment variables
   - Use secure file permissions for .env and token cache

2. Client Secret:
   - Keep your client secret secure
   - Rotate secrets periodically
   - Never share or expose your secret

#### Bot Settings in .env
```env
CLIENT_ID=your_client_id_here              # Your application's client ID
CLIENT_SECRET=your_client_secret_here      # Your application's client secret
CHANNEL=mychannel                          # Channel to join (without # symbol)
TOKEN_CACHE_FILE=.oauth_cache.json         # Optional: Path to cache OAuth token
```

## Usage

1. Start the bot:
```bash
python elkfact_bot.py
```

2. On first run, the bot will:
   - Display a Twitch authorization URL
   - Ask you to visit this URL in your browser
   - Request authorization for your Twitch account
   - Redirect you to http://localhost:3000/callback
   - If successful, the text will show "Authorization successful! You can close this window." or similar.

3. After successful authorization:
   - The bot will connect to Twitch chat
   - Your authorization will be cached for future runs
   - You won't need to re-authorize unless the cache expires
   - Token refresh happens automatically when needed

4. In Twitch chat, type:
```
!help
!ekfacts 3
!elkfact
```

The bot will respond with a random elk fact!

Note: The bot uses your authorized Twitch account to connect to chat. Make sure to log in with the account you want the bot to use when authorizing.

## Error Handling

The bot includes comprehensive error handling and logging:
- Connection issues are logged and retried
- Command errors are caught and logged
- Critical errors are logged with full stack traces
- OAuth errors are handled with automatic token refresh

## Security Notes

1. Token Refresh:
   - The bot automatically handles token refresh
   - Refresh tokens are stored securely
   - Invalid tokens trigger reauthorization

2. Error Recovery:
   - OAuth errors trigger automatic recovery
   - Failed refreshes initiate new authorization
   - All sensitive errors are logged securely

3. Data Protection:
   - Tokens are never logged
   - Credentials are kept in memory only
   - File permissions are enforced for sensitive files

## Contributing

Feel free to add more elk facts or improve the bot's functionality by submitting pull requests!

## License

This project is open source and available under the MIT License.
