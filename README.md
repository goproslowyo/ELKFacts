# Elk Facts Twitch Bot

A simple Twitch chat bot that responds to the `!elkfact` command with random elk-related facts.

## Features

- Responds to `!elkfact` command with random elk facts
- Asynchronous message handling
- Error logging and handling
- Easy configuration through environment variables

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

### Getting Your Credentials

#### OAuth Token
1. Visit https://twitchapps.com/tmi/
2. Click "Connect with Twitch"
3. Log in with your bot's Twitch account
4. Copy the generated token - it should look like this: `oauth:abcdefghijklmnopqrstuvwxyz1234`
   - The token MUST start with `oauth:`
   - Add this full string (including `oauth:`) as your `TMI_TOKEN` in the `.env` file

#### Client ID
1. Go to the Twitch Developer Console (https://dev.twitch.tv/console)
2. Log in with your Twitch account
3. Click "Register Your Application"
4. Fill in the application name and OAuth Redirect URL (can be http://localhost)
5. Copy the generated Client ID - it will look like: `a1b2c3d4e5f6g7h8i9j0`

#### Bot Settings in .env
```env
TMI_TOKEN=oauth:abcdefghijklmnopqrstuvwxyz1234  # Your OAuth token (must start with oauth:)
CLIENT_ID=a1b2c3d4e5f6g7h8i9j0                  # Your application's client ID
BOT_NICK=elkfactbot                             # Your bot's Twitch username
CHANNEL=mychannel                               # Channel to join (without # symbol)
```

## Usage

1. Start the bot:
```bash
python elkfact_bot.py
```

2. In Twitch chat, type:
```
!elkfact
```

The bot will respond with a random elk fact!

## Error Handling

The bot includes comprehensive error handling and logging:
- Connection issues are logged and retried
- Command errors are caught and logged
- Critical errors are logged with full stack traces

## Contributing

Feel free to add more elk facts or improve the bot's functionality by submitting pull requests!

## License

This project is open source and available under the MIT License.
