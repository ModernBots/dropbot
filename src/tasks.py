import asyncio

import disnake
from disnake import commands, tasks
from dotenv import dotenv_values
# import topgg
# from statcord import StatcordClient

topggtoken = dotenv_values(".env")["TOPGG"]
statcordkey = dotenv_values(".env")["STATCORD"]


class Tasks(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		# self.bot.topggpy = topgg.DBLClient(bot, topggtoken, autopost=True, post_shard_count=True)
		# self.bot.statcord_client = StatcordClient(bot, statcordkey)
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
		await self.bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name=f"/info in {len(self.bot.guilds):,} servers!"))


def setup(bot):
	bot.add_cog(Tasks(bot))
