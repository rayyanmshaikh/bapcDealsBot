import os
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import asyncio
from classes.parser import run

load_dotenv('../.env')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='?', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await periodic_run()
    print('------')
    await load_cogs()


async def load_cogs():
    """
    Load all cogs
    :return:
    """
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            cog = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(cog)
                print(f'Loaded {cog}')
            except Exception as e:
                print(f'Failed to load {cog}: {e}')


@tasks.loop(seconds=300)
async def periodic_run():
    """
    Updates stored posts periodically
    :return: None
    """
    await run()


if __name__ == "__main__":
    bot.run(os.getenv('token'))
