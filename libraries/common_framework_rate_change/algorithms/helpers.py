import hx
import datetime
# from libraries.common_framework_rate_change.algorithms.rate_walk import set_absolute_fields,set_percentage_fields


scenarios = [
    "expiring",
    "renewalStructure",
    "renewalExposure",
    "renewalLossHistory",
    "renewalSubjectiveModifiers",
    "quote"
]


class DotDict(dict):     
    '''
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
    '''
         
    def __init__(self, dct):
        # Convert initial object to a dictionary
        # NOTE: Won't work for lists but have got around that by calling it on the list elements throughout the code
        temp_dct = dict(dct)

        # Loop through all items in dict
        for key, value in temp_dct.items():

            # Deal with overrides separately as overrides can't be converted to a dict
            if hasattr(value,"is_overridden"):
                self[key] = value.selected
                continue

            # Allow for lists
            if hasattr(value,"append"):

                # If there are list elements then run LC
                if len(value) > 0:
                    self[key] = [DotDict(vals) for vals in value]
                    continue
                else:
                    # If 0 elements then assign to an empty list otherwise it retains a HXD reference
                    self[key] = []
                    continue

            # If it is a HXD.structure then run DotDict() on that object
            elif value is not None and not isinstance(value,(float,int,str,bool,datetime.date)):
                value = DotDict(value)

            # Assign the value to the key
            self[key] = value

    # These allow us to use `.` notation
    def __getattr__(*args):         
        val = dict.get(*args)         
        return DotDict(val) if type(val) is dict else val    

    __setattr__ = dict.__setitem__     
    __delattr__ = dict.__delitem__ 
        
        
def set_scenario_data(
    hxd,
    scen_nm,
    temp_scen_output):
    '''
    Description: 
    Setups the data for a given scenario:
        - expiring / quote - returns the HXD object unchanged
        - Other scenarios - takes some nodes from expiring and others from renewal

    Parameters:
        - hxd: hxd data object - hx.hxd
        - scen_nm - name of the scenario that we are running
        - temp_scen_output - dummy output shell that we use for the scenarios

    Output:
        - For a given scenario return ratingInput and ratingOutput
        - These will be HXD objects with intellisense for expiring and quote
        - These will be DotDict objects without intellisense for other scenarios
    '''

    # If expiring and renewal then return that output
    if scen_nm in ["expiring", "quote"]:
        return getattr(hxd, scen_nm)

    else:
        # Otherwise adjust the inputs to be a mixture of expiring and renewal
        scen_inputs = DotDict(hxd.expiring.ratingInput)
        curr_inputs = DotDict(hxd.quote.ratingInput)

        # All scenarios have these structures changed
        scen_inputs.scenarioDetails = curr_inputs.scenarioDetails
        scen_inputs.policyStructure = curr_inputs.policyStructure

        # Change remaining elements
        if scen_nm in ["renewalExposure","renewalLossHistory","renewalSubjectiveModifiers"]:
            scen_inputs.insuredInterest = curr_inputs.insuredInterest

        if scen_nm in ["renewalLossHistory","renewalSubjectiveModifiers"]:
            scen_inputs.lossHistory = curr_inputs.lossHistory

        if scen_nm == "renewalSubjectiveModifiers":
            scen_inputs.subjectiveModifier = curr_inputs.subjectiveModifier

        # Key change here
        scen = DotDict({"ratingInput": {},"ratingOutput": {}})
        scen['ratingInput'] = scen_inputs
        scen['ratingOutput'] = temp_scen_output
        
        return scen


def populate_scenario_results(
    scen_outputs,
    scenario_results,
    scen_nm):
    '''
    Store in a temp object the scenario technical premium for rate walk calc
    Can't be in hxd.quote as the scenario might not have been run yet
    therefore policyStructure doesn't have the required layers
    '''

    # Quote level
    quote_output = get_tech_prem(scen_outputs.ratingResult,scen_nm)
    scenario_results["rateWalk"].append(quote_output)

    # Layer level
    for id_layer, layer in enumerate(scen_outputs.policyStructure):
        layer_output = get_tech_prem(layer.ratingResult,scen_nm)

        scenario_results["policyStructure"][id_layer]["rateWalk"].append(layer_output)

        # TODO: need to loop over coverage here as well
        # for id_cov, cov in enumerate(layer)


def get_tech_prem(rr,scen_nm):
    '''Setup the required output from a scenario'''

    return {
        "resultSetTypeNm": scen_nm,
        "ratingResult": {
            "technicalPremium": rr.technicalPremium
        }
    }


def temp_scen_output(hxd):
    '''rate walk scenarios require an empty ratingOutput shell'''
    return DotDict(hxd.quote.ratingOutput)


def get_scenario_results_dict(hxd):
    '''
    Ensure that rateWalk has as many layers as policyStructure
    Create dict to store the technical premium for each scenario
    Can't assign to hxd.quote.ratingOutput.policyStructure[x].rateWalk 
    when looping through scenarios as those layers don't exist until the qte scenario is run
    '''

    # Set path
    qte = hxd.quote

    # Get number of layers in PS
    scenario_results = {
        "rateWalk": [],
        "policyStructure": [{
            "layerId": layer.layerId,
            "rateWalk": []
        } for layer in qte.ratingInput.policyStructure]
    }

    return scenario_results


def agg_list(
    parent_obj,
    list_obj,
    keys):
    '''Sums up keys from a nested layer to a higher layer'''

    # NOTE: doesn't allow for AIG share - loadings module does
    for key in keys:
        setattr(parent_obj,key,sum([getattr(el.ratingResult,key) for el in list_obj]))

