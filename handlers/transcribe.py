from discord.ext import commands

from utils.speech_to_text import GoogleSpeechRecognition
from utils.voice_recording import join, rec_start, rec_stop


def run(bot):
    @bot.command()
    @commands.has_permissions(administrator=True)
    async def transcribe_txt(ctx):
        if await join(ctx) is None:
            return

        await rec_start(ctx, "transcribe_txt")
        recognizer = GoogleSpeechRecognition('ru', ctx)
        await recognizer.start_recognition('txt')

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def transcribe_live(ctx):
        if await join(ctx) is None:
            return

        await rec_start(ctx, "transcribe_live")
        recognizer = GoogleSpeechRecognition('ru', ctx)
        await recognizer.start_recognition('live')

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def stop(ctx):
        await rec_stop(ctx)
