import { formatBarData } from "./GenerationBar";

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

describe('Generation Bar', () => {
  test('formatBarData', () => {
    const newData = formatBarData(data);

    // Notice that wind_offshore and dfo have been dropped
    const expectedOutput = [
      { "id": "Wind", "resourceType": "wind", "Generation": 1373988.21 },
      { "id": "Solar", "resourceType": "solar", "Generation": 740681.25 },
      { "id": "Natural Gas", "resourceType": "ng", "Generation": 575588.8 },
      { "id": "Coal", "resourceType": "coal", "Generation": 733868.03 },
      { "id": "Other", "resourceType": "other", "Generation": 65236.71 },
      { "id": "Geothermal", "resourceType": "geothermal", "Generation": 15030.73 },
      { "id": "Hydro", "resourceType": "hydro", "Generation": 292824.88 },
      { "id": "Nuclear", "resourceType": "nuclear", "Generation": 737762.31 }
    ];

    expect(newData).toEqual(expectedOutput);
  });
});