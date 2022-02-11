from typing import Final
from discord import PartialEmoji

class Config(object):
  # Object immutability, so we don't edit config in runtime by accident
  __slots__ = ()

  # Whether to use the RoleCommand. There are thousands of other discord bots managing roles, so pretty often this functionality will be covered without the use of Cobra bot
  ROLE_MANAGEMENT_ENABLED = True

  # List of channel IDs to watch for reactions
  ROLE_CHANNELS = [123456789]

  # Emoji-to-role mapping
  EMOJI_TO_ROLE = {
    PartialEmoji(name='🚀'): 123456789, # :rocket: on Discord
    PartialEmoji(name='🦾'): 123456789, # :mechanical_arm: on Discord
    PartialEmoji(name='🔍'): 123456789, # :mag: on Discord
  }

CONFIG: Final = Config()