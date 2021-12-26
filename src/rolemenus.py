import disnake
import pymongo
from disnake.ext import commands

mongoclient = pymongo.MongoClient()
db = mongoclient.modernbot
guild_preferences = db.guild_preferences
role_menus = db.role_menus


class RoleMenusCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	def create_role_menu(guild_id: int, channel_id: int, message_id: int, roles: list):
		data = {
			"guild_id": guild_id,
			"channel_id": channel_id,
			"message_id": message_id,
			"roles": roles
		}
		if role_menus.find_one({"message_id": message_id}) != None:
			return False
		role_menus.insert_one(data)
		return True

	def has_role_permissions():
		pass

	@commands.slash_command(description="Make a role menu. Use /add_role_to_menu to add more roles.")
	async def role_menu(inter: disnake.ApplicationCommandInteraction, title: str, description: str = None):
		pass

	@commands.slash_command(description="Adds a role to a role menu.")
	async def add_role_to_menu(inter: disnake.ApplicationCommandInteraction, message_id: int, role: disnake.Role, emoji: disnake.Emoji = None):
		pass

	@commands.slash_command(description="Removes a role to a role menu.")
	async def remove_role_from_menu(inter: disnake.ApplicationCommandInteraction, message_id: int, position: int = commands.Param(ge=1, le=25)):
		pass

	@commands.slash_command(description="Makes a role button message.")
	async def role_button(
		inter: disnake.ApplicationCommandInteraction,
		role: disnake.Role,
		message_title: str,
		button_color: str = commands.Param(
			choices=["Blurple", "Gray", "Green", "Red"]),
		message_description: str = None,
		button_emoji: disnake.Emoji = None):
		pass


def setup(bot):
	bot.add_cog(RoleMenusCog(bot))
