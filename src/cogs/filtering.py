import asyncio.exceptions
import json
import os
from discord.ext import commands

""" The class meant to interact with the users for all commands to update the filters """

filepath = "data/filters.json"


class Filtering(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def add(self, ctx, name=None, commodity=None, min_price=None, max_price=None, *keywords):
        """
        Creates a new filter with specified limitations
        name: name of filter
        :param ctx:
        :param name: name of the filter
        :param commodity: commodity being sold
        :param min_price: optional minimum price of item
        :param max_price: optional maximum price of item
        :param keywords: optional keywords to search for
        :return: None
        """
        if name is None or commodity is None:
            await ctx.send("Error: You must give the filter a name and a item to filter for")
            return

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

        standardized = [key.lower() for key in keywords]

        new_filter = {name.lower(): {"commodity": commodity.lower(), "min": min_price, "max": max_price, "keywords":
            standardized, "creator": ctx.message.author.name, "following": [ctx.message.author.id]}}

        old_filter = {}
        filter_type = ""

        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            with open(filepath) as f:
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

                filter_type = "updated"

            else:
                filter_type = "added"

            data.update(new_filter)

        else:
            data = new_filter

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        await ctx.send(f"Filter {name} {filter_type} with the following parameters:\nType - {commodity}\nMimium Price"
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
    async def remove(self, ctx, name):
        """
        Removes the filter specified
        :param ctx:
        :param name: name of filter
        :return: None
        """
        if name is None:
            await ctx.send("Error: You must give a filter name to remove")
            return

        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            with open(filepath) as f:
                data = json.load(f)

            if name not in data:
                await ctx.send(f"There is no filter named {name}")
                return

            elif ctx.author.name != data[name]["creator"] and not ctx.author.guild_permissions.administrator:
                await ctx.send(f"{ctx.author.mention} you have to be the creator or an admin to delete {name}")
                return

            else:
                data.pop(name)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            await ctx.send(f"{ctx.author.mention} you have deleted {name}")

        else:
            await ctx.send("There are no active filters")

    @commands.command()
    async def follow(self, ctx, name=None):
        """
        User follows the filter specified
        :param ctx:
        :param name: name of filter
        :return:
        """
        if name is None:
            await ctx.send("Error: You must give a filter name to follow")
            return

        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            with open(filepath) as f:
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

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            await ctx.send(f"{ctx.author.mention} you are now following {name}")

        else:
            await ctx.send("There are no active filters")

    @commands.command()
    async def unfollow(self, ctx, name=None):
        """
        User unfollows the filter specified
        :param ctx:
        :param name: name of filter
        :return:
        """
        if name is None:
            await ctx.send("Error: You must give a filter name to unfollow")
            return

        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            with open(filepath) as f:
                data = json.load(f)

            user_id = ctx.message.author.id

            if name not in data:
                await ctx.send(f"There is no filter named {name}")
                return

            elif user_id not in data[name]["following"]:
                await ctx.send(f"{ctx.author.mention} you don't follow {name}")
                return

            else:
                data[name]["following"].remove(user_id)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            await ctx.send(f"{ctx.author.mention} you have unfollowed {name}")

        else:
            await ctx.send("There are no active filters")


async def setup(bot):
    await bot.add_cog(Filtering(bot))
