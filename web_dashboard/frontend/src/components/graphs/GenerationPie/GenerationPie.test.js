import { calculatePieTotal, formatPieData } from "./GenerationPie";

const data = {
  coal: 733868.03,
  dfo: 26.54,
  geothermal: 15030.73,
  hydro: 292824.88,
  ng: 575588.8,
  nuclear: 737762.31,
  other: 65236.71,
  solar: 740681.25,
  wind: 1373988.21,
  wind_offshore: 0
};

describe('Generation Pie', () => {
  test('formatPieData', () => {
    const newData = formatPieData(data);

    // Notice that wind_offshore has been dropped
    const expectedOutput = [
      { "id": "Wind", "resourceType": "wind", "value": 1373988.21 },
      { "id": "Solar", "resourceType": "solar", "value": 740681.25 },
      { "id": "Natural Gas", "resourceType": "ng", "value": 575588.8 },
      { "id": "Coal", "resourceType": "coal", "value": 733868.03 },
      { "id": "Oil", "resourceType": "dfo", "value": 26.54 },
      { "id": "Other", "resourceType": "other", "value": 65236.71 },
      { "id": "Geothermal", "resourceType": "geothermal", "value": 15030.73 },
      { "id": "Hydro", "resourceType": "hydro", "value": 292824.88 },
      { "id": "Nuclear", "resourceType": "nuclear", "value": 737762.31 }
    ];

    expect(newData).toEqual(expectedOutput);
  });

  test('calculatePieTotal', () => {
    expect(calculatePieTotal(data)).toEqual("4,535,007");
    expect(calculatePieTotal({})).toEqual("0");
  });
});