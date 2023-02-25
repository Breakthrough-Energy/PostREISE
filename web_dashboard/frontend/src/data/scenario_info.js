import React from 'react';
import { A } from 'hookrouter';
// Scenario names, descriptions, and related text
// Mainly for the dashboard, esp. ScenarioToolbar

export const DEFAULT_SCENARIO = 's1705';
export const PRESENT_DAY_SCENARIO = 's824';
export const MAX_COLUMNS = 3;
export const SCENARIO_LABEL = 'Scenario';
export const SCENARIO_LABEL_PLURAL = 'Scenarios';
export const LOCATION_LABEL = 'Location';
export const SECURITY_NOTICE = <p>NOTE: Although recreation of high-resolution spatial data is sometimes publicly available, detailed information is often restricted on national security grounds. This limitation led to creation of ‘synthetic’ models of the U.S. power system by Texas A&M University (‘the TAMU network’), representative of real patterns of geography and network topology while disclosing no protected information. Some work has been done to add time-series load data to this synthetic network, but a full dataset providing granular temporal data for loads and variable renewable energy (VRE) for a large-scale network of the U.S. power system is still unavailable. Read more about our model <A href="/model">here</A>.</p>;

// NOTE: JS iterates over keys in order of insertion unless they are numeric
// So we prepend an s (ex: s1149) to force keys to be interpreted as non-numeric
export const SCENARIO_INFO = {
  removeColumn: {
    name: 'None',
    descList: ['Remove the current scenario.']
  },

  // Macro Grid Scenarios
  's1705': {
    name: 'Macro Grid Report - Design 1',
    descList: ['This simulation is Design 1 in BE Sciences’ Macro Grid report. In this simulation, all states with goals in the Western Interconnection meet California’s target of 60% renewable energy generation by 2030, all states with goals in the Eastern Interconnection meet New York’s target of 70% renewable energy generation by 2030, and Texas has their 2030 renewable energy projections tripled to mimic these ambitions goals. Additions of 932GW of solar and wind capacity are spread across the country to meet these goals. Substantial upgrades to the AC transmission lines are made within interconnections, connecting areas of high renewable capacity to areas of high demand.']
  },
  's1724': {
    name: 'Macro Grid Report - Design 2a',
    descList: ['This simulation is Design 2a in BE Sciences’ Macro Grid report. In this simulation, all states with goals in the Western Interconnection meet California’s target of 60% renewable energy generation by 2030, all states with goals in the Eastern Interconnection meet New York’s target of 70% renewable energy generation by 2030, and Texas has their 2030 renewable energy projections tripled to mimic these ambitions goals. Additions of 932GW of solar and wind capacity are spread across the country to meet these goals. At the interconnection seams, the HVDC back-to-back converter stations are expanded to allow for more energy exchanges between the three interconnections. Substantial upgrades to the AC transmission lines are also made within interconnections, connecting areas of high renewable capacity to areas of high demand.']
  },
  's1723': {
    name: 'Macro Grid Report - Design 2b',
    descList: ['This simulation is Design 2b in BE Sciences’ Macro Grid report. In this simulation, all states with goals in the Western Interconnection meet California’s target of 60% renewable energy generation by 2030, all states with goals in the Eastern Interconnection meet New York’s target of 70% renewable energy generation by 2030, and Texas has their 2030 renewable energy projections tripled to mimic these ambitions goals. Additions of 932GW of solar and wind capacity are spread across the country to meet these goals. Three new HVDC lines are added across the east-west interconnection seam and the HVDC back-to-back converter stations are expanded to allow for more energy exchanges between the three interconnections. Substantial upgrades to the AC transmission lines are also made within interconnections, connecting areas of high renewable capacity to areas of high demand.']
  },
  's1270': {
    name: 'Macro Grid Report - Design 3',
    descList: ['This simulation is Design 3 in BE Sciences’ Macro Grid report. In this simulation, all states with goals in the Western Interconnection meet California’s target of 60% renewable energy generation by 2030, all states with goals in the Eastern Interconnection meet New York’s target of 70% renewable energy generation by 2030, and Texas has their 2030 renewable energy projections tripled to mimic these ambitions goals. Additions of 932GW of solar and wind capacity are spread across the country to meet these goals. Sixteen new HVDC lines are added around the country to allow for more energy exchanges between and within the three interconnections. Substantial upgrades to the AC transmission lines are also made within interconnections, connecting areas of high renewable capacity to areas of high demand.']
  },

  // USA collaborative
  's1152': {
    name: 'Collaborative, USA 2030 (extra renewables)',
    descList: ['This simulation focuses on building extra renewables and building out relatively less transmission. All states across the U.S. with goals collectively meet the renewable energy and clean energy goals for 2030. States build renewables in the best locations regardless of state boundaries and build interstate transmission (transmission crossing state lines) when needed.']
  },
  's1151': {
    name: 'Collaborative, USA 2030 (balanced)',
    descList: ['This simulation balances building new renewable energy capacity and building out transmission. All states across the U.S. with goals collectively meet the renewable energy and clean energy goals for 2030. States build renewables in the best locations regardless of state boundaries and build interstate transmission (transmission crossing state lines) when needed.']
  },
  's1149': {
    name: 'Collaborative, USA 2030 (extra transmission)',
    descList: ['This simulation focuses on building out transmission and building relatively less new renewable energy capacity. All states across the U.S. with goals collectively meet the renewable energy and clean energy goals for 2030. States build interstate transmission (transmission crossing state lines) when needed and build renewables in the best locations regardless of state boundaries.']
  },

  // USA independent
  's1099': {
    name: 'Independent, USA 2030 (extra renewables)',
    descList: ['This simulation focuses on building extra renewables and building out relatively less transmission. All states across the U.S. meet their state’s own renewable energy and clean energy goals for 2030. Renewables are only built intrastate (within state) and transmission is only upgraded within each state to achieve these goals.']
  },
  's1098': {
    name: 'Independent, USA 2030 (balanced)',
    descList: ['This simulation balances building new renewable energy capacity and building out transmission. All states across the U.S. meet their state’s own renewable energy and clean energy goals for 2030. Renewables are only built intrastate (within state) and transmission is only upgraded within each state to achieve these goals.']
  },
  's1097': {
    name: 'Independent, USA 2030 (extra transmission)',
    descList: ['This simulation focuses on building out transmission and building relatively less new renewable energy capacity. All states across the U.S. meet their state’s own renewable energy and clean energy goals for 2030. Transmission is only upgraded within each state and renewables are only built intrastate (within state) to achieve these goals.']
  },

  // USA collaborative with storage
  's1206': {
    name: 'Collaborative with Storage, USA 2030 (extra renewables)',
    descList: ['This simulation focuses on building extra renewables and building out relatively less transmission while also including planned and state-mandated levels of grid-scale energy storage. All states across the U.S. collectively meet the renewable energy and clean energy goals for 2030. States build renewables in the best locations regardless of state boundaries and build interstate transmission (transmission crossing state lines) when needed.']
  },
  's1205': {
    name: 'Collaborative with Storage, USA 2030 (balanced)',
    descList: ['This simulation balances building new renewable energy capacity and building out transmission while also including planned and state-mandated levels of grid-scale energy storage. All states across the U.S. with goals collectively meet the renewable energy and clean energy goals for 2030. States build renewables in the best locations regardless of state boundaries and build interstate transmission (transmission crossing state lines) when needed.']
  },
  's1204': {
    name: 'Collaborative with Storage, USA 2030 (extra transmission)',
    descList: ['This simulation focuses on building out transmission and building relatively less new renewable energy capacity while also including planned and state-mandated levels of grid-scale energy storage. All states across the U.S. with goals collectively meet the renewable energy and clean energy goals for 2030. States build interstate transmission (transmission crossing state lines) when needed and build renewables in the best locations regardless of state boundaries.']
  },

  // USA collaborative with renewables at retirements
  's1244': {
    name: 'Collaborative with Renewables at Retirements, USA 2030 (extra renewables)',
    descList: ['This simulation focuses on building extra renewables and building out relatively less transmission. All states across the U.S. collectively meet the renewable energy and clean energy goals for 2030. States build renewables initially at locations of present-day* power plants that have or are planned to be retired before 2030, then in the best locations regardless of state boundaries.  Interstate transmission (transmission crossing state lines) is also built when needed.']
  },
  's1245': {
    name: 'Collaborative with Renewables at Retirements, USA 2030 (balanced)',
    descList: ['This simulation balances building new renewable energy capacity and building out transmission. All states across the U.S. collectively meet the renewable energy and clean energy goals for 2030. States build renewables initially at locations of present-day* power plants that have or are planned to be retired before 2030, then in the best locations regardless of state boundaries.  Interstate transmission (transmission crossing state lines) is also built when needed.']
  },
  's1257': {
    name: 'Collaborative with Renewables at Retirements, USA 2030 (extra transmission)',
    descList: ['This simulation focuses on building out transmission and building relatively less new renewable energy capacity. All states across the U.S. collectively meet the renewable energy and clean energy goals for 2030. Interstate transmission (transmission crossing state lines) is built when needed. States build renewables initially at locations of present-day* power plants that have or are planned to be retired before 2030, then in the best locations regardless of state boundaries.']
  },

  // offshore wind
  's1362': {
    name: 'Offshore Wind, 2030 (East Coast only, extra renewables)',
    descList: ['This simulation adds offshore wind and then focuses on building extra onshore renewable energy capacity. All states in the Eastern Interconnection with goals collectively meet the renewable energy and clean energy goals for 2030.'],
    offshoreWind: true
  },
  's1361': {
    name: 'Offshore Wind, 2030 (East Coast only, balanced)',
    descList: ['This simulation adds offshore wind and then balances building new onshore renewable energy capacity and building out transmission. All states in the Eastern Interconnection with goals collectively meet the renewable energy and clean energy goals for 2030.'],
    offshoreWind: true
  },
  's1338': {
    name: 'Offshore Wind, 2030 (East Coast only, extra transmission)',
    descList: ['This simulation adds offshore wind and then focuses on building out transmission. All states in the Eastern Interconnection with goals collectively meet the renewable energy and clean energy goals for 2030.'],
    offshoreWind: true
  },

  // Historic
  's824': {
    name: 'Current Conditions, USA 2020',
    descList: ['This is a base case simulation of the entire U.S. based on present-day* data.'],
    year: 2020
  },
  's823': {
    name: 'Historical Base Case Conditions, USA 2016',
    descList: ['This is a base case simulation of the entire U.S. based on 2016 historical data.'],
    year: 2016
  }
};

export const SCENARIO_ORDER_FOR_SELECT_COMPONENT = Object.keys(SCENARIO_INFO);
