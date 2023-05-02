def run(bot):
    @bot.event
    async def on_guild_join(guild):
        text_channels = guild.text_channels

        if text_channels:
            channel = text_channels[0]

        await channel.send('Привет!\n'
                           'Я помогу определить эмоции участников во время разговора '
                           'и уменьшить токсичность пользователей.\n\n'
                           'Для получения списка команд - `soul!help`')
