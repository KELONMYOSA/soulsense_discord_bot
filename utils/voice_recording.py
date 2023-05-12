import os

import discord

from utils.stream_sink import StreamSink

connections = {}


async def join(ctx):
    if ctx.author.voice and ctx.author.voice.channel:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            vc = await channel.connect()
        else:
            await ctx.voice_client.move_to(channel)
            vc = ctx.voice_client
        return vc
    else:
        em = discord.Embed(title="Вы не находитесь в голосовом канале!", color=0x992d22)
        await ctx.send(embed=em)


async def rec_start(ctx, rec_type):
    if ctx.guild.id not in connections:
        connections.update({ctx.guild.id: ctx.voice_client})
        sink = StreamSink(ctx.guild.id)

        if rec_type == "emotions":
            em = discord.Embed(title="Запись начата!",
                               description="Завершить анализ - `soul!emotions_stop`", color=0x1f8b4c)
        elif rec_type == "toxicity":
            em = discord.Embed(title="Запись начата!",
                               description="Выключить фильтр токсичности - `soul!toxicity_stop`", color=0x1f8b4c)
        elif rec_type == "transcribe":
            ctx.voice_client.start_recording(sink, rec_stop_callback_transcribe, ctx.channel)
            em = discord.Embed(title="Запись начата!",
                               description="Завершить распознавание речи - `soul!transcribe_stop`", color=0x1f8b4c)

        await ctx.send(embed=em)
    else:
        em = discord.Embed(title="Запись уже начата!", color=0x992d22)
        await ctx.send(embed=em)


async def rec_stop(ctx):
    if ctx.guild.id in connections:
        vc = connections[ctx.guild.id]
        vc.stop_recording()
        del connections[ctx.guild.id]
        os.rmdir(f'temp_voice/{ctx.guild.id}')
    else:
        em = discord.Embed(title="Запись еще не была начата!", color=0x992d22)
        await ctx.send(embed=em)


async def rec_stop_callback_transcribe(sink, channel):
    recorded_users = [
        f"<@{user_id}>"
        for user_id in sink.recorded_users
    ]

    await sink.vc.disconnect()

    em = discord.Embed(title="Запись завершена!",
                       description=f"В разговоре участвовали: {', '.join(recorded_users)}.",
                       color=0x992d22)

    await channel.send(embed=em)
