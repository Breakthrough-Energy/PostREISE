import React, { useEffect } from 'react';
import DeckGLMap from '../DeckGLMap/DeckGLMap';
import EmissionsMapLegend from './EmissionsMapLegend';
import { GRID_DATA_URL } from '../../../data/graph_info';
import PropTypes from 'prop-types';
import usePlantLayer, { PLANT_COLOR_MODE } from '../../../hooks/graphs/usePlantLayer/usePlantLayer';

import './PlantMap.css';

const PlantMap = ({ scenarioId, scenarioId2, colorMode, location, setLocation }) => {
  const filename = colorMode === PLANT_COLOR_MODE.RESOURCE_TYPE ? 'plant.json' : 'emissions.json';
  const plantDataUrl = `${GRID_DATA_URL}/${scenarioId}/${filename}`;
  const plantDataUrl2 = scenarioId2 && `${GRID_DATA_URL}/${scenarioId2}/${filename}`;

  const {
    plantLayer,
    setPlantData,
    setPlantData2,
    plantColorMode,
    setPlantColorMode,
    getPlantTooltipString } = usePlantLayer({ data: plantDataUrl, data2: plantDataUrl2, colorMode });

  useEffect(() => {
    setPlantData(plantDataUrl)
  }, [ scenarioId, plantDataUrl, setPlantData ]);

  useEffect(() => {
    setPlantData2(plantDataUrl2)
  }, [ scenarioId2, plantDataUrl2, setPlantData2 ]);

  useEffect(() => {
    setPlantColorMode(colorMode)
  }, [ colorMode, setPlantColorMode ]);

  const getTooltip = pickedObjects => {
    const tooltipStrings = [];

    pickedObjects.forEach(data => {
      const str = getPlantTooltipString(data);
      str && tooltipStrings.push(str);
    });

    if (tooltipStrings.length === 0) {
      return null;
    } else {
      return tooltipStrings.join('\n');
    }
  }

  // TODO: resource_type legend
  return (
    <div className="plant-map">
      <DeckGLMap
        layers={[plantLayer]}
        getTooltip={getTooltip}
        location={location}
        onLocationClick={setLocation}
        />

      {plantColorMode !== PLANT_COLOR_MODE.RESOURCE_TYPE
        && <EmissionsMapLegend className="plant-map__legend" plantColorMode={plantColorMode} />}
    </div>
  );
};

DeckGLMap.propTypes = {
  scenarioId: PropTypes.number,
  colorMode: PropTypes.string,
  location: PropTypes.string,
  setLocation: PropTypes.func
};

export default PlantMap;
