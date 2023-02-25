import { useEffect, useState } from 'react';
import { COLORS_RGB, EMISSIONS_COLORS_RGB, RESOURCE_COLORS_RGB } from '../../../data/colors';
import { getEmissions, RESOURCE_DISPLAY_NAMES } from '../../../data/graph_info';
import { getArrayDiff, numToDisplayString } from '../../../util/util';
import { JSONLoader } from '@loaders.gl/json';
import { load } from '@loaders.gl/core';
import { ScatterplotLayer } from '@deck.gl/layers';

export const PLANT_COLOR_MODE = {
  RESOURCE_TYPE: 'Resource Type',
  EMISSIONS: 'Emissions',
  EMISSIONS_DIFF: 'Emissions Diff'
};

// Data is: Iterable | String | Promise | AsyncIterable | Object
const usePlantLayer = props => {
  const [ colorMode, setColorMode ] = useState(props.plantColorMode || PLANT_COLOR_MODE.RESOURCE_TYPE);
  const [ dataLoaded, setDataLoaded ] = useState(false);
  const [ data, setData ] = useState(props.data);
  const [ data2, setData2 ] = useState(props.data2); // used for emissions diff
  const [ emissionsDiffData, setEmissionsDiffData ] = useState([]);

  // Get emissions diff data if needed
  useEffect(() => {
    if (colorMode !== PLANT_COLOR_MODE.EMISSIONS_DIFF) {
      return;
    }
    const getEmissionsDiffData = async () => {
      const { scenarioData, scenarioData2 } = await fetchScenarioData(data, data2)
        .catch(err => console.log(err));
      const diff = computeGenerationDiffs(scenarioData, scenarioData2);
      setEmissionsDiffData(diff);
      setDataLoaded(true);
    }
    getEmissionsDiffData();
  }, [data, data2, colorMode, setEmissionsDiffData, setDataLoaded]);

  const getTooltipBase = (data, getTooltipString) => {
    if (data.layer.id === 'plant-layer' && data.object) {
      const { resource_type } = data.object;
      return `Plant Type: ${RESOURCE_DISPLAY_NAMES[resource_type]}` + getTooltipString(data.object);
    }
  }

  // Set layer properties based on colorMode
  let getRadius, getColors, radiusScale, getTooltipString;
  switch (colorMode) {
    case PLANT_COLOR_MODE.EMISSIONS:
      getRadius = getEmissionsRadius;
      radiusScale = 50;
      getColors = data => EMISSIONS_COLORS_RGB[data.resource_type];
      getTooltipString = data => getTooltipBase(data,
        ({ generation, resource_type }) => {
          const emissions = numToDisplayString(getEmissions(generation, resource_type));
          return `, CO<sub>2</sub> Emissions: ${emissions} Tons`;
        }
      );
      break;

    case PLANT_COLOR_MODE.EMISSIONS_DIFF:
      getRadius = getEmissionsRadius;
      radiusScale = 50;
      getColors = data => EMISSIONS_COLORS_RGB[data.generation > 0 ? 'more' : 'less'];
      getTooltipString = data => getTooltipBase(data,
        ({ generation, resource_type }) => {
          const emissions = numToDisplayString(getEmissions(Math.abs(generation), resource_type));
          const increaseOrDecrease = generation > 0 ? 'increase' : 'decrease';
          return `, ${emissions} Tons ${increaseOrDecrease} in CO<sub>2</sub> emissions`;
        }
      );
      break;

    case PLANT_COLOR_MODE.RESOURCE_TYPE:
    default:
      getRadius = data => Math.sqrt(data.capacity/Math.PI);
      radiusScale = 3500;
      getColors = data => RESOURCE_COLORS_RGB[data.resource_type];
      getTooltipString = data => getTooltipBase(data,
        ({ capacity }) => `, ${numToDisplayString(capacity)} MW`
      );
  }

  const plantLayer = new ScatterplotLayer({
    id: 'plant-layer',
    data: colorMode === PLANT_COLOR_MODE.EMISSIONS_DIFF ? emissionsDiffData : data,
    onDataLoad: () => {
      requestAnimationFrame(() => setDataLoaded(true))
    },
    pickable: true,
    stroked: true,
    filled: true,
    radiusUnits: 'meters',
    radiusScale: radiusScale,
    radiusMaxPixels: 30,
    radiusMinPixels: 0,
    getFillColor: dataLoaded ? getColors : COLORS_RGB.clear,
    getRadius: getRadius,
    getPosition: data => data.coords,
    updateTriggers: {
      getFillColor: [ dataLoaded, colorMode ],
      getRadius: [ data, data2 ]
    },
    transitions: {
      getFillColor: 375,
      getRadius: 375
    },
  });

  return {
    plantLayer,
    setPlantData: setData,
    setPlantData2: setData2,
    plantColorMode: colorMode,
    setPlantColorMode: setColorMode,
    getPlantTooltipString: getTooltipString
  }
}

const getEmissionsRadius = data => {
  if (data.resource_type === 'coal' || data.resource_type === 'ng') {
    // Math.abs handles emission diffs that are negative
    return Math.sqrt(getEmissions(Math.abs(data.generation), data.resource_type)/Math.PI);
  } else {
    return 0;
  }
}

// Used for emission diffs
const fetchScenarioData = async (data, data2) => {
  let promises = [ null, null ];

  // If data is a url we need to fetch
  if (typeof(data) === 'string') {
    promises[0] = load(data, JSONLoader);
  }
  if (typeof(data2) === 'string') {
    promises[1] = load(data2, JSONLoader);
  }

  const fetchedDataList = await Promise.all(promises);

  return {
    scenarioData: fetchedDataList[0] || data,
    scenarioData2: fetchedDataList[1] || data2
  };
}


// Gets diff in generation for each scenario, which will then be used to
// calculate emissions when getRadius() is called
const computeGenerationDiffs = (scenarioData, scenarioData2) => {
  const getKey = ({ resource_type, coords, zone, interconnect }) =>
    `${interconnect},${zone},${resource_type},${coords[0]},${coords[1]}`;

  const { rightDiff, rightObj } = getArrayDiff(scenarioData, scenarioData2, "both", getKey);

  const diffData = scenarioData.map(plant => {
    const key = getKey(plant);
    // a positive number means our scenario has more emissions than the other scenario
    if (rightObj.hasOwnProperty(key)) {
      plant['generation'] = plant['generation'] - rightObj[key]['generation'];
    }
    return plant;
  });

  // include plants in scenario2 that are not found in scenario1
  rightDiff.forEach(plant => {
    plant['generation'] = -1 * plant['generation'];
    diffData.push(plant);
  });

  return diffData;
}

export default usePlantLayer;
