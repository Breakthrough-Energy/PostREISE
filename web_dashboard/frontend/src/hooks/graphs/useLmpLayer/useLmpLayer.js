import { useState } from 'react';
import { ScatterplotLayer } from '@deck.gl/layers';
import { COLORS_RGB, LMP_COLORS_RGB } from '../../../data/colors';

// Data is: Iterable | String | Promise | AsyncIterable | Object
const useLmpLayer = props => {
  const [ data, setData ] = useState(props.data);
  const [ dataLoaded, setDataLoaded ] = useState(false);

  const getColors = data => LMP_COLORS_RGB(data.lmp_mean);

  const getTooltipString = data => {
    if (data.layer.id === 'lmp-layer' && data.object) {
      // Optional: can also include voltage_level
      const { bus_id, lmp_mean } = data.object;
      return `Bus ${bus_id}: ${lmp_mean} $/MWh`;
    }
  }

  const lmpLayer = new ScatterplotLayer({
    id: 'lmp-layer',
    data: data,
    onDataLoad: () => {
      requestAnimationFrame(() => setDataLoaded(true))
    },
    pickable: true,
    opacity: 1,
    stroked: false,
    filled: true,
    radiusUnits: 'meters',
    radiusMaxPixels: 5,
    radiusMinPixels: 1,
    getRadius: 2000,
    getFillColor: dataLoaded ? getColors : COLORS_RGB.clear,
    getPosition: data => data.coords,
    updateTriggers: {
      getFillColor: dataLoaded
    },
    transitions: {
      getFillColor: 375
    },
  });

  return {
    lmpLayer,
    setLmpData: setData,
    getLmpTooltipString: getTooltipString
  }
}

export default useLmpLayer;
