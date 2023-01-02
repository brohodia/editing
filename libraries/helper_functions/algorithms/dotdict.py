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

import datetime


# TODO: there is a more up to date version of this - put in utilities common module
class DotDict(dict):
    """
    Purpose:
        - The class removes references to the HXD object allowing us to create a copy of HXD and modify it
        - If references still existed then the underlying HXD object would get updated and we would be overwriting our results
        - It converts HXD ito a dictionary allowing us to use dot notation
    Usage:
        - d = DotDict() or d = DotDict({'val1':'first'})
        - set attributes: d.str1.str2 = 'second' or d['str1']['str2'] = 'second'
        - get attributes: d.str1.str2 or d['str1']['str2']
    Note
        - When instantiated the object is created recursively so that any nested elements are a dictionary
        - Overrides need to be treated separately as they can't be converted to a dictionary
        - Empty lists are set to `{}`
        - Lists are handled via LC converting each element to a dictionary
    """

    def __init__(self, dct):
        # Convert initial object to a dictionary
        # NOTE: Won't work for lists but have got around that by calling it on the list elements throughout the code
        temp_dct = dict(dct)

        # Loop through all items in dict
        for key, value in temp_dct.items():

            # Deal with overrides separately as overrides can't be converted to a dict
            if hasattr(value, "is_overridden"):
                self[key] = value.selected
                continue

            # Allow for lists
            if hasattr(value, "append"):

                # If there are list elements then run LC
                if len(value) > 0:
                    self[key] = [DotDict(vals) for vals in value]
                    continue
                else:
                    # If 0 elements then assign to an empty list otherwise it retains a HXD reference
                    self[key] = []
                    continue

            # If it is a HXD.structure then run DotDict() on that object
            elif value is not None and not isinstance(value, (float, int, str, bool, datetime.date)):
                value = DotDict(value)

            # Assign the value to the key
            self[key] = value

    # These allow us to use `.` notation
    def __getattr__(*args):
        val = dict.get(*args)
        return DotDict(val) if type(val) is dict else val

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
