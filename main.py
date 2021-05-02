import os
import logging
import discord
from TimeCommand import TimeCommands
from CobraCommand import CobraCommands
from keep_alive import keep_alive

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('cobra_bot')

# Get Discord Bot token from env variables. 
cobratoken = os.environ['cobra.token']

# Setup Bot
bot = discord.ext.commands.Bot(
    command_prefix="!",
    description=
    "Cobra Bot is an Netrunner Tournament Bot")

# On startup, log all servers you are connected to. 
@bot.event
async def on_ready():
    logger.log(logging.INFO,
               "Hello! My name is {0.user} and I am ready!".format(bot))

    for guild in bot.guilds:
        logger.log(logging.INFO, guild.name)
        logger.log(logging.INFO, guild.owner)

# Add support for !time commands
bot.add_cog(TimeCommands(bot))
bot.add_cog(CobraCommands(bot))

# Startup Web Server in separate thread, to keep alive bot in case there is no traffic in channels.
keep_alive()  

# Startup Bot. 
bot.run(cobratoken)
