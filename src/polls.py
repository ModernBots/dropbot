import datetime

import disnake
from bson.objectid import ObjectId
from disnake.ext import commands
from motor import motor_asyncio

mongoclient = motor_asyncio.AsyncIOMotorClient()
db = mongoclient.modernbot
guild_preferences = db.guild_preferences
polls = db.polls


class PollsCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.persistent_polls = []

	async def create_poll(
		self,
		guild_id: int,
		author_id: int,
		author_name: str,
		author_avatar: str,
		title: str,
		options: list,
		votes: list,
		voted: list,
		min_choices: int,
		max_choices: int):
		data = {
			"guild_id": guild_id,
			"message_id": None,
			"author_id": author_id,
			"author_name": author_name,
			"author_avatar": author_avatar,
			"title": title,
			"options": options,
			"votes": votes,
			"voted": voted,
			"min_choices": min_choices,
			"max_choices": max_choices
		}
		return (await polls.insert_one(data)).inserted_id

	async def get_poll(post_id):
		return await polls.find_one({"_id": ObjectId(post_id)})


	class PollDropdown(disnake.ui.Select):
		def __init__(self, options, title, author_name, author_avatar, min_choices, max_choices, poll_id, votes, voted):
			self.poll_options = []
			self.title = title
			self.poll_id = poll_id
			self.str_options = options
			self.author_name = author_name
			self.author_avatar = author_avatar
			self.votes = votes
			self.voted = voted
			for i in options:
				self.poll_options.append(disnake.SelectOption(label=i))
			super().__init__(
				placeholder=f"Vote in {title}",
				min_values=min_choices,
				max_values=max_choices,
				options=self.poll_options,
				custom_id="poll"
			)

		async def callback(self, inter: disnake.MessageInteraction):
			if inter.author.id in self.voted:
				return await inter.send(f"You have already voted in this poll!", ephemeral=True)
			self.voted.append(inter.author.id)
			votes_to_update = []
			for i in self.values:
				index = self.str_options.index(i)
				votes_to_update.append(index)
			for i in votes_to_update:
				self.votes[i] += 1
			total_votes = 0
			for i in self.votes:
				total_votes += i
			await polls.update_one({"_id": self.poll_id}, {"$set": {"votes": self.votes}})
			await polls.update_one({"_id": self.poll_id}, {"$set": {"voted": self.voted}})
			embed = disnake.Embed(
				title=self.title, description=f"Total votes: {total_votes}")
			for count, i in enumerate(self.poll_options):
				filled = self.votes[count]/total_votes * 5
				filled_remainder = round(filled % 1, 2)
				if filled_remainder < 0.1:
					filled_partial = ""
				elif filled_remainder <= 0.35:
					filled_partial = "<:poll_one_quarter:925262450956316673>"
				elif filled_remainder <= 0.65:
					filled_partial = "<:poll_half:925262451304439849>"
				elif filled_remainder <= 0.9:
					filled_partial = "<:poll_three_quarters:925262451304456232>"
				else:
					filled_partial = "<:poll_full:925262451115687957>"
				blocks_filled = f"{'<:poll_full:925262451115687957>' * int(filled)}{filled_partial}"
				block_count = int(filled)
				if filled_partial != "":
					block_count += 1
				blocks_empty = "<:poll_empty:925262451287670794>" * (5 - block_count)
				total_blocks = f"{blocks_filled}{blocks_empty}"
				if int(self.votes[count]) >= 1 and total_blocks == "<:poll_empty:925262451287670794><:poll_empty:925262451287670794><:poll_empty:925262451287670794><:poll_empty:925262451287670794><:poll_empty:925262451287670794>":
					total_blocks = "<:poll_one_quarter:925262450956316673><:poll_empty:925262451287670794><:poll_empty:925262451287670794><:poll_empty:925262451287670794><:poll_empty:925262451287670794><:poll_empty:925262451287670794>"
				winner = " ✅" if int(self.votes[count]) == max(self.votes) else ""
				embed.add_field(
					name=i,
					value=f"{total_blocks} ({self.votes[count]}{winner})"
				)
				embed.set_author(
					name=f"Poll ran by {self.author_name}",
					icon_url=self.author_avatar
				)
			await inter.response.edit_message(embed=embed)

	class PollView(disnake.ui.View):
		def __init__(self, poll_options, title, author_name, author_avatar, min_choices, max_choices, poll_id, votes, voted):
			super().__init__(timeout=None)
			self.add_item(PollsCog.PollDropdown(
				poll_options, title, author_name, author_avatar, min_choices, max_choices, poll_id, votes, voted))

	@commands.slash_command(description="Make a poll. Seperate each option with a comma.")
	async def poll(
		self,
		inter: disnake.ApplicationCommandInteraction,
		title: str,
		options: str,
		min_choices: int=commands.Param(default=1, ge=1, le=24),
		max_choices: int=commands.Param(default=1, ge=1, le=25)):
		poll_options = options.split(",")[:25]
		[i.strip() for i in poll_options]
		[i[:25] for i in poll_options]
		votes = []
		for i in poll_options:
			votes.append(0)
		author_avatar = inter.author.default_avatar.url if inter.author.avatar.url == None else inter.author.avatar.url
		poll_id = await self.create_poll(inter.guild.id, inter.author.id, inter.author.name, author_avatar, title, poll_options, votes, [], min_choices, max_choices)
		embed = disnake.Embed(title=title)
		for i in poll_options:
			embed.add_field(
				name=i,
				value="<:poll_empty:925262451287670794><:poll_empty:925262451287670794><:poll_empty:925262451287670794><:poll_empty:925262451287670794><:poll_empty:925262451287670794> (0)"
			)
			embed.set_author(
				name=f"Poll ran by {inter.author.name}",
				icon_url=author_avatar
			)
		votes = (await PollsCog.get_poll(str(poll_id)))["votes"]
		voted = (await PollsCog.get_poll(str(poll_id)))["voted"]
		poll_sent = await inter.send(content=None, embed=embed, view=self.PollView(poll_options, title, inter.author.name, author_avatar, min_choices, max_choices, poll_id, votes, voted))
		original_message = await inter.original_message()
		await polls.update_one({"_id": poll_id}, {"$set": {"message_id": original_message.id}})

	@commands.slash_command(description="Close a poll.")
	async def close_poll(self, inter: disnake.ApplicationCommandInteraction, title: str):
		poll_to_close = await polls.find_one({"title": title})
		author_id = self.bot.get_message(poll_to_close["author_id"])
		if author_id != inter.author.id or not inter.author.guild_permissions.manage_messages:
			return await inter.send("You don't have permission to close this poll.", ephemeral=True)
		message = self.bot.get_message(poll_to_close["message_id"])
		if message == None:
			message = await inter.channel.fetch_message(poll_to_close["message_id"])
		if message == None:
			return await inter.send("I couldn't find the poll! Please make sure you're running this command in the ***same channel*** as the poll was sent.", ephemeral=True)
		await message.edit(view=None)
		await polls.delete_one({"title": title})
		await inter.send("Poll closed.")

	@close_poll.autocomplete("title")
	async def autocomplete_title(self, inter: disnake.ApplicationCommandInteraction, user_input: str):
		guild_polls = []
		guild_polls_cursor = polls.find({"guild_id": inter.guild.id})
		for i in await guild_polls_cursor.to_list(length=300):
			try:
				guild_polls.append(i["title"])
			except:
				pass
		return [i for i in guild_polls if user_input in i]

	@commands.Cog.listener()
	async def on_ready(self):
		print("Added polls cog!")

	@commands.Cog.listener()
	async def on_message_interaction(self, inter: disnake.ApplicationCommandInteraction):
		if inter.component.custom_id != "poll":
			return
		for view in self.bot.persistent_views:
			if view.message_id == inter.message.id:
				break
		else:
			poll_to_add = await polls.find_one({"message_id": inter.message.id})
			view = self.PollView(
				poll_to_add["options"],
				poll_to_add["title"],
				poll_to_add["author_name"],
				poll_to_add["author_avatar"],
				poll_to_add["min_choices"],
				poll_to_add["max_choices"],
				poll_to_add["_id"],
				poll_to_add["votes"],
				poll_to_add["voted"]
			)
			self.bot.add_view(view, message_id=inter.message.id)
			print("Added a persistent poll!")
		await view.PollDropdown.callback(inter)


def setup(bot):
	bot.add_cog(PollsCog(bot))
