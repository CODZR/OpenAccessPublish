import os
class Config:
    # csrf config
    CSRF_ENABLED = True
    SECRET_KEY = 'qe4v^trRAVVO7s1R7W46C8@d5ft$HY45gr'

    BASEPATH = os.getcwd().replace('\\', r'\\')
    # sqlalchemy config
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///refer.sqlite3'
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://debian-sys-maint:nG5tyhQzcnity09E@localhost/db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail config
    MAIL_DEBUG = True
    MAIL_SUPPRESS_SEND = False
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = '975336710@qq.com'
    MAIL_PASSWORD = 'mbdqdxroyydcbbjg'
    MAIL_DEFAULT_SENDER = '975336710@qq.com'

    # upload limit 20M
    MAX_CONTENT_LENGTH = 20000000
