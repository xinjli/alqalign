import logging
from pathlib import Path
import json
from argparse import Namespace
import yaml

#logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('alqalign')

root_path=Path(__file__).absolute().parent
data_path=root_path/'data'
model_path =  data_path / 'model'

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def read_config(config_name_or_path, overwrite_config=None):
    assert isinstance(config_name_or_path, str) or isinstance(config_name_or_path, Path), config_name_or_path+' is not valid'

    if isinstance(config_name_or_path, Path) or config_name_or_path.endswith('config.yml'):
        # load utterances from a yaml file
        config_dict = yaml.load(open(str(config_name_or_path)), Loader=yaml.FullLoader)

    else:
        # load preset config from config trunk
        config_yml = config_name_or_path + '.yml'
        config_path = data_path / 'config' / config_yml

        assert config_path.exists(), f"{config_path} does not exist"
        config_dict = yaml.load(open(str(config_path)), Loader=yaml.FullLoader)

    if overwrite_config is not None:
        for k,v in overwrite_config.items():
            if k not in config_dict:
                print('WARNING: ', k, ' not found !')
                config_dict[k] = v
            else:
                print("overwriting ", config_dict[k], ' --> ', v)
                config_dict[k] = v

    args = dotdict(config_dict)

    return args
