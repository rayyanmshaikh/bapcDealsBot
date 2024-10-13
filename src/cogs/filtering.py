import asyncio.exceptions
import json
import os
from discord.ext import commands


class Filtering(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """ Creates a new filter with specified limitations
    name: name of filter
    commodity: commodity being sold
    min_price: optional minimum price of item
    max_price: optional maximum price of item
    keywords: optional keywords to search for
    """

    @commands.command()
    async def add(self, ctx, name, commodity, min_price=None, max_price=None, *keywords):
        try:
            minimum = int(min_price) if min_price is not None else -1
            maximum = int(max_price) if max_price is not None else -1

        except ValueError:
            await ctx.send("Error: Minimum and maximum price of the item must be set to a number or -1 if unneeded")
            return

        if maximum < minimum:
            await ctx.send("Error: The maximum price must be greater than the minimum price")
            return

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel and message.content.lower() in [
                'y', 'n'] and (message.author.name == data[name].get("creator") or message.author.guild_permissions.
                               administrator)

        new_filter = {name: {"commodity": commodity, "min": min_price, "max": max_price, "keywords": keywords,
                             "creator": ctx.message.author.name, "following": [ctx.message.author.id]}}
        old_filter = {}

        if os.path.exists("filters.json") and os.path.getsize("filters.json") > 0:
            with open("filters.json") as f:
                data = json.load(f)

            old_filter = data.get(name)

            if name in data:
                await ctx.send(f"{ctx.author.mention} you are trying to overwrite the following filter:\n"
                               f"Name - {name}\nType - {commodity}\nMimium Price - {min_price}\nMaximum Price - "
                               f"{max_price}\nKeywords - {', '.join(keywords)}\n"
                               "Would you like to continue overwriting this filter? (y/n)")

                try:
                    user_response = await self.bot.wait_for('message', timeout=10.0, check=check)
                except asyncio.TimeoutError:
                    await ctx.send(f"{ctx.author.mention} you did not decide in time, cancelling overwrite")
                    return

                if user_response.content == 'n':
                    await ctx.send("Cancelled overwrite")
                    return

            data.update(new_filter)
            filter_type = "updated"

        else:
            data = new_filter
            filter_type = "added"

        with open("filters.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        await ctx.send(f"Watcher {name} {filter_type} with the following parameters:\nType - {commodity}\nMimium Price"
                       f" - {min_price}\nMaximum Price - {max_price}\nKeywords - {', '.join(keywords)}")

        if filter_type == "updated":
            await ctx.send(f"{ctx.author.mention} would you like to ping everyone that follows this filter? (y/n)")

            try:
                user_response = await self.bot.wait_for('message', timeout=10.0, check=check)

                if user_response.content == "y":
                    ping = True
                else:
                    ping = False

            except asyncio.TimeoutError:
                await ctx.send(f"{ctx.author.mention} you did not decide in time, pinging...")
                ping = True

            if ping:
                await ctx.send(f"The filter {name} you were following has been updated:\n"
                               f"Old:\nType - {old_filter['commodity']}\nMimium Price - {old_filter['min']}"
                               f"\nMaximum Price - {old_filter['max']}\nKeywords - "
                               f"{', '.join(old_filter['keywords'])}\n"
                               f"New:\nType - {commodity}\nMimium Price - {min_price}"
                               f"\nMaximum Price - {max_price}\nKeywords - "
                               f"{', '.join(keywords)}\n")

                await ctx.send(" ".join(f"<@{user_id}>" for user_id in data[name]["following"]))

    @commands.command()
    async def follow(self, ctx, name):
        if os.path.exists("filters.json") and os.path.getsize("filters.json") > 0:
            with open("filters.json") as f:
                data = json.load(f)

            user_id = ctx.message.author.id

            if name not in data:
                await ctx.send(f"There is no filter named {name}")
                return

            if user_id not in data[name]["following"]:
                data[name]["following"].append(user_id)

            else:
                await ctx.send(f"{ctx.author.mention} you already follow {name}")
                return

            with open("filters.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            await ctx.send(f"{ctx.author.mention} you are now following {name}")

        else:
            await ctx.send("There are no active filters")

    @commands.command()
    async def unfollow(self, ctx, name):
        # Add the user to the filter, if creator option to delete

        await ctx.send(f"{ctx.author.mention} you have unfollowed {name}")

    @commands.command()
    async def remove(self, ctx, name):
        # Remove the specified filter only admins or creator
        await ctx.send(f"{ctx.author.mention} you have removed filter {name}")


async def setup(bot):
    await bot.add_cog(Filtering(bot))
