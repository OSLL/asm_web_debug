from app.core.utils.debug_commands import DebugCommands

class Config(object):
    HOST = '0.0.0.0'
    PORT = "5000"
    SERVER_NAME = "{}:{}".format(HOST, PORT)
    DEBUG_COMMANDS = DebugCommands


class DeployConfig(Config):
    DEBUG = False


class DefaultConfig(Config):
    DEBUG = True
