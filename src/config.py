from app.core.utils.debug_commands import DebugCommands
import os
from os import environ, path

basedir = path.abspath(path.dirname(__file__))

class Config(object):
    HOST = '0.0.0.0'
    PORT = "5000"
    TEMPLATE_FOLDER ='app/templates'
    STATIC_FOLDER = 'app/static'
    SERVER_NAME = "{}:{}".format(HOST, PORT)
    DEBUG_COMMANDS = DebugCommands
    ARCHS = ['x86', 'arm','avr']


class DeployConfig(Config):
    DEBUG = False


class DefaultConfig(Config):
    DEBUG = True


config = {
	'default': DefaultConfig,
	'deploy': DeployConfig,
}
