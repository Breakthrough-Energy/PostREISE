import dashboardSlice,
      { addColumn,
        changeScenario,
        removeColumn,
        updateFilter,
        updateURLParams } from './dashboardSlice';
import { DASHBOARD_GRAPH_ORDER } from '../../data/graph_info.js';
import { DEFAULT_SCENARIO } from '../../data/scenario_info.js';

/* NOTE: It would be nice to stub out the UUID lib in order to isolate these
 tests from all randomness. */

const MOCK_GRAPH_COL = [{ id: 'abc', scenarioId: 's95', graphs: [] }];

const MOCK_GRAPH_COLS = [
  { id: 'abc', scenarioId: 's95', graphs: [] },
  { id: 'def', scenarioId: 's166', graphs: [] },
  { id: 'ghi', scenarioId: 's87', graphs: [] }
];

const MOCK_FILTERS = { location: 'A Place' };

// Set the initial URL to match graph column
describe('dashboardSlice reducer', () => {

  test('initial state', () => {
    const initialState = dashboardSlice(undefined, {});

    expect(initialState.graphColumns.length).toEqual(1);
    expect(initialState.graphColumns[0].scenarioId).toEqual(DEFAULT_SCENARIO);
    expect(initialState.graphColumns[0]).toHaveProperty('graphs');
    expect(initialState.graphColumns[0].graphs.length).toEqual(DASHBOARD_GRAPH_ORDER.length);
    expect(initialState.graphColumns[0].graphs[0]).toHaveProperty('graphType');
  });

  test('addColumn', () => {
    const action = {
      type: addColumn.type,
      payload: {}
    };

    const updatedState = dashboardSlice({ graphColumns: MOCK_GRAPH_COL }, action)
    expect(updatedState.graphColumns.length).toEqual(2);
    expect(updatedState.graphColumns[0].scenarioId).toEqual('s95');
    expect(updatedState.graphColumns[1].scenarioId).toEqual(DEFAULT_SCENARIO);
    expect(updatedState.graphColumns[1].graphs.length).toEqual(DASHBOARD_GRAPH_ORDER.length);
    expect(updatedState.graphColumns[1].graphs[0]).toHaveProperty('graphType');
  });

  test('addColumn does not add when we are at MAX_COLUMNS', () => {
    const action = {
      type: addColumn.type,
      payload: {}
    };

    expect(dashboardSlice({ graphColumns: MOCK_GRAPH_COLS }, action))
      .toEqual({ graphColumns: MOCK_GRAPH_COLS });
  });

  test('changeScenario', () => {
    const action = {
      type: changeScenario.type,
      payload: { graphColumnId: 'def', scenarioId: 's270' }
    };

    const EXPECTED_GRAPH_COLS = [
      { id: 'abc', scenarioId: 's95', graphs: [] },
      { id: 'def', scenarioId: 's270', graphs: [] },
      { id: 'ghi', scenarioId: 's87', graphs: [] }
    ];

    expect(dashboardSlice({ graphColumns: MOCK_GRAPH_COLS }, action))
      .toEqual({ graphColumns: EXPECTED_GRAPH_COLS });
  });

  test('remove scenario', () => {
    const action = {
      type: removeColumn.type,
      payload: { graphColumnId: 'abc' }
    };

    const EXPECTED_GRAPH_COLS = [
      { id: 'def', scenarioId: 's166', graphs: [] },
      { id: 'ghi', scenarioId: 's87', graphs: [] }
    ];

    expect(dashboardSlice({ graphColumns: MOCK_GRAPH_COLS }, action))
      .toEqual({ graphColumns: EXPECTED_GRAPH_COLS });
  });

  test('updateFilter updates the scenario location', () => {
    const action = {
      type: updateFilter.type,
      payload: { key: 'location', value: 'A Different Place' },
    };

    const updatedState = dashboardSlice({ filters: MOCK_FILTERS }, action)
    expect(updatedState.filters.location).toEqual('A Different Place');
  });

  test('updateURLParams updates when graph columns change', () => {
    updateURLParams(MOCK_GRAPH_COL);
    expect(window.location.search).toBe('?scenarioId=s95');

    const NEW_GRAPH_COL = [{ id: 'def', scenarioId: 's270', graphs: [] }];
    updateURLParams(NEW_GRAPH_COL);
    expect(window.location.search).toBe('?scenarioId=s270');
  });
});