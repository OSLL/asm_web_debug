from app.core.utils.debug_commands import DebugCommands

class Config(object):
    HOST = '0.0.0.0'
    PORT = '5000'
    TEMPLATE_FOLDER ='app/templates'
    STATIC_FOLDER = 'app/static'
    CODES_FOLDER = '../codes/'
    BUILD_FILE = '../DEBUG'
    DEBUG_COMMANDS = DebugCommands
    ARCHS = ['x86_64', 'ARM','AVR']
    MONGODB_SETTINGS = {
        'db': 'database',
        'host': '127.0.0.1',
        'port': 27017
    }
    SECRET_KEY = 'super secret key'
    DEBUG = True
    ANON_ACCESS = False
    ANON_USER_ID = 'a334-4276-8b34'
    LTI_CONSUMERS = {
        'secretconsumerkey': 'supersecretconsumersecret'
    }
    USER_ROLES = ['user', 'teacher', 'admin']

class DeployConfig(Config):
    MONGODB_SETTINGS = {
        'db': 'database',
        'host': 'mongo',
        'port': 27017
    }
    DEBUG = False


class TestConfig(DeployConfig):
    ANON_ACCESS = True
    DEBUG = True


class DefaultConfig(Config):
    pass


class ConfigManager:
        
    config = {
        'default': DefaultConfig,
        'deploy': DeployConfig,
        'test': TestConfig
    }

    @classmethod
    def get_config(cls, config_type):
        if config_type in cls.config:
            print(f"Using {config_type} config")
            return cls.config[config_type]
        else:
            print(f"No such config: '{config_type}'. Using default config")
            return cls.config['default']
