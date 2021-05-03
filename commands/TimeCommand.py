import logging
import asyncio
import time as clock
from discord.ext import commands


# This class supports all !time commands
class TimeCommand(commands.Cog, name="Time - Helps you manage Round time using Cobra BOT"):
    """
    Manage Netrunner Tournament Round time using Discord bot !time command  
    """
    logger = logging.getLogger("TimeCommand")

    """
    Construct Command class and setup default values. 
    Default round time 65 minutes. 
    """
    def __init__(self, bot):
        self.bot = bot

        # Start of the round in seconds since the start of time
        self._round_start = 0

        # Lenght of the round in seconds
        self._round_time = 65 * 60

        # Used to stop the round
        self._stop = False

    @staticmethod
    def formatTime(seconds):
        """
        Returns formated string based on numer of minutes and seconds left. 
        ex. 
        2 minutes 1 seconds
        2 minutes
        1 minute 5 seconds
        1 minute 
        5 seconds
        """
        min = int(seconds / 60)
        sec = int(seconds % 60)

        if min == 1:
          minutes = "1 minute "
        elif min > 1: 
          minutes = "{:d} minutes ".format(min)
        else: 
          minutes = ""

        if sec == 1:
          seconds = "1 second"
        elif sec > 1:
          seconds = "{:d} seconds".format(sec)
        else:
          seconds = ""

        return (minutes+seconds).strip()

    @commands.group(pass_context=True)
    async def time(self, ctx):
        """
        start|stop|show|set X - A set of commands to Start/Stop/Show/Set round timer.  
        """
        pass

    # Bot command: !time_set X
    # Set the timer for the round.
    # Minium time 5 minutes.
    # Maximum time 120 minutes.
    @time.command(name="set")
    async def set(self, ctx, minutes: int):
        """sets the timer for new round accoring to paramter X (in minutes) """
        self.logger.log(logging.DEBUG, ctx.command)

        if minutes < 5:
            await ctx.send("Nope! Minium round time is 5 minutes.")
        elif minutes > 120:
            await ctx.send("Nope! Maximum round time is 120 minutes.")
        else:
            self._round_time = minutes * 60
            await ctx.send("Round time set to {}. To start the round use !time start.".format(
                self.formatTime(self._round_time)))

    # Bot command: !time_start
    # Start the timer with time set up up using !time_set command
    @time.command(name="start")
    async def start(self, ctx):
        """- Starts the round timer."""
        self.logger.log(logging.DEBUG, ctx.command)

        if self._round_start > 0:
            await ctx.send(
                "If you want to start the rund. Please stop the current round first."
            )
            return

        self._round_start = clock.time()
        round_end = self._round_start + self._round_time

        # confim on channel that time was started.
        await ctx.send("Ok! Time started {}".format(
            self.formatTime(self._round_time)))

        # loop sleep untill finished or break
        while clock.time() < round_end - 6:
            if (self._stop):
                await ctx.send("Round finished.")
                self._stop = False
                self._round_start = 0
                return
            await asyncio.sleep(1)

        ## Countdown from 5 seconds.

        for x in [5, 4, 3, 2, 1]:
            await ctx.send("Only {} left!".format(self.formatTime(x)))
            await asyncio.sleep(1)

        self._round_start = 0
        ## Finish round
        await ctx.send("""@here Time's up !!! Round ends. 
Current player finishes his/her round and then opponent does the same.""")

        self.logger.log(logging.INFO, "Time Stop")

    # Bot command: !time_show
    # Bots replies with minutes and seconds untill end of the round.
    @time.command(name="show")
    async def show(self, ctx):
        """- Bots replies with minutes and seconds untill end of the round."""
        self.logger.log(logging.DEBUG, ctx.command)
        
        if self._round_start == 0:
            await ctx.send(
                "To show time - start the round first."
            )
            return             

        time_left = self._round_time + self._round_start - clock.time()
        await ctx.send("Time left {}".format(self.formatTime(time_left)))


    @time.command(name="stop")
    async def stop(self, ctx):
        """ - Stops the timer."""
        self.logger.log(logging.DEBUG, ctx.command)

        if self._round_start == 0:
            await ctx.send(
                "To stop round - start the round first."
            )
            return        

        self._stop = True
