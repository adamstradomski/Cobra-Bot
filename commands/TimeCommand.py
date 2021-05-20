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
        self.guilds = {} 
        # Dictionary GuildID.ChannelID.Start
        # Dictionary GuildID.ChannelID.Time
        # Dictionary GuildID.ChannelID.Stop

    def getRound(self, ctx):
        """ Get Round object for Guid and Channel """
        if not self.guilds.get(ctx.guild.id):
            self.guilds[ctx.guild.id] = {}

        if not  self.guilds.get(ctx.guild.id).get(ctx.channel.id):
            self.guilds[ctx.guild.id][ctx.channel.id] = {}

        return self.guilds[ctx.guild.id][ctx.channel.id]

    def getRoundTime(self, ctx) -> int:
        """ Get Round object for Guid and Channel. Default 65 minutes """
        return self.getRound(ctx).get("Time") or 65*60

    def getRoundStart(self, ctx) -> int:
        """ Get Round object for Guid and Channel. Default 0 """
        return self.getRound(ctx).get("Start") or 0

    def getRoundStop(self, ctx) -> bool:
        """ Get Round object for Guid and Channel """
        return self.getRound(ctx).get("Stop")

    def updateRoundStop(self, ctx, val):
        """ Get Round object for Guid and Channel """
        return self.getRound(ctx).update({"Stop":val}) 

    def updateRoundTime(self, ctx, val):
        """ Get Round object for Guid and Channel """
        return self.getRound(ctx).update({"Time":val}) 

    def updateRoundStart(self, ctx, val):
        """ Get Round object for Guid and Channel """
        return self.getRound(ctx).update({"Start":val})                 

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
        """start|stop|show|set {time_in_minutes}
        A set of commands to Start/Stop/Show/Set round timer.  
        """
        pass

    # Bot command: !time_set X
    # Set the timer for the round.
    # Minium time 5 minutes.
    # Maximum time 120 minutes.
    @time.command(name="set")
    async def set(self, ctx, minutes: int):
        """- Set the timer for new round accoring to paramter X (in minutes)"""
        self.logger.log(logging.DEBUG, ctx.command)

        if minutes < 5:
            await ctx.send("Nope! Minium round time is 5 minutes.")
        elif minutes > 120:
            await ctx.send("Nope! Maximum round time is 120 minutes.")
        else:
            self.getRound(ctx).update({"Time": minutes * 60})
            await ctx.send("Round time set to {}. To start the round use !time start.".format(
                self.formatTime(self.getRound(ctx).get("Time"))))

    # Bot command: !time_start
    # Start the timer with time set up up using !time_set command
    @time.command(name="start")
    async def start(self, ctx):
        """- Start the round timer."""
        self.logger.log(logging.DEBUG, ctx.command)

        if self.getRoundStart(ctx) > 0:
            await ctx.send(
                "If you want to start the rund. Please stop the current round first."
            )
            return

        self.updateRoundStart(ctx, clock.time())
        round_end = self.getRoundStart(ctx) + self.getRoundTime(ctx)

        # confim on channel that time was started.
        await ctx.send("Ok! Time started {}".format(
            self.formatTime(self.getRoundTime(ctx))))

        # loop sleep untill finished or break
        while clock.time() < round_end - 6:
            if (self.getRoundStop(ctx)):
                await ctx.send("Round finished.")
                self.updateRoundStop(ctx,False)
                self.updateRoundStart(ctx,0)
                return
            await asyncio.sleep(1)

        ## Countdown from 5 seconds.

        for x in [5, 4, 3, 2, 1]:
            await ctx.send("Only {} left!".format(self.formatTime(x)))
            await asyncio.sleep(1)

        self.updateRoundStart(ctx,0)
        ## Finish round
        await ctx.send("""@here Time's up !!! Round ends. 
Current player finishes his/her round and then opponent does the same.""")

        self.logger.log(logging.INFO, "Time Stop")

    @time.command(name="show")
    async def show(self, ctx):
        """- Show minutes and seconds until end of the round."""
        self.logger.log(logging.DEBUG, ctx.command)
        
        if self.getRoundStart(ctx) == 0:
            await ctx.send(
                "To show time - start the round first."
            )
            return             

        time_left = self.getRoundTime(ctx) + self.getRoundStart(ctx) - clock.time()
        await ctx.send("Time left {}".format(self.formatTime(time_left)))


    @time.command(name="stop")
    async def stop(self, ctx):
        """ - Stop the round timer."""
        self.logger.log(logging.DEBUG, ctx.command)

        if self.getRoundStart(ctx) == 0:
            await ctx.send(
                "To stop round - start the round first."
            )
            return        

        self.updateRoundStop(ctx, True)
