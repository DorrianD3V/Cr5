import discord


class Config:
    token = 'Токен бота'

    extensions = [
        'jishaku',
        'cogs.*',
        'cogs.internal.*',
        'cogs.utils.*'
    ]

    channels = {
        'bugs': 0, # Канал, куда будут отправлятся баги
        'backups': 0, # Канал, куда будут отправлятся дампы PostgreSQL
        'exceptions': 0 # Канал, куда будут отправляться ошибки бота
    }

    database = {
        'url': 'postgresql://username:password@127.0.0.1:5432/cr5'
    }

    environ = {
        'JISHAKU_NO_UNDERSCORE': '1',
        'JISHAKU_NO_DM_TRACEBACK': '1',
        'JISHAKU_HIDE': '1'
    }

    activity = discord.Activity(type=discord.ActivityType.listening,
                                name='c.help')

    tokens = {
        'owm': 'Токен OpenWeatherMap API', # Используется для модуля pyowm в команде weather
        'google_search': 'Токен Google Search API', # Используется для команды google
        'osu!': 'Токен osu! API', # Используется в команде osu!
        'wolfram': 'ID приложения Wolfram Alpha' # Используется в команде wolframalpha
    }
