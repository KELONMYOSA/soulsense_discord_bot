import logging
import os
from os import listdir
from os.path import isfile, join

import asyncio
import speech_recognition

from utils import voice_recording


class GoogleSpeechRecognition:
    def __init__(self, lang, ctx):
        self.lang = lang
        self.ctx = ctx
        self.guild_id = self.ctx.guild.id
        self.folder = f'temp_voice/{self.guild_id}'
        self.r = speech_recognition.Recognizer()

    def recognize(self, file_path):
        file = speech_recognition.AudioFile(file_path)
        result = None
        with file as source:
            self.r.adjust_for_ambient_noise(source)
            audio = self.r.record(source)
            try:
                result = self.r.recognize_google(audio, language=self.lang)
            except speech_recognition.UnknownValueError:
                pass
            except speech_recognition.RequestError:
                logging.error('recognize_google - Internet Connection Lost')

        return result

    async def start_recognition(self, func):
        while self.guild_id in voice_recording.connections:
            files = [f for f in listdir(self.folder) if isfile(join(self.folder, f))]

            for f in files:
                user_id = os.path.splitext(f)[0].split(sep='_')[0]
                file_path = f'{self.folder}/{f}'
                text = self.recognize(file_path)
                os.remove(file_path)
                if text is not None:
                    if func == 'txt':
                        with open(f'temp_voice/{self.guild_id}.txt', "a") as file:
                            member = await self.ctx.guild.fetch_member(user_id)
                            file.write(f"{member}: {text}\n")
                    if func == 'live':
                        await self.ctx.send(f"<@{user_id}>: {text}")

            if len(files) == 0:
                await asyncio.sleep(1)
