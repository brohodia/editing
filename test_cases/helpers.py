import re
import pandas as pd
import math
from datetime import datetime
import libraries.helper_functions.algorithms.dotdict as lib
from typing import List, Union, Any
from dataclasses import dataclass
from typing import Optional

# Tries to import HX package
try:
    import hx
    test_params = hx.params
    import_type = "standard"

except:
    # If that fails then return mockHX or error
    from algorithms.unit_test.mockhx import *
    try:
        hx = init_mockhx()
        import_type = "mock"
    except:
        print(f"Failed to initialise mock {__file__}")
        
def convert_single_layer_list_to_dataframe(
    list_obj,
    keys = [],
    rename_dict = {}):
    '''Converts a single layer list i.e. where you just want elements from one hxd list object
    To a dataframe
    And keeps required keys and renames them
    '''
    df = pd.DataFrame([dict(list_el) for list_el in list_obj])

    if keys:
        df = df[keys]

    if rename_dict:
        df = df.rename(columns = rename_dict)

    return df



def convert_nested_list_to_dataframe(
    parent_list,
    child_list: str,
    # keys: list = [],
    parent_keys: list = [],
    child_keys: list = [],
    rename_dict = {}):
    '''Converts a nested list to a dataframe e.g. claims experience tables
    This is where you want items from the parent list and the child list
    Keeps required keys and renames them
    '''
    
    # TODO: bugs when the parent and child list have the same name
    # TODO: workaround - would be to implement - child_keys,parent_keys
    # TODO: if the child key also exists in the parent key then append with {child_list}_{child_key}
    temp_list = []
    for parent_el in parent_list:
        for child_el in getattr(parent_el,child_list):

            parent_dict = dict(parent_el)
            parent_dict_subset = {
                key: value
                for key,value in parent_dict.items()
                if key in parent_keys}
            # del parent_dict[child_list]

            # temp_parent_dict = parent_dict.copy()

            child_dict = dict(child_el)
            child_dict_subset = {
                key: value
                for key,value in child_dict.items()
                if key in child_keys}

            temp_child_dict = child_dict_subset.copy()

            # Prefix as {child_list}_{child_key} if the key exists in parent_list
            for common_key in set(parent_keys).intersection(child_keys):
                temp_child_dict.pop(common_key)
                temp_child_dict[f'{child_list}_{common_key}'] = child_dict[common_key]

            # Append together
            parent_dict_subset.update(temp_child_dict)
            temp_list.append(parent_dict_subset)


    df = pd.DataFrame.from_dict(temp_list)

    # if keys:
    #     df = df[keys]

    if rename_dict:
        df = df.rename(columns = rename_dict)

    return df


def set_dataframe_to_hxd(
    hxd_object,
    child: str,
    df: pd.DataFrame
    ) :
    '''Pushes a dtaframe to HXD
    Intermediate rate walk scenarios require a DotDict object to be passed 
    So that we can continue to use the dot notation thorughout code
    '''

    temp_dict = df.to_dict('records')
    setattr(
        hxd_object,
        child,
        [lib.DotDict(record) for record in temp_dict]   
    )

def set_hxd_values_from_dict(
    hxd_object,
    input_dict: dict
    ) :
    '''Sets values to HXD given a dictionary and checks if the keys exists before assignment'''

    for key,value in input_dict.items():
        # When testing in VSCode some nodes / attributes might not be present
        # Hence hasattr will always be FALSE
        # Handled this via try/except but could equally define a parameter as import_type = mock/hx
        try:
            setattr(hxd_object,key,value)
        except:
            if hasattr(hxd_object,key):
                setattr(hxd_object,key,value)

def divide(numerator: float, denom: float):
    """safe divide that checks for non-zero denomninator"""

    if numerator is None or denom is None:
        return None
    elif denom != 0:
        return numerator / denom
    else:
        return None


def set_mult_values(
    values_to_set: List[str],
    obj_to_set,
    obj_to_fetch,
) -> None:
    """set mulitple values for object from an object"""

    for val in values_to_set:
        setattr(obj_to_set, val, getattr(obj_to_fetch, val, None))