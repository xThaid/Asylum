import configparser
config = configparser.ConfigParser()
config.read("../config.ini")


class Config(object):
    SECRET_KEY = config['SECURITY']['SecretKey']
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + config['DATABASE']['Path']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
