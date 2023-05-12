import discord


def run(bot):
    @bot.command()
    async def info(ctx):
        await ctx.send('Я предназначен для анализа тона, языка и контекста ваших разговоров, чтобы точно определить '
                       'эмоции всех участников, независимо от того, ведете ли вы серьезную деловую дискуссию или '
                       'беззаботно болтаете с друзьями. \n\n'
                       'I am designed to analyze the tone, language and context of your conversations in order to '
                       'accurately determine the emotions of all participants, regardless of whether you are having '
                       'a serious business discussion or chatting carelessly with friends.\n\n'
                       'Для получения списка команд - `soul!help`')

    bot.remove_command("help")

    @bot.command()
    async def help(ctx):
        em = discord.Embed(title='Help',
                           description='`soul!help` - список команд\n'
                                       '`soul!info` - описание бота\n\n'
                                       '`soul!emotions` - начать анализ эмоций\n'
                                       '`soul!toxicity` - включить фильтр токсичности\n'
                                       '`soul!transcribe_txt` - расшифровка разговора в txt файл\n'
                                       '`soul!transcribe_live` - расшифровка разговора в реальном времени\n\n'
                                       '`soul!stop` - отключить от голосового канала\n',
                           colour=ctx.author.color)
        await ctx.send(embed=em)
