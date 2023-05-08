from discord.ext import commands

from utils.voice_recording import join, rec_start, rec_stop


def run(bot):
    @bot.command()
    @commands.has_permissions(administrator=True)
    async def emotions_start(ctx):
        if await join(ctx) is None:
            return

        await rec_start(ctx, "emotions")

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def emotions_stop(ctx):
        await rec_stop(ctx)
