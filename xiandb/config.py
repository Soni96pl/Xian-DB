import os
import yaml


try:
    with open(os.path.expanduser('~') + '/xian/config.yml', 'r') as cfg_file:
        cfg = yaml.load(cfg_file)
except IOError:
    print "Couldn't find a valid configuration file in ~/xian/config.yml"
    print "Please refer to README.rst"

mongodb = cfg['mongodb']
