// Various text and display constants related to graphs
import React from 'react';
import Link from '../components/common/Link/Link';
import { BRANCH_COLOR_MODE } from '../hooks/graphs/useBranchLayer/useBranchLayer';
import { US_TEST_SYSTEM_DATA_URL } from './constants';
import { SCENARIO_INFO } from './scenario_info';

const GRID_DATA_VERSION = 'v1';
export const GRID_DATA_URL = `./grid-data/${GRID_DATA_VERSION}`;

// Line pattern for nivo graphs
// More info: https://nivo.rocks/guides/patterns/
export const NIVO_CURTAILMENT_LINES = {
  id: 'blackLines',
  type: 'patternLines',
  background: 'inherit',
  color: '#000000',
  rotation: -45,
  lineWidth: 1,
  spacing: 7
};

export const RESOURCE_DISPLAY_NAMES = {
  'wind_curtailment': 'Wind Curtailment',
  'wind_offshore_curtailment': 'Offshore Wind Curtailment',
  'solar_curtailment': 'Solar Curtailment',

  'storage': 'Storage',
  'wind': 'Wind',
  'wind_offshore': 'Offshore Wind',
  'solar': 'Solar',

  'ng': 'Natural Gas',
  'coal': 'Coal',
  'dfo': 'Oil',
  'other': 'Other',

  'biomass': 'Biomass',
  'geothermal': 'Geothermal',
  'hydro': 'Hydro',
  'nuclear': 'Nuclear',
};

export const RESOURCE_ORDER = Object.keys(RESOURCE_DISPLAY_NAMES);

// Taken from: https://github.com/Breakthrough-Energy/PowerSimData/blob/develop/powersimdata/network/usa_tamu/constants/plants.py
// PostREISE value sourced from: IPCC Special Report on Renewable Energy Sources and Climate Change
// Mitigation (2011), Annex II: Methodology, Table A.II.4, 50th percentile
// http://www.ipcc-wg3.de/report/IPCC_SRREN_Annex_II.pdf
export const CO2_TONS_PER_MWH = { // metric tons
  "coal": 1.001,
  "dfo": 0.840,
  "ng": 0.469,
}

export const getEmissions = (generation, resource_type) => generation * CO2_TONS_PER_MWH[resource_type];


// Graph type constants

// NOTE: If the scenario does not have offshoreWindCurtailment in
// scencario_info, offshoreWindCurtailment will be skipped over by GraphColumn
export const DASHBOARD_GRAPH_ORDER = [
  'emissions', 'emissionsDiff', 'genStack', 'genBar', 'genPie', 'branch', 'windCurtailment', 'offshoreWindCurtailment', 'solarCurtailment', 'lmp'
];

export const NO_GRAPH_TEXT = "No data available for this graph type."

export const GRAPH_INFO = {
  emissions: {
    title: 'Present Day Carbon Emissions',
    subtitle: 'Bubble size indicates quantity of carbon emissions in the present day* for all plants generating power in this simulated scenario. Color of the bubbles indicates resource type: purple for natural gas and black for coal.',
    fileName: 'carbon_map',
  },
  emissionsDiff: {
    getTitle: scenarioId => `Present Day to ${SCENARIO_INFO[scenarioId].year || 2030}`,
    subtitle: 'Bubble size indicates change in quantity of carbon emissions between the present-day* simulation and the simulated results for year 2030, for all plants generating power in this scenario. Color of the bubbles indicates direction of the change in carbon emissions: red indicates an increase in carbon emissions, whereas green indicates a decrease in carbon emissions.',
    fileName: 'carbon_diff_map',
  },
  genStack: {
    title: 'Daily Generation and Curtailment',
    subtitle: 'Time series depicting generation of energy over time for a year, with energy generation broken down by resource type.',
  },
  lmp: {
    title: 'Locational Marginal Prices',
    subtitle: 'Map of the variation in locational marginal prices (LMPs). Each dot represents a node in the simulated US electric grid. The color of the dot represents the average locational marginal price of energy at that node over the entire simulation.',
    fileName: 'lmp_map',
  },
  genBar: {
    title: 'Annual Generation by Resource',
    subtitle: 'Bar chart of annual energy produced in GWh by resource type in this simulation.',
  },
  genPie: {
    title: 'Annual Generation by Resource',
    subtitle: 'Pie chart of annual energy produced in GWh by resource type in this simulation.',
  },
  windCurtailment: {
    title: 'Daily Wind Curtailment',
    subtitle: 'Time series of daily wind power generation and curtailment for this simulation.',
  },
  offshoreWindCurtailment: {
    title: 'Daily Offshore Wind Curtailment',
    subtitle: 'Time series of daily offshore wind power generation and curtailment for this simulation.',
  },
  solarCurtailment: {
    title: 'Daily Solar Curtailment',
    subtitle: 'Time series of daily solar power generation and curtailment for this simulation.',
  },
  branch: {
    toggleGraphs: [ 'transmissionUtilization', 'transmissionRisk', 'transmissionBind' ],
    toggleText: [ BRANCH_COLOR_MODE.UTIL, BRANCH_COLOR_MODE.RISK, BRANCH_COLOR_MODE.BIND ]
  },
  transmissionUtilization: {
    title: 'Transmission Utilization',
    subtitle: 'Map of transmission system color coded to indicate degree of congestion, with red indicating the most congested lines, yellow indicating intermediate congestion, and green indicating relatively low levels of congestion.',
    fileName: 'transmission_utilization_map',
  },
  transmissionRisk: {
    title: 'Transmission Risk',
    subtitle: 'Map of transmission system indicating (1) the most congested lines, and (2) the total energy flowing over those lines when they are congested. Color of highlighted transmission lines indicates the amount of energy flowing over the line when that line is more than 90% utilized. This metric originated from the WECC Congestion Analysis Process.',
    fileName: 'transmission_risk_map',
  },
  transmissionBind: {
    title: 'Binding Branches',
    subtitle: 'Map of transmission system indicating lines that reach 100% of its maximum capacity for one or more time intervals during the simulation. Color of highlighted branches indicates the number of incidents in which the lines reached 100% capacity.',
    fileName: 'transmission_bind_map'
  },
  interconnectionMap: {
    title: 'US Interconnections',
    subtitle: null,
    fileName: 'interconnection_map'
  },
  goalsMap: {
    title: `States' Renewable Energy Goals`,
    subtitle: null,
    fileName: 'goals_map'
  }
};

export const CARBON_FOOTNOTE = (
  <>
    <p>
      <em>*Present-day simulation uses 2020 and 2019 data from multiple sources. For more detail on source data, please visit our source data repository available <Link href={US_TEST_SYSTEM_DATA_URL}>here</Link>.</em>
    </p>
  </>
);
