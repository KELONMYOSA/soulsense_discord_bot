import csv
import aiohttp
import asyncio
import os
from os import listdir
from os.path import isfile, join
from datetime import datetime

from pydub import AudioSegment


class SpeechRecognition:
    def __init__(self, ctx):
        self.ctx = ctx
        self.guild_id = self.ctx.guild.id
        self.folder = f'temp_voice/{self.guild_id}'
        self.recognition_url = os.environ.get('RECOGNITION_URL')
        self.emotion_url = os.environ.get('EMOTION_URL')
        self.is_running = True
        self.files_exist = True

    async def recognize(self, file_path, session):
        file = {'file': open(file_path, 'rb')}
        r = await session.post(f'{self.recognition_url}/speech2text', data=file)
        if r.status == 200:
            phrases = await r.json()
        else:
            phrases = []

        return phrases

    async def get_emotion(self, file_path, text, session):
        file = {'file': open(file_path, 'rb')}
        r = await session.post(f'{self.emotion_url}/emotion', data=file, params={'text': text})
        if r.status == 200:
            emotion = await r.json()
        else:
            emotion = ""

        return emotion

    async def start_recognition(self, func):
        async with aiohttp.ClientSession(trust_env=True) as session:
            while self.is_running or self.files_exist:
                files = [f for f in listdir(self.folder) if isfile(join(self.folder, f))]
                if len(files) > 0:
                    self.files_exist = True
                    files.sort(key=lambda f: int(os.path.splitext(f)[0].split(sep='_')[1]))
                    for f in files:
                        filename = os.path.splitext(f)[0].split(sep='_')
                        user_id = filename[0]
                        timestamp = datetime.strptime(filename[1], '%Y%m%d%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
                        time = datetime.strptime(filename[1], '%Y%m%d%H%M%S').strftime('%H:%M:%S')
                        member = await self.ctx.guild.fetch_member(user_id)
                        file_path = f'{self.folder}/{f}'
                        audio_duration = AudioSegment.from_file(file_path, format="wav").duration_seconds
                        phrases = await self.recognize(file_path, session)
                        if func == 'emotions' and len(phrases) > 0:
                            text = " ".join(phrases)
                            emotion = await self.get_emotion(file_path, text, session)
                            if len(emotion) > 0:
                                with open(f'temp_voice/{self.guild_id}.csv', "a") as file:
                                    try:
                                        writer = csv.writer(file)
                                        writer.writerow([timestamp, audio_duration, member.name, emotion, text])
                                    except UnicodeEncodeError as e:
                                        print(e)
                        else:
                            for text in phrases:
                                if func == 'txt':
                                    with open(f'temp_voice/{self.guild_id}.txt', "a") as file:
                                        try:
                                            file.write(f"{time} <{member.name}>: {text}\n")
                                        except UnicodeEncodeError as e:
                                            print(e)
                                if func == 'live':
                                    await self.ctx.send(f"<@{user_id}>: {text}")
                        os.remove(file_path)
                else:
                    self.files_exist = False
                    await asyncio.sleep(0.3)

    async def stop_recognition(self):
        while self.files_exist:
            await asyncio.sleep(0.3)
        self.is_running = False
