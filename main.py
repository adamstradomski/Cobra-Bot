
import os
import logging
import discord
from commands.TimeCommand import TimeCommand
from commands.CobraCommand import CobraCommand
from commands.RoleCommand import RoleCommand
from keep_alive import keep_alive
from config import CONFIG

# Setup logging
logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s %(levelname)s %(name)s: %(message)s',
  datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('cobra_bot')

# Setup Bot
intents = discord.Intents.default()
intents.members = True # required for reaction events to work
bot = discord.ext.commands.Bot(
    command_prefix="!",
    intents=intents,
    description=
    "Cobra Bot is a Discord Bot that helps you run Netrunner Tournaments using Discord!"
)


# On startup, log all servers you are connected to.
@bot.event
async def on_ready():
    logger.log(logging.INFO,
               "Hello! My name is {0.user} and I am ready!".format(bot))

    for guild in bot.guilds:
        logger.log(logging.INFO, guild.name)


# Add support for !time commands
bot.add_cog(TimeCommand(bot))

# Add support for !cobra commands
bot.add_cog(CobraCommand(bot))

# Add support for role management commands
if (CONFIG.ROLE_MANAGEMENT_ENABLED):
  bot.add_cog(RoleCommand(bot))

if __name__ == "__main__":
  # This is for replit.com 
  # Startup Web Server in separate thread, to keep alive bot.
  # You still need to have a WebServer to be pinged externally. Check out  https://uptimerobot.com/
  keep_alive()

  # Create your Bot and get token from https://discord.com/developers/
  # Get Token from environment variables
  # Startup Bot
  bot.run(os.environ['discord_bot_token'])
