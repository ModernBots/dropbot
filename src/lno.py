import disnake
from disnake.ext import commands, tasks

class LiterallyNoCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

def setup(bot):
	bot.add_cog(LiterallyNoCog(bot))