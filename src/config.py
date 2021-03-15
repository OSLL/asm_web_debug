from app.core.utils.debug_commands import DebugCommands


class Config(object):
    HOST = '0.0.0.0'
    PORT = '5000'
    TEMPLATE_FOLDER ='app/templates'
    STATIC_FOLDER = 'app/static'
    CODES_FOLDER = '../codes/'
    DEBUG_COMMANDS = DebugCommands
    ARCHS = ['x86', 'arm','avr']
    MONGO_URL = 'mongodb://mongo:27017/database'
    

class DeployConfig(Config):
    DEBUG = False


class DefaultConfig(Config):
    DEBUG = True


class ConfigManager:
        
    config = {
        'default': DefaultConfig,
        'deploy': DeployConfig,
    }

    @classmethod
    def get_config(cls, config_type):
        if config_type in cls.config:
            print(f"Using {config_type} config")
            return cls.config[config_type]
        else:
            print(f"No such config: '{config_type}'. Using default config")
            return cls.config['default']
