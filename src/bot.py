import asyncio

import disnake
import pymongo
# import topgg
from async_timeout import timeout
from disnake.ext import commands, tasks
from dotenv import dotenv_values
# from statcord import StatcordClient

token = dotenv_values(".env")["DISCORD"]
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
db = mongoclient.dropbot 
guild_preferences = db.guild_preferences
role_menus = db.role_menus
polls = db.polls

bot.load_extension("polls")
bot.load_extension("rolemenus")
bot.load_extension("info")

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


bot.remove_command("help")
bot.add_cog(Tasks(bot))

@bot.event
async def on_ready():
	print("-----\nReady\n-----\n")

bot.run(token)
