import hx_data_schema as hx
from libraries.common_framework_rate_change.data_schema.helpers import thousands_format,percent_format

# Example
# rating_results_ds(
#     thousands_format(2),
#     lob_specific={"test": 1},
#     keep_keys=["rateOnExposureChgPct","rateLevelChgPct"]
# )

def rating_results_ds(
    format,
    keep_keys = [],
    lob_specific = {}):
    '''Rating result - used for rate walk as well
    Allows you to add in custom fields and remove keys that aren't needed
    '''
    temp_dict ={
        "ratingResult" : hx.Structure(view={"label": "Rating Result"}, children={
            # Actuals
            "isAtShare": hx.Bool(mode="output",  view={"label": "Is at Share or at 100%"}),
            "actualPremium": hx.Float(mode="output",  view={"label": "Actual Premium","format": format}),
            "aggregateExposure": hx.Float(mode="output", view={"label": "Aggregate Exposure","format": format}),
            "mainLimit": hx.Float(mode="output", view={"label": "Main Limit","format": format}),
            "rateOnExposure": hx.Float(mode="output", view={"label": "Rate On Exposure","format": percent_format(2)}),
            "rateOnLimit": hx.Float(mode="output", view={"label": "Rate On Limit","format": percent_format(2)}),
            "excessProfit": hx.Float(mode="output", view={"label": "Excess Profit","format": thousands_format(2)}),

            # Technical Premium
            "technicalPremium": hx.Float(mode="output",  view={"label": "Technical Premium","format": format}),
            "techPremLossCostExposure": hx.Float(mode="output", view={"label": "Technical Loss Cost - Exposure","format": thousands_format(2)}),
            "techPremLossCostExperience": hx.Float(mode="output", view={"label": "Technical Loss Cost - Experience","format": thousands_format(2)}),
            "techPremLossCost": hx.Float(mode="output", view={"label": "Technical Loss Cost - Blended","format": thousands_format(2)}),
            "techPremCommission": hx.Float(mode="output",  view={"label": "Technical Premium - Commission","format": thousands_format(2)}),
            "techPremExpenses": hx.Float(mode="output",  view={"label": "Technical Premium - Expenses","format": thousands_format(2)}),
            "techPremReinsurance": hx.Float(mode="output",  view={"label": "Technical Premium - Reinsurance","format": thousands_format(2)}),
            "techPremGrossProfitLoading": hx.Float(mode="output",  view={"label": "Technical Premium - Gross Profit Loading","format": thousands_format(2)}),

            # Technical premium metrics
            "techPremLossRatio": hx.Float(mode="output",  view={"label": "Technical Premium - Loss Ratio","format": percent_format(2)}),
            "techPremCommissionRatio": hx.Float(mode="output",  view={"label": "Technical Premium - Commission Ratio","format": percent_format(2)}),
            "techPremExpenseRatio": hx.Float(mode="output",  view={"label": "Technical Premium - Expense Ratio","format": percent_format(2)}),
            "techPremGrossProfitLoadingRatio": hx.Float(mode="output",  view={"label": "Technical Premium - Gross Profit Loading Ratio","format": percent_format(2)}),
            "experienceModificationFactor": hx.Float(mode="output",  view={"label": "Experience Modification Factor"}),
            "termAdjustmentFactor": hx.Float(mode="output",  view={"label": "Term Adjustment Factor"}),
            "technicalRateAdequacy": hx.Float(mode="output", view={"label": "Technical Rate Adequacy","format": percent_format(2)}),
            "impliedLossRatio": hx.Float(mode="output", view={"label": "Implied Loss Ratio","format": percent_format(2)}),
            "impliedCombinedRatio": hx.Float(mode="output", view={"label": "Implied Combined Ratio","format": percent_format(2)}),

            # Modified Premium
            "modifiedLossCostExposure": hx.Float(mode="output", view={"label": "Modified Loss Cost - Exposure","format": thousands_format(2)}),
            "modifiedLossCostExperience": hx.Float(mode="output", view={"label": "Modified Loss Cost - Experience","format": thousands_format(2)}),
            "modifiedLossCost": hx.Float(mode="output", view={"label": "Modified Loss Cost - Blended","format": thousands_format(2)}),
            "modifiedPremium": hx.Float(mode="output",  view={"label": "Modified Premium","format": format}),
            "subjectiveModifierFactor": hx.Float(mode="output",  view={"label": "Subjective Modifer Factor","format": percent_format(2)}),
            "subjectiveModifierImpact": hx.Float(mode="output",  view={"label": "Subjective Modifer Impact","format": percent_format(2)}),
            "modifiedRateAdequacy": hx.Float(mode="output", view={"label": "Modified Rate Adequacy","format": percent_format(2)}),

            # Target premium
            "targetPremium": hx.Float(mode="output",  view={"label": "Target Premium","format": format}),
            "targetToTechPremRatio": hx.Float(mode="output", view={"label": "Technical Premium - Target Premium Ratio","format": percent_format(2)}),
            "targetRateAdequacy": hx.Float(mode="output", view={"label": "Target Rate Adequacy","format": percent_format(2)}),

            # Rate change / walk
            "actualPremiumChgAmt": hx.Float(mode="output", view={"label": "Actual Premium","format": thousands_format(0)}),
            "technicalPremiumChgAmt": hx.Float(mode="output", view={"label": "Technical Premium","format": thousands_format(0)}),
            "aggregateExposureChgAmt": hx.Float(mode="output", view={"label": "Aggregate Exposure","format": thousands_format(0)}),
            "mainLimitChgAmt": hx.Float(mode="output", view={"label": "Main Limit","format": thousands_format(0)}),
            "rateAdequacyChgAmt": hx.Float(mode="output", view={"label": "Rate Adequacy","format": thousands_format(0)}),
            "rateLevelChgAmt": hx.Float(mode="output", view={"label": "Rate Level","format": thousands_format(0)}),

            # Change percentage
            "actualPremiumChgPct": hx.Float(mode="output", view={"label": "Actual Premium","format": percent_format(2)}),
            "technicalPremiumChgPct": hx.Float(mode="output", view={"label": "Technical Premium","format": percent_format(2)}),
            "aggregateExposureChgPct": hx.Float(mode="output", view={"label": "Aggregate Exposure","format": percent_format(2)}),
            "mainLimitChgPct": hx.Float(mode="output", view={"label": "Main Limit","format": percent_format(2)}),
            "rateAdequacyChgPct": hx.Float(mode="output", view={"label": "Rate Adequacy","format": percent_format(2)}),
            "rateOnExposureChgPct": hx.Float(mode="output", view={"label": "Rate on Exposure","format": percent_format(2)}),
            "rateOnLimitChgPct": hx.Float(mode="output", view={"label": "Rate on Limit","format": percent_format(2)}),
            "rateLevelChgPct": hx.Float(mode="output", view={"label": "Rate Level - Change","format": percent_format(2)}),
        })
    }

    # Keep just the keys that we need
    if keep_keys:
        remove_keys = set(temp_dict["ratingResult"].children.keys()) - set(keep_keys)
        
        for remove_key in remove_keys:
            del temp_dict['ratingResult'][remove_key]

    # Append LOB specific info
    temp_dict["ratingResult"].children.update(lob_specific)

    return temp_dict

