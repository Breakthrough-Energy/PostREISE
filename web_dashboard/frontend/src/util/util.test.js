import {
  getArrayDiff,
  isDesktop,
  locationName2fileName,
  numToDisplayString } from './util';

const setClientWidth = (width) => jest.spyOn(document.documentElement, 'clientWidth', 'get').mockImplementation(() => width);

test('isDesktop returns true when the screen is larger than 1200 px', () => {
  setClientWidth(1500);
  expect(isDesktop()).toBe(true);
});

test('isDesktop returns true when the screen is equal to 1200 px', () => {
  setClientWidth(1200);
  expect(isDesktop()).toBe(true);
});

test('isDesktop returns false when the screen is smaller than 1200 px', () => {
  setClientWidth(600);
  expect(isDesktop()).toBe(false);
});

test('numToDisplayString rounds number to the nearest integer and localizes it with commas', () => {
  expect(numToDisplayString(-0.5667)).toBe('-1');
  expect(numToDisplayString(1892.893)).toBe('1,893');
  expect(numToDisplayString(0)).toBe('0');
  expect(numToDisplayString(5000)).toBe('5,000')
});

test('numToDisplayString will round to number of digits equal to round', () => {
  expect(numToDisplayString(-0.5667, 2)).toBe('-0.57');
  expect(numToDisplayString(1892.893, 4)).toBe('1,892.8930');
  expect(numToDisplayString(0, 1)).toBe('0.0');
});

test('locationName2fileName returns USA when location is null, all, or cannot be matched', () => {
  expect(locationName2fileName(null)).toBe('USA');
  expect(locationName2fileName('Show All')).toBe('USA');
});

test('locationName2fileName returns the interconnection name when location is an interconnect', () => {
  expect(locationName2fileName('Eastern Interconnect')).toBe('Eastern');
  expect(locationName2fileName('Western Interconnect')).toBe('Western');
  expect(locationName2fileName('Texas Interconnect')).toBe('Texas');
});

test('locationName2fileName returns the zone when location is a state or not found', () => {
  expect(locationName2fileName('Washington')).toBe('Washington');
  expect(locationName2fileName('Massachusetts')).toBe('Massachusetts');
  expect(locationName2fileName('Colorado')).toBe('Colorado');
  expect(locationName2fileName('foo')).toBe('foo');
});

test('getArrayDiff returns array diffs and objects representing each array', () => {
  const leftArr = [ 0, 1, 2, 3, 4 ];
  const rightArr = [ 3, 4, 5 ];
  const { leftDiff, leftObj, rightDiff, rightObj } = getArrayDiff(leftArr, rightArr);

  expect(leftDiff).toEqual([ 0, 1, 2 ]);
  expect(leftObj).toEqual({ 0: 0, 1: 1, 2: 2, 3: 3, 4: 4 });
  expect(rightDiff).toEqual([ 5 ]);
  expect(rightObj).toEqual({ 3: 3, 4: 4, 5: 5 });
});

test('getArrayDiff returns left diff when whichDiff is left', () => {
  const leftArr = [ 0, 1, 2, 3, 4 ];
  const rightArr = [ 3, 4, 5 ];
  const { leftDiff, leftObj, rightDiff, rightObj } = getArrayDiff(leftArr, rightArr, "left");

  expect(leftDiff).toEqual([ 0, 1, 2 ]);
  expect(leftObj).toEqual({});
  expect(rightDiff).toEqual([]);
  expect(rightObj).toEqual({ 3: 3, 4: 4, 5: 5 });
});

test('getArrayDiff can use getKey to create a key for each item', () => {
  // Notice that the val for 'a' is different in each array
  const leftArr = [ { id: 'a', val: 34 }, { id: 'b', val: 19 }, { id: 'c', val: 100 } ];
  const rightArr = [ { id: 'a', val: 89 }, { id: 'c', val: 100 }, { id: 'd', val: 0 } ];
  const getKey = x => x['id'];
  const { leftDiff, leftObj, rightDiff, rightObj } = getArrayDiff(leftArr, rightArr, "both", getKey);

  // Because getKey() only uses the id, 'a' does not show up in the diff even
  // though its value is different in each array. If we wanted to make sure the
  // vals were equal too, we would include them when we generate the key.
  // Like so: const getKey = x => `${x['id']},${x['val']}`
  expect(leftDiff).toEqual([{ id: 'b', val: 19 }]);
  expect(leftObj).toEqual({
    a: { id: 'a', val: 34 },
    b: { id: 'b', val: 19 },
    c: { id: 'c', val: 100 }
  });
  expect(rightDiff).toEqual([{ id: 'd', val: 0 }]);
  expect(rightObj).toEqual({
    a: { id: 'a', val: 89 },
    c: { id: 'c', val: 100 },
    d: { id: 'd', val: 0 }
  });
});
