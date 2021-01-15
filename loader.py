#!/usr/bin/env python
import os
import yaml


def load_params():
    src_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    rel_path = '/config/'
    filename = 'config.yaml'
    with open(src_dir+rel_path+filename, 'r') as stream:
        config = yaml.safe_load(stream)
    return config
