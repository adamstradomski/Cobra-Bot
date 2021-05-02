import logging
import asyncio
import time as clock
from discord.ext import commands

class CobraCommands(commands.Cog, name="Cobr.AI Integration - WORK IN PROGRESS"):
    """
    Integrate your Discord channel with cobr.ai Netrunner Tournament using Discord bot !cobra command
    """
    logger = logging.getLogger("CobraCommands")

    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    async def cobra(self, ctx):
        """
        standings|parings - NOT YET IMPLEMENTED
        """
        pass

