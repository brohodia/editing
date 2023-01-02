import hx_data_schema as hx

def thousands_format(mantissa=0):
    return {"thousandSeparated": True, "mantissa": mantissa}


def percent_format(mantissa=0):
    return {"output":"percent", "mantissa":mantissa}


def no_comma(mantissa=0):
    return {"thousandSeparated": False, "mantissa": mantissa}


def read_only():
    return {"read_only": {"read_only": True}}


def scenario_ds(
    scenario,
    scenario_label,
    rating_input,
    rating_output,
    interim_scen):
    '''Wrapper to write the I/O structure for a single scenario'''
    dict = {
        scenario : hx.Structure(view={"label": scenario_label}, children={
            **rating_input(),
            **rating_output(),
            **interim_scen(scenario),
        }),
    }

    return dict
