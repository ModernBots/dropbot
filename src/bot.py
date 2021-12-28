import disnake
from disnake.ext import commands
from dotenv import dotenv_values

token = dotenv_values(".env")["DISCORD"]
intents = disnake.Intents.default()
bot = commands.AutoShardedBot(
	command_prefix=commands.when_mentioned_or(";"),
	intents=intents,
	chunk_guilds_at_startup=False,
)
extensions = ["polls", "rolemenus", "errorhandler", "info", "tasks"] # errorhandler
for i in extensions:
	bot.load_extension(i)
bot.remove_command("help")

@bot.event
async def on_ready():
	print("-----\nReady\n-----\n")

if __name__ == "__main__":
	bot.run(token)
