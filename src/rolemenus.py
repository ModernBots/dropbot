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

	# `roles` structure:
	# {
	# 	"role_id": [user_id, ...], ...
	# }

	def create_role_menu(
		self,
		guild_id: int,
		author_id: int,
		author_name: str,
		author_avatar: str,
		title: str,
		description: str,
		roles: dict, # see above comment for structure
		min_choices: int,
		max_choices: int):
		data = {
			"guild_id": guild_id,
			"author_id": author_id,
			"author_name": author_name,
			"author_avatar": author_avatar,
			"title": title,
			"description": description,
			"roles": roles,
			"min_choices": min_choices,
			"max_choices": max_choices
		}
		return polls.insert_one(data).inserted_id

	def get_role_menu(post_id):
		return polls.find_one({"_id": ObjectId(post_id)})

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
