import ConfigParser
import logging


class ConfigProcessor:
    def __init__(self):
        pass

    @staticmethod
    def get_config_section_map(Config, section):
        tmp = {}
        options = Config.options(section)
        for option in options:
            try:
                tmp[option] = Config.get(section, option)
                if tmp[option] == -1:
                    logging.info("skip: %s" % option)
            except:
                logging.info("exception on %s!" % option)
                tmp[option] = None
        return tmp

    @staticmethod
    def get_sections(config_file):
        Config = ConfigParser.ConfigParser()
        Config.read(config_file)
        return [Config, Config.sections()]