import importlib
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv, find_dotenv

logging.basicConfig(level=logging.INFO)

load_dotenv(find_dotenv())
BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOT_PREFIX = os.environ.get('BOT_PREFIX')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

for x in os.listdir("handlers/"):
    if x.endswith(".py"):
        handler = importlib.import_module("handlers." + x[:-3])
        handler.run(bot)

bot.run(BOT_TOKEN)
