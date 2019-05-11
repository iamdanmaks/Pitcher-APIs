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
    MSEARCH_INDEX_NAME = 'msearch'
    MSEARCH_BACKEND = 'whoosh'
    MSEARCH_ENABLE = True
    OAUTH_CREDENTIALS = {
        'facebook': {
            'id': '451028598976296',
            'secret': 'cf7c2ba23b5fed2f97a77fb96fc52e2b'
        },
        'google': {
            'id': '175438313875-vbd9cnjbu1otu9jj0r1pgge748sae0gj.apps.googleusercontent.com',
            'secret': 'fvsIS_xMSKzuxi_GZROO8EI_'
        }
    }
