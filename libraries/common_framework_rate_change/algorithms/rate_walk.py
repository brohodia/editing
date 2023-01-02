import hx
from libraries.common_framework_rate_change.algorithms.helpers import DotDict



# Constants used in multiple functions
full_amounts = ["actualPremium","technicalPremium","aggregateExposure","mainLimit"]
metrics = ["technicalRateAdequacy","rateOnExposure","rateOnLimit"]
abs_pct_fields = full_amounts + metrics
change_pct_fields = [field for field in abs_pct_fields if field not in ["actualPremium","technicalPremium","technicalRateAdequacy"]]


def rate_walk_wrapper(
    hxd,
    scenario_results,
    scenarios,
    layer_level = True):
    '''
    This is the function that raters need to call
    Carries out rate walk at a total and a layer level
    '''

    # Set paths
    exp_out = hxd.expiring.ratingOutput
    qte_out = hxd.quote.ratingOutput

    # Total
    set_rate_walk_inputs(
        exp_rr=exp_out.ratingResult,
        qte_rr=qte_out.ratingResult,
        rw=qte_out.rateWalk,
        scenario_results=scenario_results["rateWalk"],
        scenarios=scenarios
    )
    
    rate_walk(qte_out.rateWalk,scenarios)

    # Loop over layers if required
    if layer_level:
        for id,layer in enumerate(qte_out.policyStructure):
            set_rate_walk_inputs(
                exp_rr=exp_out.policyStructure[id].ratingResult,
                qte_rr=qte_out.policyStructure[id].ratingResult,
                rw=layer.rateWalk,
                scenario_results=scenario_results["policyStructure"][id]["rateWalk"],
                scenarios=scenarios
            )
        
            rate_walk(layer.rateWalk,scenarios)


def set_rate_walk_inputs(
    exp_rr,
    qte_rr,
    rw,
    scenario_results,
    scenarios):
    '''Assigns data for the rate walk calculation'''

    # Assign scenario values
    for scen_nm in scenarios:
        temp_dict = get_scenario(scen_nm=scen_nm,obj=scenario_results)

        rate_walk_actual_prem(exp_rr,qte_rr,temp_dict,scen_nm)
        rate_walk_main_limit(exp_rr,qte_rr,temp_dict,scen_nm)
        rate_walk_exposure(exp_rr,qte_rr,temp_dict,scen_nm)

        # Assign back to HXD
        rw.append(temp_dict)

        # Allow for rate and percentage field - identical to quote
        if scen_nm == "quote":
            temp_dict["resultSetTypeNm"] = "rate"
            rw.append(temp_dict)


def rate_walk_actual_prem(
    exp_out,
    qte_out,
    rw_scen,
    scen_nm):
    '''Actual premium - intermediate scenarios are calculated via rate adequacy %'''

    rw_scen["ratingResult"]["actualPremium"] = exp_out.actualPremium if scen_nm == "expiring" else qte_out.actualPremium


def rate_walk_main_limit(
    exp_out,
    qte_out,
    rw_scen,
    scen_nm):
    '''Main limit - either qte or expiring limit'''

    rw_scen["ratingResult"]["mainLimit"] = exp_out.mainLimit if scen_nm in ["expiring","expiringLatestRater"] else qte_out.mainLimit


def rate_walk_exposure(
    exp_out,
    qte_out,
    rw_scen,
    scen_nm):
    '''Aggregate Exposure - either qte or expiring'''

    rw_scen["ratingResult"]["aggregateExposure"] = exp_out.aggregateExposure if scen_nm in ["expiring","expiringLatestRater","renewalStructure"] else qte_out.aggregateExposure


def get_scenario(scen_nm,obj):
    '''Allow for either dictionary or HXD object'''
    try:
        return [scen for scen in obj if scen["resultSetTypeNm"] == scen_nm][0]
    except:
        return [scen for scen in obj if scen.resultSetTypeNm == scen_nm][0]



def rate_walk(rw,scenarios: str):
    """Calculate rate walk for all scenarios"""

    # Set paths
    rw_exp = get_scenario(scen_nm="expiring",obj=rw).ratingResult
    rw_qte = get_scenario(scen_nm="quote",obj=rw).ratingResult

    # Scenario mappings - what to compare each scenario to
    rw_compare = {
        "renewalStructure": "expiring",
        "renewalExposure": "renewalStructure",
        "renewalLossHistory": "renewalExposure",
        "renewalSubjectiveModifiers": "renewalLossHistory",
        "rate": "renewalSubjectiveModifiers",
        "quote": "expiring"
    }

    # Calculate metrics for expiring - rate adequacy used for other scenarios
    calculate_metrics(rw_exp)

    # Calculate metrics for each scenario
    set_scenario_fields(scenarios=scenarios,rw=rw,rw_compare=rw_compare)

    # Calculate rate change
    # NOTE: likely to be bespoke by LOB so refine after calling func
    set_rate_change(rw=rw)


def get_target_source(target_str,source_str,key):
    '''Helper to extract required keys from structures'''
    target = getattr(target_str,key)
    source = getattr(source_str,key)

    return target, source


def calculate_metrics(source_str):
    '''
    Calculates Metric   
    parameter: 
       source_str: source structure of hxd data schema object
    '''
    
    source_str.technicalRateAdequacy = divide(numerator=source_str.actualPremium, denom=source_str.technicalPremium)
    source_str.rateOnExposure = divide(numerator=source_str.actualPremium, denom=source_str.aggregateExposure)
    source_str.rateOnLimit = divide(numerator=source_str.actualPremium, denom=source_str.mainLimit)


