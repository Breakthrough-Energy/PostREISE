import React from 'react';
import { ResponsivePie } from '@nivo/pie';
import { RESOURCE_COLORS_HEX } from '../../../data/colors';
import { GRID_DATA_URL, RESOURCE_DISPLAY_NAMES, RESOURCE_ORDER } from '../../../data/graph_info';
import { locationName2fileName, numToDisplayString } from '../../../util/util';
import useJsonQuery from '../../../hooks/useJsonQuery/useJsonQuery';

import './GenerationPie.css';

const GenerationPie = ({ scenarioId, location }) => {
  const baseUrl = `${GRID_DATA_URL}/${scenarioId}/yearly/${locationName2fileName(location)}`;
  const { loading, error, data } = useJsonQuery(`${baseUrl}/pg.json`);

  if (loading) return 'Loading...';
  if (error) return `Error loading data.`;

  const pieData = formatPieData(data);

  return (
    <>
      <ResponsivePie
        data={pieData}
        keys={pieData.map(resource => resource.resourceType)}
        indexBy="resourceType"
        margin={{ top: 20, right: 90, bottom: 20, left: 90 }}
        startAngle={-90}
        innerRadius={0.7}
        padAngle={1}
        cornerRadius={1}
        colors={graphData => RESOURCE_COLORS_HEX[graphData.data.resourceType]}
        arcLinkLabelsSkipAngle={5}
        arcLinkLabelsDiagonalLength={15}
        arcLinkLabelsStraightLength={0}
        arcLinkLabelsTextOffset={0}
        arcLinkLabelsThickness={0}
        enableArcLabels={false}
        valueFormat={value => numToDisplayString(value)}
        animate={true}
        motionStiffness={90}
        motionDamping={15} />
      <div className="pie__total">
        <span>{calculatePieTotal(data)}</span>
        <span>GWh</span>
      </div>
    </>
  );
}

/**
 * Formats the response data for the graph
 * @param data { 'ng': 123.45, 'wind': 25.61, ... }
 * @returns [ { id: 'Natural Gas', resourceType: 'ng', value: 123.45 }, ... ]
 */
export const formatPieData = data => {
  const pieData = RESOURCE_ORDER.reduce((acc, resourceType) => {
    const generation = data[resourceType];
    if (generation) {
      acc.push({
        id: RESOURCE_DISPLAY_NAMES[resourceType],
        resourceType: resourceType,
        'value': data[resourceType]
      });
    }

    return acc;
  }, []);
  return pieData;
}

export const calculatePieTotal = data => {
  const generationTotal = Object.values(data).reduce((acc, val) => acc + val, 0);
  return numToDisplayString(generationTotal);
}

export default React.memo(GenerationPie);
