import disnake
from disnake.ext import commands
from motor import motor_asyncio

mongoclient = motor_asyncio.AsyncIOMotorClient()
db = mongoclient.modernbot
guild_preferences = db.guild_preferences
role_menus = db.role_menus


class RoleMenusCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	# `roles` structure:
	# {
	# 	"role_id": {
	# 		"name": "role name",
	# 		"who": [user_id, ...],
	# 	} ...
	# }
	#
	# Ex.
	# for i in roles:
	# 	print(i)				# Role ID
	#	print(roles[i]) 		# All role data
	# 	for j in roles[i]:
	# 		print(j) 			# Key (first iter: name, second iter: who)
	# 		print(roles[i][j]) 	# Value (first iter: the role name, second iter: who chose it)

	async def create_role_menu(
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
			"message_id": None,
			"author_id": author_id,
			"author_name": author_name,
			"author_avatar": author_avatar,
			"title": title,
			"description": description,
			"roles": roles,
			"min_choices": min_choices,
			"max_choices": max_choices
		}
		return (await role_menus.insert_one(data)).inserted_id

	async def get_role_menu(post_id):
		return await polls.find_one({"_id": ObjectId(post_id)})

	class Menu(disnake.ui.View):
		def __init__(self, embeds, dropdowns):
			super().__init__()
			self.embeds = embeds
			self.dropdowns = dropdowns
			self.embed_count = 0
			self.prev_page.disabled = True
			for i, embed in enumerate(self.embeds):
				embed.set_footer(text=f"Page {i + 1} of {len(self.embeds)}")

		@disnake.ui.button(label="Previous page", emoji="◀️", style=disnake.ButtonStyle.red)
		async def prev_page(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
			self.embed_count -= 1
			embed = self.embeds[self.embed_count]
			self.next_page.disabled = False
			if self.embed_count == 0:
				self.prev_page.disabled = True

			await interaction.response.edit_message(embed=embed, view=self)

		@disnake.ui.button(label="Next page", emoji="▶️", style=disnake.ButtonStyle.green)
		async def next_page(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
			self.embed_count += 1
			embed = self.embeds[self.embed_count]
			self.prev_page.disabled = False
			if self.embed_count == len(self.embeds) - 1:
				self.next_page.disabled = True

			await interaction.response.edit_message(embed=embed, view=self)

	class InitialRoleSelectDropdown(disnake.ui.Select):
		def __init__(self, roles, title, description, min_choices, max_choices):
			self.role_titles = []
			self.title = title
			self.author_name = author_name
			self.author_avatar = author_avatar
			self.roles = roles
			self.min_choices = min_choices
			self.max_choices = max_choices
			[self.role_titles.append(i.name) for i in self.roles]
			super().__init__(
				placeholder=f"Vote in {title}",
				min_values=1,
				max_values=len(role_titles),
				options=self.role_titles
			)

		async def callback(self, inter: disnake.MessageInteraction):
			author_avatar = inter.author.default_avatar.url if inter.author.avatar.url == None else inter.author.avatar.url
			await RoleMenusCog.create_role_menu(
				inter.guild.id,
				inter.author.id,
				inter.author.name,
				author_avatar,
				title,
				description,
				roles,
				min_choices,
				max_choices)

	class InitialRoleSelectView(disnake.ui.View):
		def __init__(self, accessible_roles, title, author_name, author_avatar, min_choices, max_choices):
			super().__init__()
			self.add_item(PollsCog.InitialRoleSelectDropdown(accessible_roles))

	@commands.slash_command()
	async def role_menu(inter: disnake.ApplicationCommandInteraction, title: str, description: str = None):
		"""Make a role menu

		Parameters
		----------
		title: str
			The title of the role menu
		description: str
			The description of the role menu
		"""
		if not inter.author.guild_permissions.manage_roles:
			return await inter.send("You don't have permission to manage roles!", ephemeral=True)
		# Ephemeral dropdow menu(s) to select multiple roles
		# Paginated list of roles
		# Only roles that the bot is above
		# Show warning about that lol
		# If bot can't assign any roles show ephemeral wraning
		print(inter.guild.roles)
		accessible_roles = inter.guild.roles.reverse()[inter.guild.roles.index(inter.me.roles[0]) + 1:]
		if len(accessible_roles != 0):
			for i in accessible_roles:
				if not i.is_assignable():
					accessible_roles.remove(i)
		if len(accessible_roles == 0):
			embed = disnake.Embed(
				title="I can't assign any roles!",
				description="The bot's highest role is below all other roles, so it can't assign any roles. Please move the bot's role above all other roles you want assignable."
				)
			embed.set_image(url="https://media.discordapp.net/attachments/925817023815118962/925818669165072514/New_Project5.png")
			return await inter.send(embed=embed, ephemeral=True)
		embed = disnake.Embed(title=f"Choose roles for the role menu {title}!")
		for i in accessible_roles:
			embed.add_field(
				name=i.name,
				value=i.mention,
			)
		await inter.send(embed=embed, view=InitialRoleSelectView(accessible_roles), ephemeral=True)

	@commands.slash_command(description="Adds a role to a role menu.")
	async def add_role_to_menu(inter: disnake.ApplicationCommandInteraction, title: str, role: disnake.Role):
		"""Add a role to a role menu

		Parameters
		----------
		title: str
			The title of the role menu
		role: disnake.Role
			The role to add to the menu
		"""
		if not inter.author.guild_permissions.manage_roles:
			return await inter.send("You don't have permission to manage roles!", ephemeral=True)

	@commands.slash_command(description="Removes a role to a role menu.")
	async def remove_role_from_menu(inter: disnake.ApplicationCommandInteraction, title: str, role: disnake.Role):
		"""Removes a role from a role menu

		Parameters
		----------
		title: str
			The title of the role menu
		role: disnake.Role
			The role to remove from the menu
		"""
		if not inter.author.guild_permissions.manage_roles:
			return await inter.send("You don't have permission to manage roles!", ephemeral=True)


def setup(bot):
	bot.add_cog(RoleMenusCog(bot))