def set_change_percentage(target_str,source_str):
    '''
    Calculate change percentages 
    parameters: 
        target_str: target structure of hxd data schema object
        source_str: source structure of hxd data schema object
    '''
    target_str.actualPremiumChgPct = divide(numerator=target_str.actualPremiumChgAmt,denom=source_str.actualPremium)
    target_str.technicalPremiumChgPct = divide(numerator=target_str.technicalPremiumChgAmt,denom=source_str.technicalPremium)
    target_str.rateAdequacyChgPct = get_percentage(numerator=target_str.technicalRateAdequacy,denom=source_str.technicalRateAdequacy)

    for key in change_pct_fields:
        target,source = get_target_source(target_str=target_str,source_str=source_str,key=key)
        setattr(target_str,f"{key}ChgPct",get_percentage(numerator=target,denom=source))


def set_change_amounts(target_str,source_str):
    '''
    function to calculate change amounts   
    parameters: 
        target_str: target structure of hxd data schema object
        source_str: source structure of hxd data schema object
    '''

    for key in full_amounts:
        target,source = get_target_source(target_str=target_str,source_str=source_str,key=key)
        setattr(target_str,f"{key}ChgAmt",safe_subtract(val1=target,val2=source))


def set_scenario_fields(scenarios,rw,rw_compare):
    '''Calculates the metrics for each scenario of the rate walk'''

    # Set paths
    rw_exp = get_scenario(scen_nm="expiring",obj=rw).ratingResult
    rw_qte = get_scenario(scen_nm="quote",obj=rw).ratingResult
    
    # Remove expiring from scenarios
    scen_subset = [scen_nm for scen_nm in scenarios if scen_nm != "expiring"]
    scen_subset = scen_subset + ["rate"]

    # For each scenario: calculate the metrics, change amounts and change percentages
    for scen_nm in scen_subset:
        rw_scen = get_scenario(scen_nm=scen_nm,obj=rw).ratingResult
        rw_comp = get_scenario(scen_nm=rw_compare[scen_nm],obj=rw).ratingResult

        # Set the actual premium
        if scen_nm not in ["rate","quote"]:
            rw_scen.actualPremium = rw_scen.technicalPremium * rw_exp.technicalRateAdequacy if rw_exp.technicalRateAdequacy is not None else 0
        
        # Create metrics for each scenario
        calculate_metrics(rw_scen)

        # Calculate change percentages and amounts compared to other scenario
        set_change_amounts(rw_scen,rw_comp)
        set_change_percentage(rw_scen,rw_comp)



def set_rate_change(rw):
    '''Sets rate change calculation'''

    rw_exp = get_scenario(scen_nm="expiring",obj=rw).ratingResult
    rw_qte = get_scenario(scen_nm="quote",obj=rw).ratingResult
    rw_rs = get_scenario(scen_nm="renewalStructure",obj=rw).ratingResult

    rate_level_chg_denom = + \
        (1 + rw_qte.aggregateExposureChgPct if rw_qte.aggregateExposureChgPct is not None else 0) * \
        (1 + rw_rs.technicalPremiumChgPct if rw_rs.technicalPremiumChgPct is not None else 0) * \
        rw_exp.actualPremium

    rw_qte.rateLevelChgPct = rw_qte.actualPremium / rate_level_chg_denom - 1 if rate_level_chg_denom != 0 else 0


def set_absolute_fields(rw_qte,rw_exp,rw_abs):
    '''Set absolute rate walk scenario fields'''

    for key in abs_pct_fields:
        target,source = get_target_source(target_str=rw_qte,source_str=rw_exp,key=key)

        setattr(rw_abs,key,safe_subtract(val1=target,val2=source))


def set_percentage_fields(rw_qte,rw_exp,rw_pct):
    '''Set percentage rate walk scenario fields'''
    
    for key in abs_pct_fields:
        target,source = get_target_source(target_str=rw_qte,source_str=rw_exp,key=key)

        val = get_percentage(numerator=target,denom=source)

        setattr(rw_pct,key,val)




# Used in rate walk
def divide(numerator: float,
           denom: float):
    """safe divide that checks for non-zero denomninator"""
    
    if numerator is None or denom is None:
        return None
    elif denom != 0:
        return numerator / denom
    else: 
        return None


def get_percentage(numerator: float,
           denom: float):
    """Get percentage checking for nones"""
    
    val = divide(numerator=numerator,denom=denom)

    if val is None:
        return None
    else:
        return val - 1

def safe_subtract(val1: float,
           val2: float):
    """Subtract fields allowing for nones"""
    
    if val1 is None or val2 is None:
        return None
    else:
        return val1 - val2




def set_interim_rate_walk_outputs(hxd):
    '''Set the outputs in quote/interim/rateWalkOutput based on chosen level of granularity'''

    # Set paths
    qte = hxd.quote
    rw_out = qte.interim.uiTables.rateWalkOutput

    ro = qte.ratingOutput
    globs = qte.interim.uiControls.rateWalk

    # Get the required input structure
    if globs.results_granularity == "quote":
        rw_in = ro.rateWalk
    else:
        if globs.output_layer_selection is None:
            return None
            
        rw_in = ro.policyStructure[globs.output_layer_selection].rateWalk


    for scen in rw_in:
        scen_nm = scen.resultSetTypeNm
        rw_out_scen = getattr(rw_out,scen_nm)

        setattr(rw_out_scen,"ratingResult",scen.ratingResult)
            

    # Set absolute and percentage fields
    rw_pct = rw_out.percentage.ratingResult
    rw_abs = rw_out.absolute.ratingResult
    rw_qte = rw_out.quote.ratingResult
    rw_exp = rw_out.expiring.ratingResult

    set_absolute_fields(rw_qte=rw_qte,rw_exp=rw_exp,rw_abs=rw_abs)
    set_percentage_fields(rw_qte=rw_qte,rw_exp=rw_exp,rw_pct=rw_pct)
