from discord.ext import commands

from utils.speech_to_text import GoogleSpeechRecognition
from utils.voice_recording import join, rec_start, rec_stop


def run(bot):
    @bot.command()
    @commands.has_permissions(administrator=True)
    async def transcribe_start(ctx):
        if await join(ctx) is None:
            return

        await rec_start(ctx, "transcribe")
        recognizer = GoogleSpeechRecognition('ru', ctx.guild.id)
        await recognizer.start_recognition()

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def transcribe_stop(ctx):
        await rec_stop(ctx)
