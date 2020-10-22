#!/usr/bin/env python3
'''
Construct command objects for DUNE DAQ appfwk apps based on moo oschema.
'''

import os
import moo


def default_schema_paths():
    '''
    Return list of default file system paths from which to locate schema files.
    '''
    maybe = [
        ".",
        os.environ.get("MOO_MODULE_PATH"),
        # add more here if we default conventions.
    ]
    return [one for one in maybe if one]


def load_oschema(filename, path=()):
    '''
    Load oschema file as data structure.
    '''
    return moo.io.load(filename, list(path) + default_schema_paths())


def make_otypes(schema):
    '''
    Make Python types from schema structure.
    '''
    ret = dict()
    for one in schema:
        typ = moo.otypes.make_type(**one)
        ret[typ.__module__ + '.' + typ.__name__] = typ
    return ret


def init(queues=(), modules=()):
    '''
    Make an init command object
    '''
    from dunedaq.appfwk import cmd  # must call make_otypes() first
    return cmd.Command(id=cmd.CmdId("init"),
                       data=cmd.Init(queues=queues, modules=modules))
    

def conf(modconf=()):
    from dunedaq.appfwk import cmd  # must call make_otypes() first
    return cmd.Command(id=cmd.CmdId("conf"),
                       data=cmd.AddressedCmds(modconf))

    
