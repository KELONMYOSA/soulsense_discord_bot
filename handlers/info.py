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
                                       '`soul!info` - описание бота\n'
                                       '`soul!emotions_start` - начать анализ эмоций\n'
                                       '`soul!emotions_stop` - завершить анализ и получить отчет\n'
                                       '`soul!toxicity_start` - включить фильтр токсичности\n'
                                       '`soul!toxicity_stop` - выключить фильтр токсичности\n',
                           colour=ctx.author.color)
        await ctx.send(embed=em)
