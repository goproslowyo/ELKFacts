import os
import random
from dotenv import load_dotenv
from twitchio.ext import commands
import logging
from functools import lru_cache
from typing import List

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

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
    def __init__(self):
        try:
            # Load facts once at initialization
            self.facts = load_elk_facts()
            self.fact_count = len(self.facts)
            logger.info(f"Loaded {self.fact_count} elk facts")
            
            # Initialize bot configuration
            token = os.environ.get('TMI_TOKEN')
            client_id = os.environ.get('CLIENT_ID')
            nick = os.environ.get('BOT_NICK')
            channel = os.environ.get('CHANNEL')
            
            if not all([token, client_id, nick, channel]):
                raise ValueError("Missing required environment variables")
            
            super().__init__(
                token=token,
                client_id=client_id,
                nick=nick,
                prefix='!',
                initial_channels=[channel]
            )
            logger.info(f"Bot initialized for channel: {channel}")
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

    @commands.command(name='elkfact')
    async def elk_fact(self, ctx: commands.Context):
        """Send a random elk fact when the command is used."""
        try:
            # Use randrange for more efficient random selection
            fact = self.facts[random.randrange(self.fact_count)]
            await ctx.send(f"Did you know? {fact}")
            logger.info(f"Sent elk fact in response to {ctx.author.name}")
        except Exception as e:
            logger.error(f"Error sending elk fact: {str(e)}")
            await ctx.send("Sorry, I couldn't retrieve an elk fact right now!")

def main():
    try:
        bot = ElkFactBot()
        bot.run()
    except Exception as e:
        logger.critical(f"Critical error running bot: {str(e)}")

if __name__ == "__main__":
    main()