def init_mockhx():
    hxmock = Hxdummy()
    hxmock.task = print_nothing
    return hxmock 

try:
    import hx
    test_params = hx.params
    import_type = 'standard'

except:
    # If that fails then return mockHX or error
    from algorithms.unit_test.mockhx import *
    try:
        hx = init_mockhx()
        import_type = 'mock'
    except:
        print(f'Failed to initialise mock {__file__}')