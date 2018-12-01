import discord
import os
import asyncio

from discord.ext import commands


class Misc:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def servers(self, ctx):
        servers = f"{self.bot.user.name} is in:\n"
        for server in self.bot.guilds:
            servers += f"{server.name}\n"
        await ctx.send(servers)


def setup(bot):
    bot.add_cog(Misc(bot))
