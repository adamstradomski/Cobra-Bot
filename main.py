import os
import logging
import discord
from commands.TimeCommand import TimeCommand
from commands.CobraCommand import CobraCommand
from keep_alive import keep_alive

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('cobra_bot')

# Setup Bot
bot = discord.ext.commands.Bot(
    command_prefix="!",
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

if __name__ == "__main__":
  # This is for replit.com 
  # Startup Web Server in separate thread, to keep alive bot.
  # You still need to have a WebServer to be pinged externally. Check out  https://uptimerobot.com/
  keep_alive()

  # Create your Bot and get token from https://discord.com/developers/
  # Get Token from environment variables
  # Startup Bot
  bot.run(os.environ['discord_bot_token'])
