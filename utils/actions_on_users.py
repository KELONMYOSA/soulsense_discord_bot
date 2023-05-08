import asyncio

import discord


async def mute_user(ctx, user: discord.Member, time: int = 1):
    secs = time * 60
    for channel in ctx.guild.channels:
        if isinstance(channel, discord.TextChannel):
            await ctx.channel.set_permissions(user, send_messages=False)
        elif isinstance(channel, discord.VoiceChannel):
            await channel.set_permissions(user, connect=False)
    await ctx.send(f"{user.mention} был заглушен на {time} мин.")
    await asyncio.sleep(secs)
    for channel in ctx.guild.channels:
        if isinstance(channel, discord.TextChannel):
            await ctx.channel.set_permissions(user, send_messages=None)
        elif isinstance(channel, discord.VoiceChannel):
            await channel.set_permissions(user, connect=None)
