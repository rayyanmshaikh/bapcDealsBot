import json
import re
import os
import discord.utils
from discord.ext import commands, tasks
from datetime import datetime, timezone

""" Output all posts that fit the filters """

channel_filepath = "data/channels.json"
filter_filepath = "data/filters.json"
subreddit_filepath = "data/subreddit.json"


def timecheck(post_time_str, time):
    """
    Check if publishing time was greater than time
    :param post_time_str: publishing time
    :param time: time in seconds to check for
    :return: true if difference is greater
    """
    post_time = datetime.strptime(post_time_str, "%Y-%m-%dT%H:%M:%S.%f%z")
    current_time = datetime.now(timezone.utc)

    return (current_time - post_time).total_seconds() > time


class Output(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.output.start()

    async def error(self):
        """
        Send an error to the admin due to not setting a channel for the bot to post to
        """
        for channel in self.bot.guilds[0].channels:
            if isinstance(channel, discord.TextChannel):
                try:
                    await channel.send(
                        f"Error: Please inform an admin to use the setChannel command on the channel(s) I can post to")
                    return
                except discord.Forbidden:
                    print(f"Could not send a message in {channel.name} (missing permissions).")
                except discord.HTTPException as e:
                    print(f"Failed to send message in {channel.name}: {e}")

        return

    @tasks.loop(seconds=10)
    async def output(self):
        """
        Send pings to those following relevant filters about posts
        """
        if os.path.exists(channel_filepath):
            with open(channel_filepath, 'r', encoding='utf-8') as f:
                try:
                    channel = json.load(f)
                except json.JSONDecodeError:
                    await self.error()
                    return

        else:
            await self.error()
            return

        if os.path.exists(filter_filepath):
            with open("data/filters.json", "r", encoding="utf-8") as f:
                filters = json.load(f)

        else:
            return

        with open("data/subreddit.json", "r", encoding="utf-8") as f:
            parsed = json.load(f)

        for filt in filters:
            commodity = f"[{filters[filt]['commodity']}]"
            min_price = int(filters[filt]['min'])
            max_price = int(filters[filt]['max'])
            keywords = filters[filt]['keywords']

            for post in parsed["posts"]:
                for key, value in post.items():
                    # if timecheck(value["publishingDate"], 300):
                    #     return

                    post_text = key
                    price_match = re.search(rf"\s*\$*(\d+)\)", post_text)

                    if price_match:
                        price = int(price_match.group(1))
                        keyword_match = all(key in post_text for key in keywords)

                        if commodity in post_text and min_price <= price <= max_price and keyword_match:
                            for ch in channel["channels"]:
                                c = discord.utils.get(self.bot.guilds[0].channels, name=ch)

                                if c and isinstance(c, discord.TextChannel):
                                    await c.send(f"Filter {filt}: {value['link']}\n")
                                    await c.send("".join(f"<@{user_id}>" for user_id in filters[filt]["following"]))


async def setup(bot):
    await bot.add_cog(Output(bot))
