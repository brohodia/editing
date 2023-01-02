import numpy as np
import pandas as pd
import unittest
import pytest
import test_cases.helpers as test_hlp
from algorithms.unit_test.helpers import Util
import algorithms.helpers as hlp
import libraries.helper_functions.algorithms.dotdict as lib


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

@pytest.fixture(scope="module", name="hxd")
def load_hxd() -> lib.DotDict:
    raw = Util.load_json("test_cases/test_data.json")

    hxd = lib.DotDict(raw)
    yield hxd

keys = ["groupId","operator","aircraftTypeSummary","aircraftUse",
        "ageGroup","operatorCountry","aircraftCt","selectedPerCraftExpDep","selectedPerCraftAvgSeats","selectedPerCraftUsedAv"]

rename_dict = {
      
    }

@pytest.fixture(scope="module", name="run_data")
def run_data(hxd):
    """Runs through the module with mockHX object"""
    scen_inputs = hxd.insuredInterest
    nes_inputs = hxd.lossHistory


def test_convert_single_layer_list_to_dataframe(hxd, run_data):
    in_input = hxd.insuredInterest
    test_df = hlp.convert_single_layer_list_to_dataframe(
        list_obj = in_input.aircraftGroupAirlines,
        keys=keys,
        rename_dict=rename_dict)

    assert type(test_df) == pd.DataFrame


agg_exp_keys = ["lossHistoryYear"]
claim_segment_keys = ["claimSegmentCd",
        "indemnityIncurredAmt","aircraftCt",
        "cdf","trend",
        "indemnityIncurredAmtAttrUlt","lossCostAttr"]

def test_convert_nested_list_to_dataframe(hxd, run_data):
    nested_input = hxd.lossHistory
    test_df = hlp.convert_nested_list_to_dataframe(
       parent_list=nested_input.aggExperience,
        child_list="claimSegment",
        parent_keys = agg_exp_keys,
        child_keys = claim_segment_keys)

    assert type(test_df) == pd.DataFrame


def test_agg_list() -> None:
    test_dict = lib.DotDict(
        {
            "result": {},
            "list": [{"ratingResult": {"test_value": 5}}, {"ratingResult": {"test_value": 6}}],
        }
    )

    hlp.agg_list(parent_obj=test_dict.result, list_obj=test_dict.list, keys=["test_value"])

    assert test_dict.result.test_value == 11

groupby_fields = ["operator","aircraftTypeSummary","aircraftUse","ageGroup","operatorCountry"]
agg_fields = ["aircraftCt","selectedPerCraftExpDep","selectedPerCraftAvgSeats","selectedPerCraftUsedAv"]
keys = groupby_fields + agg_fields

def aggregate(
    final_df: pd.DataFrame
    ) -> pd.DataFrame:
    
    # Aggregate
    group_df = (final_df
        .groupby(by=groupby_fields)
        [agg_fields].sum()
        .reset_index()
    )

def test_set_dataframe_to_hxd(hxd,run_data):

    # Set paths
    ins_int = hxd.insuredInterest

    # Get cirium df
    final_df = hlp.convert_single_layer_list_to_dataframe(
        list_obj=ins_int.aircraftGroupAirlines,
        keys=keys)

    group_df = aggregate(final_df=final_df)

    # Populate HXD
    temp_dict = hlp.set_dataframe_to_hxd(
        hxd_object = ins_int,
        child="aircraftGroupAirlines",
        df=final_df)
    
def calc(
    ins_int,
    final_df: pd.DataFrame
) -> dict:

    group_df = (final_df
        .groupby(by=groupby_fields)
        [agg_fields].sum()
        .reset_index()
    )
    return group_df.to_dict()

def test_set_hxd_values_from_dict(hxd,run_data):

    # Set pathsd
    ins_int = hxd.insuredInterest

    # Get cirium df
    final_df = hlp.convert_single_layer_list_to_dataframe(
        list_obj=ins_int.aircraftGroupAirlines,
        keys=keys)

    group_df_dict = calc(ins_int=ins_int, final_df=final_df)

    # Populate dict
    temp_dict = hlp.set_hxd_values_from_dict(
        hxd_object = ins_int.aircraftGroupAirlines,
        input_dict=group_df_dict)  