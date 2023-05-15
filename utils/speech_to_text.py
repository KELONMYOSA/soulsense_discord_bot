import aiohttp
import asyncio
import os
from os import listdir
from os.path import isfile, join


class SpeechRecognition:
    def __init__(self, ctx):
        self.ctx = ctx
        self.guild_id = self.ctx.guild.id
        self.folder = f'temp_voice/{self.guild_id}'
        self.recognition_url = os.environ.get('RECOGNITION_URL')
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

    async def start_recognition(self, func):
        async with aiohttp.ClientSession() as session:
            while self.is_running or self.files_exist:
                files = [f for f in listdir(self.folder) if isfile(join(self.folder, f))]
                if len(files) > 0:
                    self.files_exist = True
                    files.sort(key=lambda f: int(os.path.splitext(f)[0].split(sep='_')[1]))
                    for f in files:
                        user_id = os.path.splitext(f)[0].split(sep='_')[0]
                        file_path = f'{self.folder}/{f}'
                        phrases = await self.recognize(file_path, session)
                        os.remove(file_path)
                        for text in phrases:
                            if func == 'txt':
                                with open(f'temp_voice/{self.guild_id}.txt', "a") as file:
                                    member = await self.ctx.guild.fetch_member(user_id)
                                    file.write(f"<{member.name}>: {text}\n")
                            if func == 'live':
                                await self.ctx.send(f"<@{user_id}>: {text}")
                else:
                    self.files_exist = False
                    await asyncio.sleep(0.3)

    async def stop_recognition(self):
        while self.files_exist:
            await asyncio.sleep(0.3)
        self.is_running = False
