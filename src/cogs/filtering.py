# contains all the code for filters, read to add, delete, update

from discord.ext import commands


class Filtering(commands.Cog):
    def __int__(self, bot):
        self.bot = bot

    """ Creates a new filter with specified limitations
    name: name of filter
    commodity: commodity being sold
    min_price: optional minimum price of item
    max_price: optional maximum price of item
    keywords: optional keywords to search for
    """

    @commands.command()
    async def addFilter(self, ctx, name, commodity, min_price=None, max_price=None, *keywords):
        try:
            int(min_price) if min_price is not None else -1
            int(max_price) if max_price is not None else -1
        except ValueError:
            await ctx.send("Error: Minimum and maximum price of the item must be set to a number or -1 if unneeded")
            return

        if max_price < min_price:
            await ctx.send("Error: The maximum price must be greater than the minimum price")
            return

        # Send to DB or store in file for testing

        await ctx.send(f"Watcher {name} added with the following parameters:\nType - {commodity}\nMimium Price (if "
                       f"declared) - {min_price}\nMaximum Price (if declared) - {max_price}\nKeywords - "
                       f"{', '.join(keywords)}")

    @commands.command()
    async def follow(self, ctx, name):
        #Add the user to the filter

        await ctx.send(f"{ctx.author.mention} you are now watching {name}")

    @commands.command()
    async def remove(self, ctx, name):
        #Remove the specified filter
        await ctx.send(f"{ctx.author.mention} you have removed filter {name}")

    @commands.command()
    async def update(self, ctx, name, commodity=None, min_price=None, max_price=None, *keywords):
        #Update filter name with any field that is filled
        await ctx.send(f"{ctx.author.mention} you have updated {name}")


async def setup(bot):
    await bot.add_cog(Filtering(bot))
