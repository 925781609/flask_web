import os

basedir = os.path.abspath(os.path.dirname(__file__))

HOSTNAME = 'localhost'
DATABASE = 'r'
USERNAME = 'web'
PASSWORD = 'web' #os.environ.get('PASSWORD')
DB_URI = 'mysql+mysqlconnector://{}:{}@{}/{}'.format(
        USERNAME, PASSWORD, HOSTNAME, DATABASE )

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True   
    MAIL_SERVER = 'smtp.yeah.cn'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME =os.environ.get('MAIL_USERNAME') , 
    MAIL_PASSWORD =  os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'web_admin@yeah.net'
    FLASKY_ADMIN = 'web_admin@yeah.net'
    BOOTSTRAP_SERVE_LOCAL = True
    FLASKY_POSTS_PER_PAGE=20
    FLASKY_FOLLOWERS_PER_PAGE = 1
    FLASKY_COMMENTS_PER_PAGE = 1

    @staticmethod
    def init_app(app):
        pass
mmm = Config()
print("Display member of config")
print(Config.MAIL_USERNAME)
print(Config.MAIL_PASSWORD)

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = DB_URI

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

