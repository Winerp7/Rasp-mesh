from master import MasterNode
from slave import SlaveNode
import os
from os.path import dirname, join
from dotenv import load_dotenv
from utils import string_to_bool

if __name__ == '__main__':
    dotenv_path = join(dirname(dirname(__file__)), 'variables.env')
    load_dotenv(dotenv_path)

    is_master = string_to_bool(os.environ.get('ISMASTER'))

    if is_master:
        master = MasterNode()
        master.run()
    else:
        slave = SlaveNode()
        slave.run()