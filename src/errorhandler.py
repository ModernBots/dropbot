import disnake
from disnake.ext import commands


class CommandErrorHandler(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_command_error(inter, error):
		if hasattr(inter, "on_error"):
			return
		ignored = (commands.errors.CommandNotFound,
				   commands.errors.UserInputError)
		error = getattr(error, "original", error)
		if isinstance(error, ignored):
			return
		elif isinstance(error, commands.errors.DisabledCommand):
			return await inter.send(content=f"{inter.command} has been disabled.", ephemeral=True)
		elif isinstance(error, commands.errors.NoPrivateMessage):
			try:
				return await inter.author.send(f"{inter.command} can not be used in Private Messages.")
			except:
				pass
		elif isinstance(error, commands.errors.BadArgument):
			if inter.command.qualified_name == "tag list":
				return await inter.send(content="I could not find that member. Please try again.", ephemeral=True)
		elif isinstance(error, commands.errors.CommandOnCooldown):
			return await inter.send(content="You're on cooldown!", ephemeral=True)
		print(f"Ignoring exception in command {inter.command}:", file=sys.stderr)
		traceback.print_exception(
			type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
	bot.add_cog(CommandErrorHandler(bot))
