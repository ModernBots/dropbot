import asyncio
import datetime
import sys
import traceback
import typing

import disnake
import humanfriendly
import pymongo
import topgg
from async_timeout import timeout
from disnake.ext import commands, tasks
from dotenv import dotenv_values
from statcord import StatcordClient

token = dotenv_values(".env")["DISCORD"]
upsince = datetime.datetime.now()
version = "**ALPHA PRERELEASE**"
intents = disnake.Intents.default()
bot = commands.AutoShardedBot(
	command_prefix=commands.when_mentioned_or(";"),
	intents=intents,
	chunk_guilds_at_startup=False,
)

# topggtoken = dotenv_values(".env")["TOPGG"]
# statcordkey = dotenv_values(".env")["STATCORD"]
# bot.topggpy = topgg.DBLClient(
# 	bot, topggtoken, autopost=True, post_shard_count=True)
# bot.statcord_client = StatcordClient(bot, statcordkey)

mongoclient = pymongo.MongoClient()
db = mongoclient.modernbot 
guild_preferences = db.guild_preferences
role_menus = db.role_menus
polls = db.polls

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

def create_poll(guild_id: int, message_id: int, options: list):
	data = {
		"guild_id": guild_id,
		"channel_id": channel_id,
		"message_id": message_id,
		"votes": []
	}
	if polls.find_one({"message_id": message_id}) != None:
		return False
	polls.insert_one(data)
	return True

class Tasks(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		# self.update_stats.start()
		self.update_status.start()

	@tasks.loop(minutes=30.0)
	async def update_stats(self):
		await self.bot.wait_until_ready()
		await asyncio.sleep(5)
		try:
			await self.bot.topggpy.post_guild_count()
		except Exception as e:
			print(f"\nServer update on top.gg failed\n{e}\n")

	@tasks.loop(minutes=10)
	async def update_status(self):
		await self.bot.wait_until_ready()
		await asyncio.sleep(10)
		await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name=f"/info in {len(bot.guilds):,} servers!"))

class InfoButtons(disnake.ui.View):
	def __init__(self):
		super().__init__()
		self.add_item(disnake.ui.Button(
			style=disnake.ButtonStyle.link,
			label="GitHub",
			emoji="<:github:923861791409307659>",
			url="https://github.com/ThatOneCalculator/modernbot",
			row=0
		))
		self.add_item(disnake.ui.Button(
			style=disnake.ButtonStyle.link,
			label="Invite",
			emoji="😊",
			url="https://discord.com/api/oauth2/authorize?client_id=923845100277202974&permissions=1376805841984&scope=bot%20applications.commands",
			row=0
		))

@bot.slash_command(description="Gives some helpful information about the bot.")
async def info(inter: disnake.ApplicationCommandInteraction):
	# botinfo = await bot.topggpy.get_bot_info()
	# votes = botinfo["monthly_points"]
	# allvotes = botinfo["points"]
	shardscounter = []
	for guild in bot.guilds:
		if guild.shard_id not in shardscounter:
			shardscounter.append(guild.shard_id)
	shards = []
	for i in shardscounter:
		shards.append(bot.get_shard(i))
	allmembers = 0
	for guild in bot.guilds:
		try:
			allmembers += guild.member_count
		except:
			pass
	uptime = datetime.datetime.now() - upsince
	embed = disnake.Embed(
		title="ModernBot Info",
		description="Made by ThatOneCalculator#0001",
		color=0x5865F2,
		#url="https://modernbot.t1c.dev/"
	)
	embed.set_thumbnail(url="https://cdn.discordapp.com/app-icons/923845100277202974/c238b92ba3f25743da34f7d42ff17e03.png?size=512")
	embed.add_field(
		name="🤔 How to use",
		value="""__Type `/`, and navigate to ModernBot to see all the commands.__

__Use `/poll` to make a poll.__
Options should be seperated by commas, and a poll can have up to 25 options.
The poll author can use `/close_poll` to close a poll they made.

__For role menus and role buttons, you must have the **Manage Roles** permission in order to run the commands.__

__Use `/role_menu` to make a role menu.__
You have to choose one role when making a role menu, and can add more roles to a role menu by using `/add_role_to_menu`.
Likewise, you can use `/remove_role_from_menu` to remove a role from a menu.

__Use `/role_button` to make a role button.__
Reccomended for single role assign functions/rule agreement.
Only one button/role per message.
""",
		inline=False
	)
	embed.add_field(
		name="🏓 Ping",
		value=f"Bot latency is {str(round((bot.latency * 1000),2))} milliseconds.",
		inline=False
	)
	embed.add_field(
		name="☕ Uptime",
		value=f"I have been up for {humanfriendly.format_timespan(uptime)}.",
	)
	embed.add_field(
		name="🔮 Shards",
		value=f"This guild is on shard {inter.guild.shard_id}, with a total of {len(shards)} shards.",
	)
	embed.add_field(
		name="👪 Bot stats",
		value=f"I am in {len(bot.guilds):,} servers with a total of {allmembers:,} people.",
	)
	# embed.add_field(
	# 	name="📈 Votes",
	# 	value=f"I have {int(votes):,} mothly votes and {int(allvotes):,} all-time votes on top.gg.",
	# )
	embed.add_field(
		name="🧑‍💻 Version",
		value=f"I am on version {version}. This bot uses disnake, and is licensed under the A-GPLv3 code license. See the GitHub for more info.",
		inline=False
	)
	await inter.send(content=None, embed=embed, view=InfoButtons())

