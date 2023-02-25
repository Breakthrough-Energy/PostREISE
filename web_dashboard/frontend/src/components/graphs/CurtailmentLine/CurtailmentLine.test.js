import { formatLineData, sumDemandForDate } from "./CurtailmentLine";

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
    const newData = formatLineData(data, curtailmentData, 'wind');

    // Notice that wind_offshore has been dropped
    const expectedOutput = [
      {
        id: 'Curtailed Wind',
        resourceType: 'curtailment',
        data: [{x: '2016-01-01', y: 799.59}, {x: '2016-01-02', y: 628.83}]
      },
      {
        id: 'Available Wind',
        resourceType: 'wind',
        data: [{x: '2016-01-01', y: 5113.32}, {x: '2016-01-02', y: 4729.78}]
      },
      {
        id: 'Total Demand',
        resourceType: 'demand',
        data: [{x: '2016-01-01', y: 6056.26}, {x: '2016-01-02', y: 5836.97}]
      }
    ];

    expect(newData).toEqual(expectedOutput);
  });

  test('subDemandForDate', () => {
    const dataList = Object.values(data);

    // We use toFixed() to avoid weird integer things like 6056.259999999999
    expect(sumDemandForDate(dataList, '2016-01-01', 0).toFixed(2)).toEqual("6056.26");
    expect(sumDemandForDate(dataList, '2016-01-02', 1).toFixed(2)).toEqual("5836.97");
  });
});