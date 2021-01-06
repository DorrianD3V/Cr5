
class Config:
    token = 'Токен бота'
    extensions = [
        'jishaku',
        'cogs.*',
        'cogs.internal.*'
    ]
    channels = {
        'bugs': 0, # Канал, куда будут отправлятся баги
        'backups': 0, # Канал, куда будут отправлятся дампы PostgreSQL
        'exceptions': 0 # Канал, куда будут отправляться ошибки бота
    }
    database = {
        'url': 'postgresql://username:password@127.0.0.1:5432/cr5'
    }
