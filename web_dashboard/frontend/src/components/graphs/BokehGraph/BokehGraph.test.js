import {
  calculateMapInfo,
  getObjectProps,
  updateMap
} from './BokehGraph';

// TODO: The following tests rely on rendering with lots of stubbing
// we'll save them for later

// shallow render
  // stub out axios.get()
  // https://jestjs.io/docs/en/mock-functions.html#mocking-modules
  // success resp is { data: { root_id, target_id }}
  // stub window.Bokeh.embed.embed_item
  // embed_item sets window.Bokeh.index.{map_index}.model
  // model is {x_range: { start, end }, y_range: { start, end }

// renders without mapRange

// renders with mapRange

// handles updating mapURI

// parseRespInfo
  // sets rootid and target id
  // clears existing graph
  // returns resp

// getMapInfo
  // sets plotRef and isBokehRendered
  // updates map if mapRange

test('updateMap updates map correctly when prop aspect ratio is greater than existing bokeh ratio', () => {
  const plot = {
    x_range: { start: 0, end: 10 }, // aspectRatio 2
    y_range: { start: 5, end: 25 }
  };
  const mapRange = { xStart: 2, xEnd: 4, yStart: 0, yEnd: 10 }; // aspectRatio 5

  updateMap(plot, mapRange);
  expect(plot).toEqual({
    x_range: { start: 0.5, end: 5.5 },
    y_range: { start: 0, end: 10 }
  });
});

test('updateMap updates map correctly when prop aspect ratio is less than existing bokeh ratio', () => {
  const plot = {
    x_range: { start: 0, end: 10 }, // aspectRatio 2
    y_range: { start: 5, end: 25 }
  };
  const mapRange = { xStart: 2, xEnd: 12, yStart: 0, yEnd: 10 }; // aspectRatio 1

  updateMap(plot, mapRange);
  expect(plot).toEqual({
    x_range: { start: 2, end: 12 },
    y_range: { start: -5, end: 15 }
  });
});

test('updateMap updates map correctly when prop aspect ratio is equal to existing bokeh ratio', () => {
  const plot = {
    x_range: { start: 0, end: 10 }, // aspectRatio 2
    y_range: { start: 5, end: 25 }
  };
  const mapRange = { xStart: 2, xEnd: 7, yStart: 0, yEnd: 10 }; // aspectRatio 2

  updateMap(plot, mapRange);
  expect(plot).toEqual({
    x_range: { start: 2, end: 7 },
    y_range: { start: 0, end: 10 }
  });
});

test('calculateMapInfo', () => {
  const info = calculateMapInfo(0, 10, 5, 20);
  expect(info).toEqual({ xRange: 10, yRange: 15, aspectRatio: 1.5 });
});

test('getObjectProps returns false when obj is undefined', () => {
  const hasProp = getObjectProps(undefined, 'foo');
  expect(hasProp).toEqual(false);
});

test.skip('getObjectProps returns true when obj is not undefined and rest has length 1', () => {
  const hasProp = getObjectProps({ foo: 1 }, 'bar', 'baz');
  expect(hasProp).toEqual(true);
});

// test recursion
test.skip('getObjectProps works recursively', () => {
  const testObj = { a: { b: { c: { d: { text: 'hello world' }}}}};
  const hasProp = getObjectProps(testObj, 'a', 'b', 'c', 'd', 'text');
  expect(hasProp).toEqual(true);
});

test('getObjectProps returns false when obj does not have level property and length of rest is greater than 1', () => {
  const hasProp = getObjectProps({ foo: 1 }, 'bar', 'baz', 'cat');
  expect(hasProp).toEqual(false);
});
