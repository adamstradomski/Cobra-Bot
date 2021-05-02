import logging
import asyncio
import time as clock
from discord.ext import commands


# This class supports all !time commands
class CobraCommands(commands.Cog, name="Cobr.AI Integration - WORK IN PROGRESS"):
    pass

    logger = logging.getLogger("CobraCommands")

    def __init__(self, bot):
        self.bot = bot

        # Start of the round in seconds since the start of time
        self._round_start = 0

        # Lenght of the round in seconds
        self._round_time = 0

        # Used to stop the round
        self._stop = False


    @commands.group(pass_context=True)
    async def cobra(self, ctx):
        """
        standings|parings - NOT YET IMPLEMENTED
        """
        pass

