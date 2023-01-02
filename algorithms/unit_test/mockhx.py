from algorithms.unit_test.parameter_tables_util import ParameterTable
from algorithms.unit_test.helpers import Util
import os

class DummyDecorator(object):
    def __call__(self, func):
        pass

class dummy:
    pass

def print_nothing(self):
    print('nothing')    

def init_mockhx():
    hxmock = Hxdummy()
    hxmock.task = print_nothing
    return hxmock 
   
class Hxdummy:
    '''Dummy class for loading parameter tables when executing rating algorithms as part of pytest unit and functional tests'''

    def __init__ (self):
        #Init params - empty class
        self.params = Hxparams()

        # NOTE: required to run through code
        self.Hxd = None
        self.rating = None

        #Open parameter table schema from parameter tables folder
        curr_dir = Util.get_abs_path()
        folder = os.path.join(curr_dir, '..','..','parameter_tables',)
        json_def_path = os.path.join(folder,'parameter_tables_schema.json')
        paramdef = Util.load_json(json_def_path)

        #Iterate through schema, load from csv folded using schema structure for each parameter table        
        for key, val in paramdef.items():
            setattr(self.params, key, ParameterTable.from_csv(f"{folder}/{key}.csv", schema=val).df())

    # Dummy to handle decorator function
    def task(func):
        def wrapper():
            return func()

        return wrapper


class Hxparams:
    def __int__(self):    
        print('created')