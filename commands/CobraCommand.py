import logging
import requests
from discord.ext import commands
from discord import Embed, Colour

COBRA_URL = "http://cobr.ai/tournaments/"


class CobraCommand(commands.Cog, name="Cobr.AI Integration"):
    """
    Integrate your Discord channel with cobr.ai Netrunner Tournament using Discord bot !cobra command
    """
    logger = logging.getLogger("CobraCommand")

    def __init__(self, bot):
        self.bot = bot

    # Dictionary GuildID.ChannelID.TournamentID
    guilds = {}

    def getTournamentId(self, ctx):
        """ Get current tournament ID provided by SET command.  """
        return self.guilds[ctx.guild.id][ctx.channel.id]["tournamentID"]

    def getTournament(self, ctx):
        """ Connect to Cobra.AI and get tournament current information. """
        try:
            return requests.get(COBRA_URL + self.getTournamentId(ctx) +
                                ".json").json()
        except Exception:
            return None

    async def cog_check(self, ctx):
        """ Verify if the tournametn ID was set, before using any of commands. Expect set command."""
        if ctx.invoked_with == "set" or ctx.invoked_with == "cobra" or ctx.invoked_with == "help":
            return True  # !set, !cobra - can be invoked always

        # Require tournamentID for all other commands
        if self.guilds.get(ctx.guild.id) and self.guilds.get(ctx.guild.id).get(
                ctx.channel.id) and self.guilds.get(ctx.guild.id).get(
                    ctx.channel.id).get("tournamentID"):
            return True
        else:
            await ctx.send(
                "Before using other commands, please set Tournament ID using !cobra set"
            )
            return False

    @commands.group(pass_context=True, invoke_without_command=True)
    async def cobra(self, ctx):
        """ set {ID} | set http://cobr.ai/tournaments/{ID} | show | standings | pairings | pairings {ROUND} | stats - !help cobra for more info"""
        await ctx.send("!help cobra for more info")

    @cobra.command(name="set")
    async def set(self, ctx, id: str):
        """Sets the tournament id
         by either copy-past tournament URL (eg. http://cobr.ai/tournaments/2029) or the tournament ID for cobr.ai (eg. 2029) """

        # extract tournament id from URL: http://cobr.ai/tournaments/2029 -> 2029
        id = id.strip().split("/")[-1]
        if id.isnumeric():
            if not self.guilds.get(ctx.guild.id):
                self.guilds[ctx.guild.id] = {}
            self.guilds[ctx.guild.id][ctx.channel.id] = {}
            self.guilds[ctx.guild.id][ctx.channel.id]["tournamentID"] = id

            data = self.getTournament(ctx)
            if data:
                await ctx.send("Set current tournament to '{}'".format(
                    data.get("name")))
            else:
                self.guilds[ctx.guild.id][
                    ctx.channel.id]["tournamentID"] = None
                await ctx.send("Tournament Not found: {}{}".format(
                    COBRA_URL, id))
        else:
            await ctx.send(
                """Wrong tournament id format. Example use:\n!cobra set 2029\n!cobra set http://cobr.ai/tournaments/2029"""
            )

    @cobra.command(name="show",
                   description="Show basic tournament information")
    async def show(self, ctx):
        """Show basic tournament infomation"""
        data = self.getTournament(ctx)

        embed = Embed()
        embed.title = data.get("name")
        embed.url = COBRA_URL + self.getTournamentId(ctx)
        embed.color = Colour.dark_green()
        embed.add_field(
            name="Organizer",
            value=data.get("tournamentOrganiser").get("nrdbUsername"),
            inline=True)
        embed.add_field(name="Players",
                        value=len(data.get("players")),
                        inline=True)
        embed.add_field(name="Rounds",
                        value=data.get("preliminaryRounds"),
                        inline=True)

        await ctx.send(embed=embed)

    @cobra.command(name="standings")
    async def standings(self, ctx):
        """Show tournament current standings. """
        data = self.getTournament(ctx)
        ranks, names, mps = "", "", ""

        for player in data.get("players"):
            self.logger.log(logging.DEBUG, player)

            ranks = ranks + str(player["rank"]) + "\n"
            names = names + str(player["name"]) + "\n"
            mps = mps + str(player["matchPoints"]) + "\n"

        embed = Embed()
        embed.title = data.get("name")
        embed.description = "Standings round " + str(len(data.get("rounds")))
        embed.url = COBRA_URL + self.getTournamentId(ctx)
        embed.color = Colour.red()
        embed.add_field(name="Rank", value=ranks, inline=True)
        embed.add_field(name="Name", value=names, inline=True)
        embed.add_field(name="Points", value=mps, inline=True)
        await ctx.send(embed=embed)

    @cobra.command(name="pairings")
    async def pairingsRound(self, ctx, round: int = -1):
        """Show tournament current pairings. Use !cobra pairings {ROUND} to get pairings for specific round. """
        data = self.getTournament(ctx)

        # Create Dictionary PlayerID:PlayerName for pairings
        players = {None: "Bye"}  # Null players are Bye
        for player in data.get("players"):
            players.update({player.get("id"): player.get("name")})

        if round < 0: 
          round = len(data.get("rounds")) - 1
        else: 
          round -= 1

        tables, player1, player2 = "", "", ""

        # Loop over each pair in round
        for pair in data.get("rounds")[round]:
            self.logger.log(logging.DEBUG, pair)

            p1 = pair.get("player1").get("id")
            p2 = pair.get("player2").get("id")

            tables = tables + str(pair.get("table")) + "\n"
            player1 += players[p1] + "\n"
            player2 += players[p2] + "\n"

        embed = Embed()
        embed.title = data.get("name")
        embed.description = "Pairings for round " + str(round + 1)
        embed.url = COBRA_URL + self.getTournamentId(ctx)
        embed.color = Colour.dark_orange()
        embed.add_field(name="Table", value=tables, inline=True)
        embed.add_field(name="Player 1", value=player1, inline=True)
        embed.add_field(name="Player 2", value=player2, inline=True)
        await ctx.send(embed=embed)

    @cobra.command(name="stats")
    async def stats(self, ctx):
        """Show the tournament Corp ID and Runner ID statistics. """
        data = self.getTournament(ctx)

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

        corp, runner, ccount, rcount = "", "", "", ""
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
        embed.color = Colour.dark_magenta()
        embed.add_field(name="Corp IDs", value=corp, inline=True)
        embed.add_field(name="No", value=ccount, inline=True)
        embed.add_field(name="\u200B", value="\u200B", inline=False)
        embed.add_field(name="Runnder IDs", value=runner, inline=True)
        embed.add_field(name="N0", value=rcount, inline=True)
        await ctx.send(embed=embed)
