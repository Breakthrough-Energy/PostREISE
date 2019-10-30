zones_to_states = {
    1: 'ME',
    2: 'NH',
    3: 'VT',
    4: 'MA',
    5: 'RI',
    6: 'CT',
    7: 'NY',
    8: 'NY',
    9: 'NJ',
    10: 'PA',
    11: 'PA',
    12: 'DE',
    13: 'MD',
    14: 'VA',
    15: 'VA',
    16: 'NC',
    17: 'NC',
    18: 'SC',
    19: 'GA',
    20: 'GA',
    21: 'FL',
    22: 'FL',
    23: 'FL',
    24: 'AL',
    25: 'MS',
    26: 'TN',
    27: 'KY',
    28: 'WV',
    29: 'OH',
    30: 'OH',
    31: 'MI',
    32: 'MI',
    33: 'IN',
    34: 'IL',
    35: 'IL',
    36: 'WI',
    37: 'MN',
    38: 'MN',
    39: 'IA',
    40: 'MO',
    41: 'MO',
    42: 'AR',
    43: 'LA',
    44: 'TX',
    45: 'TX',
    46: 'NM',
    47: 'OK',
    48: 'KS',
    49: 'NE',
    50: 'SD',
    51: 'ND',
    52: 'MT',
    201: 'WA',
    202: 'OR',
    203: 'CA',
    204: 'CA',
    205: 'CA',
    206: 'CA',
    207: 'CA',
    208: 'NV',
    209: 'AZ',
    210: 'UT',
    211: 'NM',
    212: 'CO',
    213: 'WY',
    214: 'ID',
    215: 'MT',
    216: 'TX',
    301: 'TX',
    302: 'TX',
    303: 'TX',
    304: 'TX',
    305: 'TX',
    306: 'TX',
    307: 'TX',
    308: 'TX',
    }


def classify_interstate_intrastate(scenario):
    """Classifies branches in a change_table as interstate or intrastate.

    :param powersimdata.scenario.scenario.Scenario scenario: scenario instance.
    :return: (*dict*) -- keys are *'interstate'*, *'intrastate'*. Values are
        list of branch ids.
    """
    
    ct = scenario.state.get_ct()
    grid = scenario.state.get_grid()
    upgraded_branches = _classify_interstate_intrastate(ct, grid)
    return upgraded_branches


def _classify_interstate_intrastate(ct, grid):
    """Classifies branches in a change_table as interstate or intrastate.
    This function is separate from classify_interstate_intrastate() for testing
    purposes.

    :param dict ct: change_table dictionary.
    :param powersimdata.input.grid.Grid grid: Grid instance.
    :return: (*dict*) -- keys are *'interstate'*, *'intrastate'*. Values are
        list of branch ids.
    """
    
    branch = grid.branch
    upgraded_branches = {'interstate': [], 'intrastate': []}
    
    if 'branch' not in ct or 'branch_id' not in ct['branch']:
        return upgraded_branches
    
    all_upgraded_branches = ct['branch']['branch_id'].keys()
    for b in all_upgraded_branches:
        # Alternatively: bus.loc[branch.loc[b, 'from_bus_id'], 'from_zone_id']
        try:
            from_zone = branch.loc[b, 'from_zone_id']
            to_zone = branch.loc[b, 'to_zone_id']
        except KeyError:
            raise ValueError('ct entry not found in branch: ' + str(b))
        try:
            from_state = zones_to_states[from_zone]
        except KeyError:
            err_msg = 'zone not found in zones_to_states: ' + str(from_zone)
            raise ValueError(err_msg)
        try:
            to_state = zones_to_states[to_zone]
        except KeyError:
            err_msg = 'zone not found in zones_to_states: ' + str(to_zone)
            raise ValueError(err_msg)
        if from_state == to_state:
            upgraded_branches['intrastate'].append(b)
        else:
            upgraded_branches['interstate'].append(b)
    
    return upgraded_branches
