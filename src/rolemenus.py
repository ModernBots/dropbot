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

	@commands.slash_command()
	async def role_menu(inter: disnake.ApplicationCommandInteraction, title: str, initial_role: disnake.Role, initial_role_emoji: disnake.Emoji = None, initial_role_description: str = None, description: str = None):
		"""Make a role menu, use /add_role_to_menu to add more roles

		Parameters
		----------
		title: str
			The title of the role menu
		initial_role: disnake.Role
			The role to start the menu with, more can be added with /add_role_to_menu
		initial_role_emoji: disnake.Emoji
			The emoji to use for the initial role
		initial_role_description: str
			The description of the initial role
		description: str
			The description of the role menu
		"""
		pass

	@commands.slash_command(description="Adds a role to a role menu.")
	async def add_role_to_menu(inter: disnake.ApplicationCommandInteraction, title: str, role: disnake.Role, emoji: disnake.Emoji = None, description: str = None):
		"""Adds a role to a role menu

		Parameters
		----------
		title: str
			The title of the role menu
		role: disnake.Role
			The role to add to the menu
		emoji: disnake.Emoji
			The emoji to use for the role
		description: str
			The description of the role menu
		"""
		pass

	@commands.slash_command(description="Removes a role to a role menu.")
	async def remove_role_from_menu(inter: disnake.ApplicationCommandInteraction, message_id: int, position: int = commands.Param(ge=1, le=25)):
		"""Removes a role from a role menu

		Parameters
		----------
		title: str
			The title of the role menu
		role: disnake.Role
			The role to remove from the menu
		"""
		pass


def setup(bot):
	bot.add_cog(RoleMenusCog(bot))
