import logging
from discord import RawReactionActionEvent
from discord.ext import commands
from config import CONFIG

class RoleCommand(commands.Cog, name="Manage server roles"):
    """
    Add or remove roles from users based on their reaction in a specified channel.
    """
    logger = logging.getLogger("RoleCommand")

    def __init__(self, bot):
        self.bot = bot
        self.guilds = {} # Dictionary GuildID.ChannelID.TournamentID

    def validate_reaction_payload(self, payload: RawReactionActionEvent):
      """
      Perform validation checks on reaction event payload to make sure it's addressed to the right channel and correctly maps to an existing role.

      :param payload: a RawReactionActionEvent payload to verify
      :return: None if verification failed, dictionary containing role and member the reaction maps to otherwise"""
      # ignore messages in non-watched channels
      if payload.channel_id not in CONFIG.ROLE_CHANNELS:
        return

      # check if we're in the guild the payload came from
      guild = self.bot.get_guild(payload.guild_id)
      if guild is None:
        self.logger.error(f"Received payload from wrong guild {payload.guild_id} (is the bot still a member of this guild?)")
        return

      # map emoji to role
      try:
        role_id = CONFIG.EMOJI_TO_ROLE[payload.emoji]
      except KeyError:
        self.logger.warning(f"Unknown emoji {payload.emoji} reaction received in watched channel {payload.channel_id}")
        return

      role = guild.get_role(role_id)
      if role is None:
        self.logger.error(f"Couldn't find role with ID {role_id} in guild {payload.guild_id}")
        return

      member = guild.get_member(payload.user_id)
      if member is None:
        self.logger.error(f"Couldn't find member with user ID {payload.user_id} in guild {payload.guild_id}")
        return

      return {"role": role, "member": member}

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
      role_change = self.validate_reaction_payload(payload)
      if role_change is None:
        return

      try:
        await role_change["member"].add_roles(role_change["role"])
        self.logger.info(f"Added role {role_change['role']} to user {role_change['member']}.")
      except Exception:
        self.logger.exception(f"A problem occured when adding role based on payload {payload}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
      role_change = self.validate_reaction_payload(payload)
      if role_change is None:
        return

      try:
        await role_change["member"].remove_roles(role_change["role"])
        self.logger.info(f"Removed role {role_change['role']} from user {role_change['member']}.")
      except Exception:
        self.logger.exception(f"A problem occured when removing role based on payload {payload}")
