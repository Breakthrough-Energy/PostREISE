import { useState } from 'react';
import { LineLayer } from '@deck.gl/layers';
import { COLORS_RGB, createTrafficScale, INTERCONNECT_COLORS_RGB } from '../../../data/colors';
import { numToDisplayString } from '../../../util/util';

export const BRANCH_COLOR_MODE = {
  INTERCONNECT: 'Interconnect',
  UTIL: 'Util',
  RISK: 'Risk',
  BIND: 'Bind'
};

// Data is: Iterable | String | Promise | AsyncIterable | Object
const useBranchLayer = props => {
  const [ data, setData ] = useState(props.data);
  const [ colorMode, setColorMode ] = useState(props.branchColorMode || BRANCH_COLOR_MODE.INTERCONNECT);
  const [ dataLoaded, setDataLoaded ] = useState(false);

  const createTooltip = (data, getTooltipString) => {
    if (data.layer.id === 'branch-layer' && data.object) {
      return getTooltipString(data.object);
    }
  }

  const getTooltipBase = ({ branch_id, capacity }) => {
    return `Branch ${branch_id}: ${numToDisplayString(capacity)} MW`;
  }

  // create function to get branch colors
  let getColors, trafficScale, getTooltipString;
  switch (colorMode) {
    case BRANCH_COLOR_MODE.UTIL:
      trafficScale = createTrafficScale(0, 1);
      getColors = data => trafficScale(data.median_utilization);
      getTooltipString = data => createTooltip(data,
        data => `${getTooltipBase(data)}, ${Math.round(data.median_utilization * 100)}% Utilization`
      );
      break;
    case BRANCH_COLOR_MODE.RISK:
      trafficScale = createTrafficScale(0, 20000000); // 20mil TODO: check if correct
      getColors = data => data.risk === 0 ? COLORS_RGB.mapGray : trafficScale(data.risk);
      getTooltipString = data => createTooltip(data,
        data => (data.risk > 0) && `${getTooltipBase(data)}, Risk: ${numToDisplayString(data.risk)} GWh`
      );
      break;
    case BRANCH_COLOR_MODE.BIND:
      trafficScale = createTrafficScale(0, 3000);
      getColors = data => data.bind === 0 ? COLORS_RGB.mapGray : trafficScale(data.bind);
      getTooltipString = data => createTooltip(data,
        data => (data.bind > 0) && `${getTooltipBase(data)}, ${numToDisplayString(data.bind)} Binding Incidents`
      );
      break;
    case BRANCH_COLOR_MODE.INTERCONNECT:
    default:
      getColors = data => INTERCONNECT_COLORS_RGB[data.interconnect];
  }

  //TODO: make binding and risky branches more visible

  const branchLayer = new LineLayer({
    id: 'branch-layer',
    data: data,
    onDataLoad: () => {
      requestAnimationFrame(() => setDataLoaded(true));
    },
    pickable: true,
    widthScale: 5,
    widthMinPixels: 0.2,
    widthMaxPixels: 50,
    widthUnits: 'meters',
    getWidth: data => data.capacity,
    getSourcePosition: data => data.coords[0],
    getTargetPosition: data => data.coords[1],
    getColor: dataLoaded ? getColors : COLORS_RGB.clear,
    updateTriggers: {
      getColor: [ dataLoaded, colorMode ],
    },
    transitions: {
      getColor: 375,
    },
  });

  return {
    branchLayer,
    setBranchData: setData,
    branchColorMode: colorMode,
    setBranchColorMode: setColorMode,
    getBranchTooltipString: getTooltipString
  }
}

export default useBranchLayer;
