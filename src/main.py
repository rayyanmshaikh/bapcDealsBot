import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv('../.env')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='?', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    await load_cogs()


async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            cog = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(cog)
                print(f'Loaded {cog}')
            except Exception as e:
                print(f'Failed to load {cog}: {e}')


bot.run(os.getenv('token'))
