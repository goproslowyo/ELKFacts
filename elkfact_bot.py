import os
import random
import asyncio
from dotenv import load_dotenv
from twitchio.ext import commands
import logging
from functools import lru_cache
from typing import List, Dict
from oauth import TwitchOAuth
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class RateLimiter:
    """Handles Twitch chat message rate limiting."""
    def __init__(self):
        self.messages = []
        self.mod_messages = []
        self.last_message_time = {}  # Per channel message timing

    async def can_send_message(self, channel: str, is_mod: bool = False) -> bool:
        """
        Check if a message can be sent according to Twitch rate limits.

        Regular users: 20 msgs/30sec, 1 msg/sec per channel
        Mods/VIPs: 100 msgs/30sec
        """
        current_time = time.time()

        # Clean up old messages (older than 30 seconds)
        cutoff_time = current_time - 30
        self.messages = [t for t in self.messages if t > cutoff_time]
        self.mod_messages = [t for t in self.mod_messages if t > cutoff_time]

        # Per channel rate limit (1 message per second for non-mods)
        if not is_mod:
            last_msg_time = self.last_message_time.get(channel, 0)
            if current_time - last_msg_time < 1:
                return False

        # Global rate limits
        if is_mod:
            if len(self.mod_messages) >= 100:  # Mod limit: 100 msgs/30sec
                return False
        elif len(self.messages) >= 20:  # Regular limit: 20 msgs/30sec
            return False

        return True

    def record_message(self, channel: str, is_mod: bool = False):
        """Record that a message was sent."""
        current_time = time.time()
        if is_mod:
            self.mod_messages.append(current_time)
        self.messages.append(current_time)
        self.last_message_time[channel] = current_time

@lru_cache(maxsize=1)
def load_elk_facts() -> List[str]:
    """Load elk facts from the file. Result is cached to avoid repeated disk reads."""
    facts = ["Elk are fascinating creatures!"]  # Default fallback fact
    try:
        with open('elk.elkfacts.txt', 'r') as file:
            loaded_facts = [line.strip() for line in file if line.strip()]
            if loaded_facts:
                facts = loaded_facts
            else:
                logger.error("No facts found in elk.elkfacts.txt")
    except FileNotFoundError:
        logger.error("elk.elkfacts.txt not found")
    except Exception as e:
        logger.error(f"Error reading elk facts file: {str(e)}")
    return facts

