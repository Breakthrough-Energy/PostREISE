import React from 'react';
import { ResponsiveLine } from '@nivo/line';
import {
  locationName2fileName,
  numToDisplayString } from '../../../util/util';
import {
  GRID_DATA_URL,
  RESOURCE_DISPLAY_NAMES } from '../../../data/graph_info';
import { RESOURCE_COLORS_HEX } from '../../../data/colors';
import useJsonQuery from '../../../hooks/useJsonQuery/useJsonQuery';

const CurtailmentLine = ({ scenarioId, location, resourceType }) => {
  // We create demand by summing all generation
  // this query is the same as genStack so it can be cached in the future

  // Load files for PG and curtailment
  const baseUrl = `${GRID_DATA_URL}/${scenarioId}/daily/${locationName2fileName(location)}`;
  const { loading, error, data } = useJsonQuery(`${baseUrl}/pg.json`);
  const { loading: cLoading, error: cError, data: cData } = useJsonQuery(`${baseUrl}/curtailment.json`);

  if (loading || cLoading) return 'Loading...';
  if (error || cError) return `Error loading data.`;

  const lineData = formatLineData(data, cData, resourceType);
  if (!lineData) return 'No data for this location.';

  return (
    <ResponsiveLine
      data={lineData}
      margin={{ top: 5, right: 30, bottom: 55, left: 60 }}
      xScale={{
        type: 'time',
        format: '%Y-%m-%d',
        useUTC: false,
        precision: 'day',
      }}
      xFormat="time:%Y-%m-%d"
      yScale={{
        type: 'linear',
        min: 0,
        max: 'auto',
        stacked: false,
        reverse: false
      }}
      axisTop={null}
      axisRight={null}
      axisBottom={{
        format: '%b',
        tickValues: 'every month',
      }}
      axisLeft={{
          format: value => numToDisplayString(value),
          orient: 'left',
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: 'Daily Energy (GWh/Day)',
          legendOffset: -55,
          legendPosition: 'middle'
      }}
      colors={graphData => RESOURCE_COLORS_HEX[graphData.resourceType]}
      lineWidth={1}
      enableSlices="x"
      enablePoints={false}
      legends={[
        {
            anchor: 'bottom',
            direction: 'row',
            justify: false,
            translateX: 0,
            translateY: 52,
            itemsSpacing: 0,
            itemDirection: 'left-to-right',
            itemWidth: 110,
            itemHeight: 20,
            itemOpacity: 0.75,
            symbolSize: 12,
            symbolShape: 'circle',
            symbolBorderColor: 'rgba(0, 0, 0, .5)',
        }
    ]}
    />
  );
}

// Takes 2D array and sums values by column
export const sumDemandForDate = (pgByResource, date, i) => {
  return pgByResource.reduce((totalDemand, resourceData) => {
    const { x: listDate, y: pg } = resourceData[i];
    if (listDate === date) {
      return totalDemand + pg;
    } else {
      // TODO: escalate error?
      console.log("Curtailment Line data misaligned");
      return totalDemand;
    }
  }, 0);
}

/**
 * Formats the response data for the graph
 * @param data  {
 *                wind: [ { x: '2016-01-23', y: 12345.67 }, ... ]
 *                coal: [ ... ],
 *                ...
 *                }
 * @returns     [{
 *                id: 'Total Demand',
 *                resourceType: 'demand'
 *                data: [ { x: '2016-01-23', y: 12345.67 }, ... ]
 *               },
 *              ... ]
 */
export const formatLineData = (data, cData, resourceType) => {
  const curtailmentType = `${resourceType}_curtailment`;

  // Some locations do not have data, e.g. no offshore wind in Kansas
  if (!data[resourceType] || !cData[curtailmentType]) {
    return null;
  }

  const pgByResource = Object.values(data);
  const dataLen = data[resourceType].length;

  const demandData = [];
  const availabilityData = [];

  for (let i = 0; i < dataLen; i++) {
    // Calculate available wind/solar power (generation + curtailment)
    const { x: date, y: generation } = data[resourceType][i];
    const { x: cDate, y: curtailment } = cData[curtailmentType][i];
    const availablePower = Math.round((generation + curtailment) * 100) / 100; // two decimal places

    if (date === cDate) {
      availabilityData.push({ x: date, y: availablePower });
    } else {
      // TODO: escalate error?
      console.log("Curtailment Line data misaligned");
    }

    // Calculate demand data
    // Demand is equal the sum of all power generated on that day
    const demand = Math.round(sumDemandForDate(pgByResource, date, i) * 100) / 100; // two decimal places
    demandData.push({ x: date, y: demand });
  }

  const displayName = RESOURCE_DISPLAY_NAMES[resourceType];
  const lineData = [
    { id: `Curtailed ${displayName}`, resourceType: 'curtailment', data: cData[curtailmentType] },
    { id: `Available ${displayName}`, resourceType: resourceType, data: availabilityData },
    { id: `Total Demand`, resourceType: 'demand', data: demandData }
  ];

  return lineData;
}

export default React.memo(CurtailmentLine);
