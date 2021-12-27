import datetime

import disnake
import pymongo
from bson.objectid import ObjectId
from disnake.ext import commands

mongoclient = pymongo.MongoClient()
db = mongoclient.modernbot
guild_preferences = db.guild_preferences
polls = db.polls


class PollsCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	def create_poll(self, guild_id: int, author_id: int, options: list, votes: list):
		data = {
			"guild_id": guild_id,
			"author_id": author_id,
			"options": options,
			"votes": votes
		}
		return polls.insert_one(data).inserted_id

	def get_poll(post_id):
		return polls.find_one({"_id": ObjectId(post_id)})

	# https://github.com/DisnakeDev/disnake/blob/master/examples/views/persistent.py

	class PollDropdown(disnake.ui.Select):
		def __init__(self, options, title, min_choices, max_choices, poll_id):
			self.poll_options = []
			self.title = title
			# self.author = author
			self.votes = PollsCog.get_poll(str(poll_id))["votes"]
			for count, i in enumerate(options):
				vote_count = self.votes[count]
				self.poll_options.append(disnake.SelectOption(label=i))
			super().__init__(
				placeholder=title,
				min_values=min_choices,
				max_values=max_choices,
				options=self.poll_options,
				custom_id=str(poll_id)
			)

		async def callback(self, inter: disnake.MessageInteraction):
			for i in range(self.values):
				self.votes[i] += 1
			embed = disnake.Embed(
				title=self.title, description=f"Total votes: {self.total_votes}")
			for count, i in enumerate(self.options):
				blocks_filled = "🟦" * int((self.votes[count]/self.total_votes)*10)
				blocks_empty = "⬜" * int((10-(self.votes[count]/self.total_votes))*10)
				embed.add_field(
					name=i,
					value=f"{blocks_filled}{blocks_empty} ({self.votes[count]})"
				)
			await inter.response.edit_message(embed=embed)

	class PollView(disnake.ui.View):
		def __init__(self, poll_options, title, min_choices, max_choices, poll_id):
			super().__init__(timeout=None)
			self.add_item(PollsCog.PollDropdown(
				poll_options, title, min_choices, max_choices, poll_id))

	@commands.slash_command(description="Make a poll. Seperate each option with a comma.")
	async def poll(
		self,
		inter: disnake.ApplicationCommandInteraction,
		title: str,
		options: str,
		min_choices=commands.Param(default=1, ge=1, le=24),
		max_choices=commands.Param(default=1, ge=1, le=25)):
		poll_options = options.split(",")[:25]
		[i.strip() for i in poll_options]
		[i[:25] for i in poll_options]
		votes = []
		for i in poll_options:
			votes.append(0)
		poll_id = self.create_poll(inter.guild.id, inter.author.id, poll_options, votes)
		embed = disnake.Embed(title=title)
		for i in poll_options:
			embed.add_field(
				name=i,
				value="⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜ (0)"
			)
		await inter.send(content=None, embed=embed, view=self.PollView(poll_options, title, min_choices, max_choices, poll_id))

	def autocomplete_title(self, inter: disnake.ApplicationCommandInteraction, user_input: str):
		guild_polls = polls.find_many({"guild_id": inter.guild.id})
		open_polls = []
		for i in guild_polls:
			open_polls.append(guild_polls["title"])
		return [i for i in open_polls if user_input in i]

	@commands.slash_command(description="Close a poll.")
	async def close_poll(self, inter: disnake.ApplicationCommandInteraction, title: str = commands.Param(autocomplete=autocomplete_title)):
		# Condition: must be mod or poll author
		# TODO: Get message
		# message.edit_original(view=None)
		polls.delete_one({"message_id": inter.id})
		await inter.send("Poll closed.")


def setup(bot):
	bot.add_cog(PollsCog(bot))
