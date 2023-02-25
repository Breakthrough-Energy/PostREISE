import React from 'react';
import { ResponsiveBar } from '@nivo/bar';
import { RESOURCE_COLORS_HEX } from '../../../data/colors';
import { GRID_DATA_URL, RESOURCE_DISPLAY_NAMES, RESOURCE_ORDER } from '../../../data/graph_info';
import { locationName2fileName, numToDisplayString } from '../../../util/util';
import useJsonQuery from '../../../hooks/useJsonQuery/useJsonQuery';

export const GenerationBar = ({ scenarioId, location }) => {
  const baseUrl = `${GRID_DATA_URL}/${scenarioId}/yearly/${locationName2fileName(location)}`;
  const { loading, error, data } = useJsonQuery(`${baseUrl}/pg.json`);

  if (loading) return 'Loading...';
  if (error) return `Error loading data.`;

  const barData = formatBarData(data);

  return (
    <ResponsiveBar
      data={barData.reverse()}
      keys={['Generation']}
      indexBy="id"
      layout="horizontal"
      margin={{ top: 5, right: 30, bottom: 72, left: 90 }}
      padding={0.3}
      colors={graphData => RESOURCE_COLORS_HEX[graphData.data.resourceType]}
      colorBy="index"
      axisBottom={{
        format: value => numToDisplayString(value),
        tickRotation: -45,
        legend: 'Annual Generation (GWh)',
        legendPosition: 'middle',
        legendOffset: 60
      }}
      axisLeft={{
        tickSize: 5,
        tickPadding: 5,
        tickRotation: 0,
        legend: null,
      }}
      enableLabel={false}
      tooltipFormat={value => numToDisplayString(value)}
      animate={true}
      motionStiffness={90}
      motionDamping={15} />
  );
}

/**
 * Formats the response data for the graph. Also filters out values that are
 * too small to show on the graph (they mess up the bar colors)
 * @param data { 'ng': 123.45, 'wind': 25.61, ... }
 * @returns [ { id: 'Natural Gas', resourceType: 'ng', ng: 123.45 }, ... ]
 */
export const formatBarData = data => {
  // Used to filter out values that are non-zero but too small to show
  const maxGenerationValue = Math.max(...Object.values(data));

  const barData = RESOURCE_ORDER.reduce((acc, resourceType) => {
    const generation = data[resourceType];
    const isTooSmall = generation/maxGenerationValue < 0.005;
    if (generation && !isTooSmall) {
      acc.push({
        id: RESOURCE_DISPLAY_NAMES[resourceType],
        resourceType: resourceType,
        'Generation': generation
      });
    }

    return acc;
  }, []);

  return barData;
};

export default React.memo(GenerationBar);
