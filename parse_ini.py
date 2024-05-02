import configparser

config = configparser.ConfigParser()
config.read('config.ini')

converted_data = {}

def parse_config_file():
    for map_name in config.sections():
        section_data = {}
        for variables in config[map_name]:
            section_data[variables] = config[map_name][variables]
        converted_data[map_name] = section_data
    return converted_data
