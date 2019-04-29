import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = "are-lobsters-mermaids-for-scorpions"
    #SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:343dfb3e@localhost/pitcher_application"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir[:-12], 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    COMPRESS_MIMETYPES = ['application/json']
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500
    JWT_SECRET_KEY = 'jwt-secret-string'
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
