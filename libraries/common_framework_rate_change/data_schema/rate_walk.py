import hx_data_schema as hx
from libraries.common_framework_rate_change.data_schema.helpers import thousands_format,percent_format
from libraries.common_framework_rate_change.data_schema.rating_results import rating_results_ds

# Define all keys required
rating_calc_fields = [
    "isAtShare",
    "excessProfit",
    "techPremLossCostExposure",
    "techPremLossCostExperience",
    "techPremLossCost",
    "techPremCommission",
    "techPremExpenses",
    "techPremReinsurance",
    "techPremGrossProfitLoading",
    "techPremLossRatio",
    "techPremCommissionRatio",
    "techPremExpenseRatio",
    "techPremGrossProfitLoadingRatio",
    "experienceModificationFactor",
    "termAdjustmentFactor",
    "impliedLossRatio",
    "impliedCombinedRatio",
    "modifiedLossCostExposure",
    "modifiedLossCostExperience",
    "modifiedLossCost",
    "modifiedPremium",
    "subjectiveModifierFactor",
    "subjectiveModifierImpact",
    "modifiedRateAdequacy",
    "targetPremium",
    "targetToTechPremRatio",
    "targetRateAdequacy"
]

chg_keys = [
    "actualPremiumChgAmt",
    "technicalPremiumChgAmt",
    "aggregateExposureChgAmt",
    "mainLimitChgAmt",
    "rateAdequacyChgAmt",
    "rateLevelChgAmt",
    "actualPremiumChgPct",
    "technicalPremiumChgPct",
    "aggregateExposureChgPct",
    "mainLimitChgPct",
    "rateAdequacyChgPct",
    "rateOnExposureChgPct",
    "rateOnLimitChgPct",
    "rateLevelChgPct"
]

# Interim - Rate Walk
core_rw_fields = [
    "actualPremium",
    "aggregateExposure",
    "mainLimit",
    "technicalPremium",
    "technicalRateAdequacy",
    "rateOnExposure",
    "rateOnLimit",
]

## Define fields required
rw_fields = core_rw_fields + chg_keys
rating_fields = rating_calc_fields + core_rw_fields


def rate_walk_interim():
    '''
    Nodes required for the rate walk calculation
    These are defined as structures rather than lists because:
        - There wil be a fixed number of scenarios for each LOB
        - Structures can be aligned together easily in the UI whereas lists can't be transposed so avoids using the interim node
    Might need a different set of scenarios for LOB rater
    '''

    # Don't need rate level change for some scenarios
    rw_fields_wo_rate_level_chg = rw_fields.copy()
    rw_fields_wo_rate_level_chg.remove("rateLevelChgPct")


    # Some keys will never be populated for expiring, absolute or percentage
    # So remove to make UI cleaner
    dict ={
        "rateWalkOutput": hx.Structure(view={"label": "Rate Walk Output"}, children={
            **rate_walk_scen("expiring","Expiring",keep_keys=core_rw_fields),
            **rate_walk_scen("renewalStructure","Renewal Structure",keep_keys=rw_fields_wo_rate_level_chg),
            **rate_walk_scen("renewalExposure","Renewal Exposure",keep_keys=rw_fields_wo_rate_level_chg),
            **rate_walk_scen("renewalLossHistory","Renewal Loss History",keep_keys=rw_fields_wo_rate_level_chg),
            **rate_walk_scen("renewalSubjectiveModifiers","Renewal SRM",keep_keys=rw_fields_wo_rate_level_chg),
            **rate_walk_scen("rate","Rate",keep_keys=rw_fields_wo_rate_level_chg),
            **rate_walk_scen("quote","Renewal",keep_keys=rw_fields),
            **rate_walk_scen("absolute","Absolute",keep_keys=core_rw_fields),
            **rate_walk_scen("percentage","Percentage",format=percent_format(2),keep_keys=core_rw_fields),
        }),
    }

    return dict


def rate_walk_scen(
    scenario: str,
    scenario_label: str,
    keep_keys: list = [],
    format = thousands_format(0)):
    '''Wrapper for a single scenario'''

    dict ={
        scenario : hx.Structure(view={"label": scenario_label}, children={
            **rating_results_ds(keep_keys=keep_keys,format=format)
        }),
    }

    return dict


def rate_walk_rating_output():
    '''Structure required for rating output'''

    dict ={
        "rateWalk": hx.List(mode="output", children={
            "resultSetTypeNm": hx.Str(mode="output", view={"label": "Result Set Type Name"}),
            "resultSetTypeCd": hx.Str(mode="output", view={"label": "Result Set Type Code"}),
            **rating_results_ds(
                format=thousands_format(2),
                keep_keys=rw_fields)
        }),
    }

    return dict
