import os

import discord

from utils.speech_to_text import SpeechRecognition
from utils.stream_sink import StreamSink

connections = {}
recognizers = {}
rec_types = {}


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
        if ctx.guild.id not in rec_types:
            connections.update({ctx.guild.id: ctx.voice_client})
            rec_types.update({ctx.guild.id: rec_type})
            sink = StreamSink(ctx.guild.id)
            recognizer = SpeechRecognition(ctx)
            recognizers.update({ctx.guild.id: recognizer})

            ctx.voice_client.start_recording(sink, rec_stop_callback, ctx.channel)

            if rec_type == "emotions":
                em = discord.Embed(title="Запись начата!",
                                   description="Завершить анализ - `soul!stop`", color=0x1f8b4c)
                await ctx.send(embed=em)
                await recognizer.start_recognition('emotions')
            elif rec_type == "toxicity":
                em = discord.Embed(title="Запись начата!",
                                   description="Выключить фильтр токсичности - `soul!stop`", color=0x1f8b4c)
                await ctx.send(embed=em)
            elif rec_type == "transcribe_txt":
                em = discord.Embed(title="Запись начата!",
                                   description="Завершить распознавание речи - `soul!stop`", color=0x1f8b4c)
                await ctx.send(embed=em)
                await recognizer.start_recognition('txt')
            elif rec_type == "transcribe_live":
                em = discord.Embed(title="Запись начата!",
                                   description="Завершить распознавание речи - `soul!stop`", color=0x1f8b4c)
                await ctx.send(embed=em)
                await recognizer.start_recognition('live')
        else:
            em = discord.Embed(title="Подождите, пока не будут обработаны результаты!", color=0x992d22)
            await ctx.send(embed=em)
    else:
        em = discord.Embed(title="Запись уже начата!", color=0x992d22)
        await ctx.send(embed=em)


async def rec_stop(ctx):
    if ctx.guild.id in connections:
        vc = connections[ctx.guild.id]
        vc.stop_recording()
        del connections[ctx.guild.id]
        recognizer = recognizers[ctx.guild.id]
        del recognizers[ctx.guild.id]
        await recognizer.stop_recognition()
        os.rmdir(f'temp_voice/{ctx.guild.id}')
        if rec_types[ctx.guild.id] == "transcribe_txt":
            await send_transcribe_txt(ctx)
        elif rec_types[ctx.guild.id] == "emotions":
            await send_emotions_report(ctx)
        del rec_types[ctx.guild.id]
    else:
        em = discord.Embed(title="Запись еще не была начата!", color=0x992d22)
        await ctx.send(embed=em)


async def rec_stop_callback(sink, channel):
    recorded_users = [
        f"<@{user_id}>"
        for user_id in sink.recorded_users
    ]

    await sink.vc.disconnect()

    em = discord.Embed(title="Запись завершена!",
                       description=f"В разговоре участвовали: {', '.join(recorded_users)}.\n\n"
                                   f"Как только результаты будут обработаны - я их отправлю.",
                       color=0x992d22)

    await channel.send(embed=em)


async def send_transcribe_txt(ctx):
    file_path = f'temp_voice/{ctx.guild.id}.txt'
    try:
        file = discord.File(file_path)
        file.filename = 'transcription.txt'
        await ctx.send(file=file)
        os.remove(file_path)
    except FileNotFoundError:
        print(f"File transcription.txt not found for guild ID-{ctx.guild.id}")


async def send_emotions_report(ctx):
    file_path = f'temp_voice/{ctx.guild.id}.csv'
    try:
        file = discord.File(file_path)
        file.filename = 'emotions_report.csv'
        await ctx.send(file=file)
        os.remove(file_path)
    except FileNotFoundError:
        print(f"File emotions_report.csv not found for guild ID-{ctx.guild.id}")
