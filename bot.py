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
version = "1.0.0"
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
reaction_roles = db.reaction_roles

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
		value="""Type `/`, and navigate to ModernBot to see all the commands.

I have 2 main functions: polls and role menus.

For polls, you can use `/single_poll` to make a poll where everyone can vote only once, and `/multi_poll` to make a poll where everyone can vote one or more times.
Options should be seperated by commas, and a poll can have up to 25 options.
Example: `/single_poll title:What's your favorite fruit? options:Apple, Orange, Banana, Lime, Strawberry`
The poll author can use `/close_poll` to close a poll they made.

For role menus, you must have the **Manage Roles** permission in order to run the commands.
You can use `/single_role_menu` to make a role menu where everyone can only choose one role, and `/multi_role_menu` to make a role menu where everyone can choose one or more roles.
You have to choose one role when making a role menu, and can add more roles to a role menu by using `/add_role_to_menu`. Likewise you can use `/remove_role_from_menu` to remove a role from a menu.
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

@bot.slash_command(description="Poll: vote for one option. Seperate each option with a comma.")
async def single_poll(inter: disnake.ApplicationCommandInteraction, options: str):
	pass

@bot.slash_command(description="Poll: vote for one or more option(s). Seperate each option with a comma.")
async def multi_poll(inter: disnake.ApplicationCommandInteraction, options: str):
	pass

@bot.slash_command(description="Stops a poll from being voted on.")
async def close_poll(inter: disnake.ApplicationCommandInteraction):
	pass

@bot.slash_command(description="Role menu: assign one role. Use /add_role_to_menu to add more roles.")
async def single_role_menu(inter: disnake.ApplicationCommandInteraction, title: str, description: str = None):
	pass

@bot.slash_command(description="Role menu: assign one or more role(s). Use /add_role_to_menu to add more roles.")
async def multi_role_menu(inter: disnake.ApplicationCommandInteraction, title: str, description: str = None):
	pass

@bot.slash_command(description="Adds a role to a role menu.")
async def add_role_to_menu(inter: disnake.ApplicationCommandInteraction, message_id: int, role: disnake.Role, emoji: disnake.Emoji = None):
	pass

@bot.slash_command(description="Removes a role to a role menu.")
async def remove_role_from_menu(inter: disnake.ApplicationCommandInteraction, message_id: int, position: int = commands.Param(ge=1, le=25), emoji: disnake.Emoji = None):
	pass

@bot.event
async def on_ready():
	print("-----\nReady\n-----\n")

bot.login(token)