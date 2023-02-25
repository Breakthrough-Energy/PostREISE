import { createSlice } from '@reduxjs/toolkit'
import { v4 as uuidv4 } from 'uuid';
import { setQueryParams } from 'hookrouter';
import { DASHBOARD_GRAPH_ORDER } from '../../data/graph_info.js';
import { DEFAULT_SCENARIO, MAX_COLUMNS } from '../../data/scenario_info.js';
import { load } from '@loaders.gl/core';
import { ShapefileLoader } from '@loaders.gl/shapefile';

const SHAPEFILE_URL = `./grid-data/US-States-Shapefiles/US-States-Shapefiles.shp`;

/**
 * Initializes a new graph column by creating UUIDs for the col and its graphs
 * @param {string} scenarioId
 * @param {list(string)} graphConfig - list of graphType strings
 */

const createInitialGraphColumn = () => {
  const urlSearchParams = new URLSearchParams(window.location.search);
  const { scenarioId } = Object.fromEntries(urlSearchParams.entries());

  if (scenarioId) {
    const scenarios = scenarioId.split(',');
    return scenarios.map((id) => {
      return createGraphColumn(id);
    });
  }
  return [ createGraphColumn() ];
}

const createGraphColumn = (
  scenarioId=DEFAULT_SCENARIO,
  graphConfig=DASHBOARD_GRAPH_ORDER) => {

  const graphs = graphConfig.map(graphType => {
    return { id: graphType + '_' + uuidv4(), graphType }
  });

  return { id: uuidv4(), scenarioId, graphs };
}

const fetchStateShapefiles = () => {
  return new Promise(resolve => {
    load(SHAPEFILE_URL, ShapefileLoader)
      .then(response => {
        resolve({ type: "FeatureCollection", features: response.data });
      })
      .catch(error => {
        console.log(error)
        resolve([]);
      });
  });
}

const updateURLParams = (graphColumns) => {
  let urlParams = [];

  graphColumns.forEach(column => {
    const scenarioId = column.scenarioId
    urlParams.push(scenarioId);
  });
  const finalParamsString =  urlParams.join(',');
  setQueryParams({ scenarioId: finalParamsString });
}

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState: {
    graphColumns: createInitialGraphColumn(),
    filters: { location: 'Show All' },
    stateShapefiles: fetchStateShapefiles()
  },

  reducers: {
    addColumn: (state) => {
      if (state.graphColumns.length < MAX_COLUMNS) {
        const newColumn = createGraphColumn();
        state.graphColumns.push(newColumn);
        updateURLParams(state.graphColumns);
      }
    },

    changeScenario: (state, { payload: { graphColumnId, scenarioId } }) => {
      const idx = state.graphColumns.findIndex(col => col.id === graphColumnId);
      state.graphColumns[idx].scenarioId = scenarioId;
      updateURLParams(state.graphColumns);
    },

    removeColumn: (state, { payload: { graphColumnId } }) => {
      const idx = state.graphColumns.findIndex(col => col.id === graphColumnId);
      // js arrays have no remove() method so we use splice()
      state.graphColumns.splice(idx, 1);
      updateURLParams(state.graphColumns);
    },

    updateFilter: (state, { payload: { key, value } }) => {
      state.filters[key] = value;
    }
  }
});

export default dashboardSlice.reducer;
export const { addColumn, changeScenario, removeColumn, updateFilter } = dashboardSlice.actions;
export { updateURLParams }
