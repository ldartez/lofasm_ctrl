# routines to read lofasm.cfg


import os, sys

global config
config = {}

try:
    # first look for $HOME/.lofasm/lofasm.cfg
    DEFAULT_CONFIG = os.path.join(os.environ['HOME'], '.lofasm',
                                  'lofasm.cfg')
except KeyError:
    print "Please set environment variable $HOME."
    sys.exit(-1)

if not os.path.exists(DEFAULT_CONFIG):
    print "The default config path does not exist: {}".format(DEFAULT_CONFIG)
    print '''Either put the config file in that location, set DEFAULT_CONFIG
    to the path of your config file, or simply manage your own config dictionary
    when using the config submodule.'''
    sys.stdout.flush()

def read_config(cfg_file=DEFAULT_CONFIG, cfg_dict=config):
    '''parse cfg file
    '''

    with open(cfg_file, 'r') as cfg:
        lines = cfg.readlines()

    #prune comments
    lines = [l for l in lines if not l.startswith('#')]
    for i in range(len(lines)):
        line = lines[i]
        if line.startswith('#'):
            pass
        try:
            k, v = line.split()
        except ValueError:
            # skip lines that are improperly formatted
            print "skipping line {} due to improper formatting".format(i+1)
            sys.stdout.flush()

        cfg_dict[k] = v
