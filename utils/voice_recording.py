import discord

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
        ctx.voice_client.start_recording(discord.sinks.WaveSink(), rec_stop_callback, ctx.channel)
        connections.update({ctx.guild.id: ctx.voice_client})

        if rec_type == "emotions":
            em = discord.Embed(title="Запись начата!",
                               description="Завершить анализ - `soul!emotions_stop`", color=0x1f8b4c)
        elif rec_type == "toxicity":
            em = discord.Embed(title="Запись начата!",
                               description="Выключить фильтр токсичности - `soul!toxicity_stop`", color=0x1f8b4c)

        await ctx.send(embed=em)
    else:
        em = discord.Embed(title="Запись уже начата!", color=0x992d22)
        await ctx.send(embed=em)


async def rec_stop(ctx):
    if ctx.guild.id in connections:
        vc = connections[ctx.guild.id]
        vc.stop_recording()
        del connections[ctx.guild.id]
    else:
        em = discord.Embed(title="Запись еще не была начата!", color=0x992d22)
        await ctx.send(embed=em)


async def rec_stop_callback(sink, channel):
    recorded_users = [
        f"<@{user_id}>"
        for user_id, audio in sink.audio_data.items()
    ]
    await sink.vc.disconnect()
    files = [discord.File(audio.file, f"{user_id}.{sink.encoding}") for user_id, audio in sink.audio_data.items()]
    em = discord.Embed(title="Запись завершена!", description=f"В разговоре участвовали: {', '.join(recorded_users)}.",
                       color=0x992d22)
    await channel.send(embed=em, files=files)
