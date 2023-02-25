import React from 'react';
import { ResponsiveLine } from '@nivo/line';
import {
  locationName2fileName,
  numToDisplayString } from '../../../util/util';
import {
  NIVO_CURTAILMENT_LINES,
  GRID_DATA_URL,
  RESOURCE_DISPLAY_NAMES,
  RESOURCE_ORDER } from '../../../data/graph_info';
import { RESOURCE_COLORS_HEX } from '../../../data/colors';
import useJsonQuery from '../../../hooks/useJsonQuery/useJsonQuery';

const GenerationStackedLine = ({
  scenarioId,
  location,
  dateFormat = '%Y-%m-%d',
  enableGridX = true,
  precision = 'day',
  axisBottom = {
    format: '%b',
    tickValues: 'every month',
  }}) => {

  // Load files for PG and curtailment
  const baseUrl = `${GRID_DATA_URL}/${scenarioId}/daily/${locationName2fileName(location)}`;
  const { loading, error, data } = useJsonQuery(`${baseUrl}/pg.json`);
  const { loading: cLoading, error: cError, data: cData } = useJsonQuery(`${baseUrl}/curtailment.json`);

  if (loading || cLoading) return 'Loading...';
  if (error || cError) return `Error loading data.`;

  const lineData = formatLineData(data, cData);
  const yAxisText = { 'hour': 'Hourly Energy (GW)', 'day': 'Daily Energy (GWh/Day)' };

  return (
    <ResponsiveLine
      data={lineData.reverse()}
      margin={{ top: 5, right: 0, bottom: 30, left: 60 }}
      xScale={{
        type: 'time',
        format: dateFormat,
        useUTC: false,
        precision,
      }}
      xFormat={`time:${dateFormat}`}
      yScale={{
        type: 'linear',
        min: 0,
        max: 'auto',
        stacked: true,
        reverse: false
      }}
      axisTop={null}
      axisRight={null}
      axisBottom={axisBottom}
      axisLeft={{
          format: value => numToDisplayString(value),
          orient: 'left',
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: yAxisText[precision],
          legendOffset: -55,
          legendPosition: 'middle'
      }}
      colors={graphData => RESOURCE_COLORS_HEX[graphData.resourceType]}
      defs={[ NIVO_CURTAILMENT_LINES ]}
      fill={[
        { match: { id: 'Wind Curtailment' }, id: 'blackLines' },
        { match: { id: 'Solar Curtailment' }, id: 'blackLines' },
        { match: { id: 'Wind Offshore Curtailment' }, id: 'blackLines' },
      ]}
      lineWidth={1}
      enableArea={true}
      areaOpacity={1}
      enableSlices="x"
      enablePoints={false}
      enableGridX={enableGridX}
      theme={{
        tooltip: {
            container: {
                fontSize: 14,
            },
        },
      }}
    />
  );
}

// return true if all values in list equal zero
export const resourceHasNoData = data => data.find(({ y }) => y !== 0) === undefined;

/**
 * Formats the response data for the graph
 * @param data  {
 *                ng: [ { x: '2016-01-23', y: 12345.67 }, ... ]
 *                coal: [ ... ],
 *                ...
 *                }
 * @returns     [{
 *                id: 'Natural Gas',
 *                resourceType: 'ng'
 *                data: [ { x: '2016-01-23', y: 12345.67 }, ... ]
 *               },
 *              ... ]
 */
export const formatLineData = (data, curtailmentData) => {
  const lineData = RESOURCE_ORDER.reduce((acc, resourceType) => {
    const resourceTypeData = data[resourceType] || curtailmentData[resourceType];

    if (!resourceTypeData || resourceHasNoData(resourceTypeData)) {
      return acc;
    }

    acc.push({
      id: RESOURCE_DISPLAY_NAMES[resourceType],
      resourceType: resourceType,
      data: resourceTypeData
    });

    return acc;
  }, []);

  return lineData;
}

export default React.memo(GenerationStackedLine);
