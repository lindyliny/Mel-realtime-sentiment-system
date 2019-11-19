class Config:
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    database = '../data.db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(database)


class TwitterConfig:
    Customer_Key = 'tp1EesbrZvb6noSIDzsZWU3en'
    Customer_Secret = 'uOBlE9fQ4SAGjScelzOHYnvtf6rYRfCi9gQz0Ra3mBILZ3tiEK'
    Token_Key = '459168227-UGLJuuC88ApvuX718ePVi3tP7mJNA6c6XMsVeMzV'
    Token_Secret = 'Qlmk5IyGr0kWvTyvEfOSJU3RGME7URnLgRiWoJNoEISpH'
    Proxy = '127.0.0.1:1087'


config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