class Polls(commands.Cog):

	class PollDropdown(disnake.ui.Select):
		def __init__(self, poll_options, title, min_choices, max_choices):
			self.options = []
			self.votes = polls.find_one() #TODO
			self.total_votes = []
			for count, i in enumerate(poll_options):
				vote_count = votes[count]
				self.options.append(disnake.SelectOption(
					label=i,
					description=f"{votes} vote{'' if len(vote_count) == 1 else 's'}"
					))
			super().__init__(
				placeholder=title,
				min_values=min_choices,
				max_values=max_choices,
				options=self.options,
			)
		async def callback(self, inter: disnake.MessageInteraction):
			for i in self.values:
				self.votes[i] += 1
			embed = discord.Embed(title=title, description=f"Total votes: {self.total_votes}")
			for count, i in enumerate(self.options):
				blocks_filled = "🟦" * int((self.votes[count]/self.total_votes)*10)
				blocks_empty = "⬜" * int((10-(self.votes[count]/self.total_votes))*10)
				embed.add_field(
					name=i
					value=f"{blocks_filled}{blocks_empty} ({self.votes[count]})"
				)
			await inter.response.edit_message(embed=embed)

	class PollView(disnake.ui.View):
		def __init__(self, poll_options, title, min_choices, max_choices):
			super().__init__()
			self.add_item(SinglePollDropdown(poll_options, title, min_choices, max_choices))

	@bot.slash_command(description="Make a poll. Seperate each option with a comma.")
	async def poll(
		self,
		inter: disnake.ApplicationCommandInteraction, 
		title: str, 
		options: str, 
		min_choices = commands.Param(default=1, ge=1, le=24), 
		max_choices = commands.Param(default=1, ge=1, le=25)):
		poll_options = options.split(",")[:25]
		[i.strip() for i in poll_options]
		[i[:25] for i in poll_options]
		create_poll(inter.guild.id, inter.channel.id, inter.id)
		embed = discord.Embed(title=title)
		for i in options:
			embed.add_field(
				name=i
				value="⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ (0)"
			)
		await inter.send(content=None, embed=embed, view=SinglePollView(poll_options, title, min_choices, max_choices))

class RoleMenus(commands.Cog):

	def has_role_permissions()

	@bot.slash_command(description="Make a role menu. Use /add_role_to_menu to add more roles.")
	async def role_menu(self, inter: disnake.ApplicationCommandInteraction, title: str, description: str = None):
		pass

	@bot.slash_command(description="Adds a role to a role menu.")
	async def add_role_to_menu(self, inter: disnake.ApplicationCommandInteraction, message_id: int, role: disnake.Role, emoji: disnake.Emoji = None):
		pass

	@bot.slash_command(description="Removes a role to a role menu.")
	async def remove_role_from_menu(self, inter: disnake.ApplicationCommandInteraction, message_id: int, position: int = commands.Param(ge=1, le=25)):
		pass

	@bot.slash_command(description="Makes a role button message")
	async def role_button(
		self,
		inter: disnake.ApplicationCommandInteraction, 
		role: disnake.Role, 
		message_title: str, 
		message_description: str = None, 
		button_color: commands.Param(choices=["Blurple", "Gray", "Green", "Red"]), 
		button_emoji: disnake.Emoji = None):
		pass

bot.remove_command("help")
bot.add_cog(Tasks(bot))
bot.add_cog(Polls(bot))
bot.add_cog(RoleMenus(bot))

@bot.event
async def on_ready():
	print("-----\nReady\n-----\n")

bot.run(token)