import { formatLineData, resourceHasNoData } from "./GenerationStackedLine";

const data = {
  coal: [{x: '2016-01-01', y: 1742.53}, {x: '2016-01-02', y: 1735.62}],
  dfo: [{x: '2016-01-01', y: 0}, {x: '2016-01-02', y: 0.4}],
  wind: [{x: '2016-01-01', y: 4313.73}, {x: '2016-01-02', y: 4100.95}],
  wind_offshore: [{x: '2016-01-01', y: 0}, {x: '2016-01-02', y: 0}]
};

const curtailmentData = {
  wind_curtailment: [{x: '2016-01-01', y: 799.59}, {x: '2016-01-02', y: 628.83}],
};

describe('Generation Stacked Line', () => {
  test('formatLineData', () => {
    const newData = formatLineData(data, curtailmentData);

    // Notice that wind_offshore has been dropped
    const expectedOutput = [
      {
        "id": "Wind Curtailment",
        "resourceType": "wind_curtailment",
        "data": [{x: '2016-01-01', y: 799.59}, {x: '2016-01-02', y: 628.83}]
      }, {
        "id": "Wind",
        "resourceType": "wind",
        "data": [{x: '2016-01-01', y: 4313.73}, {x: '2016-01-02', y: 4100.95}]
      }, {
        "id": "Coal",
        "resourceType": "coal",
        "data": [{x: '2016-01-01', y: 1742.53}, {x: '2016-01-02', y: 1735.62}]
      }, {
        "id": "Oil",
        "resourceType": "dfo",
        "data": [{x: '2016-01-01', y: 0}, {x: '2016-01-02', y: 0.4}]
      },
    ];

    expect(newData).toEqual(expectedOutput);
  });

  test('resourceHasNoData', () => {
    expect(resourceHasNoData(data['coal'])).toEqual(false);
    expect(resourceHasNoData(data['wind_offshore'])).toEqual(true);
  });
});