import logging
import requests
from discord.ext import commands
from discord import Embed, Colour

COBRA_URL = "http://cobr.ai/tournaments/"


class CobraCommand(commands.Cog,
                   name="Cobr.AI Integration"):
    """
    Integrate your Discord channel with cobr.ai Netrunner Tournament using Discord bot !cobra command
    """
    logger = logging.getLogger("CobraCommand")

    def __init__(self, bot):
        self.bot = bot

    # Dictionary GuildID.ChannelID.TournamentID
    guilds = {}

    def getTournamentId(self, ctx):
        return self.guilds[ctx.guild.id][ctx.channel.id]["tournamentID"]

    def requireTournamentId(func):
        """
        Decorator that verifies if tournament ID was set on the channel and notifies users if not. 
        Works with bot.command methods. Requires attributes (CobraCommand, ctx) 
        """
        async def wrapper(*args, **kwargs):
            self = args[0]
            ctx = args[1]

            if self.guilds.get(ctx.guild.id) and self.guilds.get(
                    ctx.guild.id).get(ctx.channel.id) and self.guilds.get(
                        ctx.guild.id).get(ctx.channel.id).get("tournamentID"):
                await func(*args, **kwargs)
            else:
                await ctx.send(
                    "Before using other commands, please set Tournament ID using !cobra set"
                )

        return wrapper

    @commands.group(pass_context=True)
    async def cobra(self, ctx):
        """
        set|show|standings|pairings|stats
        """
        pass

    @cobra.command(name="set")
    async def set(self, ctx, id: str):
        """Set the tournament ID by either copy-past tournament URL (eg. http://cobr.ai/tournaments/2029) or the tournament ID for cobr.ai (eg. 2029) """

        # extract tournament id from URL: http://cobr.ai/tournaments/2029 -> 2029
        id = id.strip().split("/")[-1]
        if id.isnumeric():
            self.guilds[ctx.guild.id] = {}
            self.guilds[ctx.guild.id][ctx.channel.id] = {}
            self.guilds[ctx.guild.id][ctx.channel.id]["tournamentID"] = id
            self.guilds[ctx.guild.id][ctx.channel.id]["players"] = {}
            await ctx.send("Tournament ID set to {}".format(id))
        else:
            await ctx.send("""Wrong tournament id format. Example use:
!cobra set 2029
!cobra set http://cobr.ai/tournaments/2029
          """)

    @cobra.command(name="show", description="Show basic tournament information")
    @requireTournamentId
    async def show(self, ctx):
        """Show the tournament infomation"""
        data = requests.get(COBRA_URL + self.getTournamentId(ctx) +".json").json()
        embed = Embed()
        embed.title = data.get("name")
        embed.url = COBRA_URL + self.getTournamentId(ctx)
        embed.color=Colour.dark_green()
        embed.add_field(name="Organizer", value=data.get("tournamentOrganiser").get("nrdbUsername"), inline=True)
        embed.add_field(name="Players", value=len(data.get("players")), inline=True)
        embed.add_field(name="Rounds", value=data.get("preliminaryRounds"), inline=True)

        await ctx.send(embed=embed)

    @cobra.command(name="standings")
    @requireTournamentId
    async def standings(self, ctx):
        """Show the current tournament standings. """
        data = requests.get(COBRA_URL + self.getTournamentId(ctx) +".json").json()
        ranks,names,mps="","",""

        for player in data.get("players"): 
          self.logger.log(logging.DEBUG, player)

          ranks = ranks + str(player["rank"]) + "\n"
          names = names + str(player["name"]) + "\n"
          mps = mps + str(player["matchPoints"]) + "\n"

        embed = Embed()
        embed.title = data.get("name")
        embed.description = "Standings round " + str(len(data.get("rounds")))
        embed.url = COBRA_URL + self.getTournamentId(ctx)
        embed.color=Colour.red()
        embed.add_field(name="Rank", value=ranks, inline=True)
        embed.add_field(name="Name", value=names, inline=True)
        embed.add_field(name="Points", value=mps, inline=True)  
        await ctx.send(embed=embed)

    @cobra.command(name="pairings")
    @requireTournamentId
    async def pairings(self, ctx):
        """Show the current tournament pairing. """
        data = requests.get(COBRA_URL + self.getTournamentId(ctx) +".json").json()

        # Create Map PlayerID:PlayerName        
        for player in data.get("players"):
            self.guilds[ctx.guild.id][ctx.channel.id]["players"].update({player.get("id"): player.get("name")}) 
        
        self.logger.log(logging.DEBUG, self.guilds[ctx.guild.id][ctx.channel.id]["players"])

        tables,player1,player2="","",""

        # Loop over last round
        for pair in data.get("rounds")[-1]: 
          self.logger.log(logging.DEBUG, pair)
          p1 = pair.get("player1").get("id")
          p2 = pair.get("player2").get("id")
          tables = tables + str(pair.get("table")) + "\n"
          player1 = player1 + self.guilds[ctx.guild.id][ctx.channel.id]["players"][p1] + "\n"
          player2 = player2 + self.guilds[ctx.guild.id][ctx.channel.id]["players"][p2] + "\n"

        embed = Embed()
        embed.title = data.get("name")
        embed.description = "Pairings round " + str(len(data.get("rounds")))
        embed.url = COBRA_URL + self.getTournamentId(ctx)
        embed.color=Colour.dark_orange()
        embed.add_field(name="Table", value=tables, inline=True)
        embed.add_field(name="Player 1", value=player1, inline=True)
        embed.add_field(name="Player 2", value=player2, inline=True)  
        await ctx.send(embed=embed)

    @cobra.command(name="stats")
    @requireTournamentId
    async def stats(self, ctx):
        """Show the current tournament Corp and Runner ID statistics. """
        data = requests.get(COBRA_URL + self.getTournamentId(ctx) +".json").json()

        cids = {}
        rids = {}
        # Create Map PlayerID:PlayerName        
        for player in data.get("players"):
          cid = cids.get(player.get("corpIdentity"))
          if not cid: 
            cid = 0
          cids.update({player.get("corpIdentity"): cid + 1})
          
          rid = rids.get(player.get("runnerIdentity"))
          if not rid: 
            rid = 0          
          rids.update({player.get("runnerIdentity"): rid + 1})

        corp,runner,ccount,rcount="","","",""
        for id in cids:
          corp = corp + id + "\n"
          ccount = ccount + str(cids[id]) + "\n"

        for id in rids:
          runner = runner + id + "\n"
          rcount = rcount + str(rids[id]) + "\n"

        embed = Embed()
        embed.title = data.get("name")
        embed.description = "Statistics"
        embed.url = COBRA_URL + self.getTournamentId(ctx)
        embed.color=Colour.dark_magenta()
        embed.add_field(name="Corp IDs", value=corp, inline=True)
        embed.add_field(name="No", value=ccount, inline=True)
        embed.add_field(name="\u200B", value="\u200B", inline=False)
        embed.add_field(name="Runnder IDs", value=runner, inline=True)
        embed.add_field(name="N0", value=rcount, inline=True)
        await ctx.send(embed=embed)