class ElkFactBot(commands.Bot):
    def __init__(self, facts: List[str], token_data: Dict[str, str], client_id: str, client_secret: str, channel: str, cache_file: str):
        """Initialize the bot with token data that includes user information."""
        if not token_data.get('login'):
            raise ValueError("Token data must include login information")

        # Initialize with token and login from token data
        super().__init__(
            token=f"oauth:{token_data['access_token']}",
            client_id=client_id,
            nick=token_data['login'],  # Use login from token data
            prefix='!',
            initial_channels=[channel]
        )

        # Store instance variables
        self.facts = facts
        self.fact_count = len(facts)
        self.oauth = TwitchOAuth(
            client_id=client_id,
            client_secret=client_secret,
            cache_file=cache_file
        )
        self._token_data = token_data
        self.rate_limiter = RateLimiter()

    @classmethod
    async def create(cls):
        """Factory method to create a new bot instance asynchronously."""
        try:
            # Load facts once at initialization
            facts = load_elk_facts()
            logger.info(f"Loaded {len(facts)} elk facts")

            # Get environment variables
            client_id = os.environ.get('CLIENT_ID')
            client_secret = os.environ.get('CLIENT_SECRET')
            channel = os.environ.get('CHANNEL')
            cache_file = os.environ.get('TOKEN_CACHE_FILE', '.oauth_cache.json')

            if not all([client_id, client_secret, channel]):
                raise ValueError("Missing required environment variables: CLIENT_ID, CLIENT_SECRET, CHANNEL")

            # Initialize OAuth handler
            oauth = TwitchOAuth(client_id=client_id, client_secret=client_secret, cache_file=cache_file)

            # Try to load cached token
            await oauth._load_cached_token()

            token_data = None
            if oauth._token_data:
                # Verify we have login info
                if oauth._token_data.get('login'):
                    token_data = oauth._token_data
                else:
                    logger.info("Cached token missing login info, will reauthorize")

            # If no valid token, start OAuth flow
            if not token_data:
                token_data = await oauth.get_token()

            if not token_data.get('login'):
                raise ValueError("Failed to get login information from Twitch")

            # Create bot instance
            bot = cls(
                facts=facts,
                token_data=token_data,
                client_id=client_id,
                client_secret=client_secret,
                channel=channel,
                cache_file=cache_file
            )

            logger.info(f"Bot initialized for channel: {channel}")
            return bot
        except Exception as e:
            logger.error(f"Failed to initialize bot: {str(e)}")
            raise

    async def event_ready(self):
        """Called once when the bot is connected."""
        try:
            channels = [channel.name for channel in self.connected_channels]
            logger.info(f'Ready | {self.nick} is online in {", ".join(channels)}')
        except Exception as e:
            logger.error(f"Error in event_ready: {str(e)}")

    async def event_error(self, error: Exception, data: str = None):
        """Called when the bot encounters an error."""
        logger.error(f"Error encountered: {error}")
        if data:
            logger.error(f"Error data: {data}")

        # Check if error is auth-related and try to refresh token
        if "auth" in str(error).lower() or "unauthorized" in str(error).lower():
            try:
                logger.info("Attempting to get new auth token")
                new_token_data = await self.oauth.get_token()  # Get fresh token through OAuth flow
                if not new_token_data.get('login'):
                    raise ValueError("Failed to get user login information from new token")

                # Update bot's token and user info
                self._token_data = new_token_data
                self._connection.token = f"oauth:{new_token_data['access_token']}"
                self.nick = new_token_data['login']
                logger.info("Successfully refreshed auth token")
            except Exception as e:
                logger.error(f"Failed to refresh token: {e}")

    async def event_message(self, message):
        """Runs every time a message is sent in chat."""
        try:
            # Ignore messages from the bot itself
            if message.echo:
                return

            # Handle commands
            await self.handle_commands(message)
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")

    @commands.command(name='help')
    async def help_command(self, ctx: commands.Context):
        """Display help information about available commands."""
        try:
            help_text = "Available commands: " \
                       "► !elkfact - Get a random elk fact | " \
                       "► !elkfacts <number> - Get multiple random elk facts (1-5) | " \
                       "► !help - Show this help message"

            # Check rate limit before sending
            if await self.rate_limiter.can_send_message(ctx.channel.name, ctx.author.is_mod):
                await ctx.send(help_text)
                self.rate_limiter.record_message(ctx.channel.name, ctx.author.is_mod)
                logger.info(f"Sent help info in response to {ctx.author.name}")
            else:
                logger.info(f"Rate limited help command from {ctx.author.name}")

        except Exception as e:
            logger.error(f"Error sending help: {str(e)}")

    @commands.command(name='elkfact')
    async def elk_fact(self, ctx: commands.Context):
        """Send a random elk fact when the command is used."""
        try:
            # Check rate limit before sending
            if await self.rate_limiter.can_send_message(ctx.channel.name, ctx.author.is_mod):
                fact = self.facts[random.randrange(self.fact_count)]
                await ctx.send(f"Did you know? {fact}")
                self.rate_limiter.record_message(ctx.channel.name, ctx.author.is_mod)
                logger.info(f"Sent elk fact in response to {ctx.author.name}")
            else:
                logger.info(f"Rate limited elkfact command from {ctx.author.name}")

        except Exception as e:
            logger.error(f"Error sending elk fact: {str(e)}")

    @commands.command(name='elkfacts')
    async def elk_facts(self, ctx: commands.Context, num_facts: str = "1"):
        """Send multiple random elk facts when the command is used."""
        try:
            # Convert input to integer and validate
            count = int(num_facts)
            if count < 1 or count > 5:
                if await self.rate_limiter.can_send_message(ctx.channel.name, ctx.author.is_mod):
                    await ctx.send("Please request between 1 and 5 facts!")
                    self.rate_limiter.record_message(ctx.channel.name, ctx.author.is_mod)
                return

            # Get random facts (avoiding duplicates)
            selected_facts = random.sample(self.facts, min(count, self.fact_count))

            # Send each fact with rate limiting
            facts_sent = 0
            for i, fact in enumerate(selected_facts, 1):
                if await self.rate_limiter.can_send_message(ctx.channel.name, ctx.author.is_mod):
                    await ctx.send(f"Fact #{i}: {fact}")
                    self.rate_limiter.record_message(ctx.channel.name, ctx.author.is_mod)
                    facts_sent += 1
                    if i < len(selected_facts):  # Don't delay after the last fact
                        await asyncio.sleep(1.1)  # Ensure we respect the 1 message per second rule
                else:
                    logger.info(f"Rate limited elkfacts command from {ctx.author.name} after {facts_sent} facts")
                    break

            logger.info(f"Sent {facts_sent} elk facts in response to {ctx.author.name}")
        except ValueError:
            if await self.rate_limiter.can_send_message(ctx.channel.name, ctx.author.is_mod):
                await ctx.send("Please provide a valid number between 1 and 5!")
                self.rate_limiter.record_message(ctx.channel.name, ctx.author.is_mod)
        except Exception as e:
            logger.error(f"Error sending elk facts: {str(e)}")

async def main():
    """Main entry point for the bot."""
    try:
        bot = await ElkFactBot.create()
        await bot.start()
    except Exception as e:
        logger.critical(f"Critical error running bot: {str(e)}")
        raise  # Re-raise to see full traceback

if __name__ == "__main__":
    asyncio.run(main())
