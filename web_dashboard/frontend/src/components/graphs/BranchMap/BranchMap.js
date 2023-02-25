import React, { useEffect } from 'react';
import BranchMapLegend from './BranchMapLegend';
import DeckGLMap from '../DeckGLMap/DeckGLMap';
import { GRID_DATA_URL } from '../../../data/graph_info';
import InterconnectionMapLegend from './InterconnectionMapLegend';
import PropTypes from 'prop-types';
import useBranchLayer, { BRANCH_COLOR_MODE } from '../../../hooks/graphs/useBranchLayer/useBranchLayer';

import './BranchMap.css';

const BranchMap = ({ scenarioId, colorMode, location, setLocation }) => {
  const branchDataUrl = `${GRID_DATA_URL}/${scenarioId}/branch.json`;
  const {
    branchLayer,
    setBranchData,
    branchColorMode,
    setBranchColorMode,
    getBranchTooltipString } = useBranchLayer({ data: branchDataUrl, colorMode });

  useEffect(() => {
    setBranchData(branchDataUrl)
  }, [ scenarioId, branchDataUrl, setBranchData ]);

  useEffect(() => {
    setBranchColorMode(colorMode)
  }, [ colorMode, setBranchColorMode ]);

  const getTooltip = pickedObjects => {
    const tooltipStrings = [];

    pickedObjects.forEach(data => {
      const str = getBranchTooltipString(data);
      str && tooltipStrings.push(str);
    });

    if (tooltipStrings.length === 0) {
      return null;
    } else {
      return tooltipStrings.join('\n');
    }
  }

  let legend;
  switch (branchColorMode) {
    case BRANCH_COLOR_MODE.UTIL:
      legend = <BranchMapLegend className="branch-map__legend" title="Median Utilization" min={0} max={100} unit="%" />;
      break;
    case BRANCH_COLOR_MODE.RISK:
      legend = <BranchMapLegend className="branch-map__legend" title="Risk (GWh)" min={0.0} max={20000} />;
      break;
    case BRANCH_COLOR_MODE.BIND:
      legend = <BranchMapLegend className="branch-map__legend" title="Binding Incidents" min={0.0} max={3000} />;
      break;
    case BRANCH_COLOR_MODE.INTERCONNECT:
    default:
      legend = <InterconnectionMapLegend />;
  }

  return (
    <div className="branch-map">
      <DeckGLMap
        layers={[branchLayer]}
        getTooltip={getTooltip}
        location={location}
        onLocationClick={setLocation}
        />
      {legend}
    </div>
  );
};

DeckGLMap.propTypes = {
  scenarioId: PropTypes.number,
  colorMode: PropTypes.string,
  location: PropTypes.string,
  setLocation: PropTypes.func
};

export default BranchMap;
