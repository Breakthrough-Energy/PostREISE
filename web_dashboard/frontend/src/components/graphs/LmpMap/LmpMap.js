import React, { useEffect } from 'react';
import DeckGLMap from '../DeckGLMap/DeckGLMap';
import { GRID_DATA_URL } from '../../../data/graph_info';
import LmpMapLegend from './LmpMapLegend';
import useLmpLayer from '../../../hooks/graphs/useLmpLayer/useLmpLayer';

import './LmpMap.css';

const LmpMap = ({ scenarioId, location, setLocation }) => {
  const lmpDataUrl = `${GRID_DATA_URL}/${scenarioId}/lmp.json`;
  const {
    lmpLayer,
    setLmpData,
    getLmpTooltipString } = useLmpLayer({ data: lmpDataUrl });

  useEffect(() => {
    setLmpData(lmpDataUrl)
  }, [ scenarioId, lmpDataUrl, setLmpData ]);

  const getTooltip = pickedObjects => {
    const tooltipStrings = [];

    pickedObjects.forEach(data => {
      const str = getLmpTooltipString(data);
      str && tooltipStrings.push(str);
    });

    if (tooltipStrings.length === 0) {
      return null;
    } else {
      return tooltipStrings.join('\n');
    }
  }

  return (
    <div className="lmp-map">
      <DeckGLMap
        layers={[lmpLayer]}
        getTooltip={getTooltip}
        location={location}
        onLocationClick={setLocation}
        />
      <LmpMapLegend className="lmp-map__legend" />
    </div>
  );
};

export default LmpMap;
