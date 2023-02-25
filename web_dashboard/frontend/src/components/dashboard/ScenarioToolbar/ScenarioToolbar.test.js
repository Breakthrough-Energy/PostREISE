import React from 'react';
import { shallow } from 'enzyme';

import { ScenarioToolbar } from './ScenarioToolbar';
import Select from '../../common/Select/Select.js'

// Importing like this so we can override constants and functions imported into Scrollytelling
import * as constants from '../../../data/scenario_info';

beforeEach(() => {
  // Mock the constants import so we can isolate the tests from any changes to it
  constants.SCENARIO_LABEL = 'Scenario';
  constants.SCENARIO_LABEL_PLURAL = 'Scenarios';
  constants.MAX_COLUMNS = 3;
});

const MOCK_GRAPH_COL = [{ id: "abc", scenarioId: 's1149'}];

const MOCK_GRAPH_COLS = [
  { id: "abc", scenarioId: 's1149'},
  { id: "def", scenarioId: 's1152'},
  { id: "ghi", scenarioId: 's1099'}
];

describe('<ScenarioToolbar /> rendering', () => {
  test('renders without crashing', () => {
    shallow(<ScenarioToolbar graphColumns={[]} />);
  });

  test('renders correct number of select inputs', () => {
    const wrapper = shallow(<ScenarioToolbar graphColumns={MOCK_GRAPH_COLS} />);
    expect(wrapper.find('.scenario-toolbar__select')).toHaveLength(3);
  });

  test('renders correct plurality of Scenario(s) label', () => {
    const wrapper = shallow(<ScenarioToolbar graphColumns={MOCK_GRAPH_COL} />);
    expect(wrapper.contains('Scenario:')).toBe(true);

    wrapper.setProps({ graphColumns: MOCK_GRAPH_COLS });
    expect(wrapper.contains('Scenarios:')).toBe(true);
  });

  // For these two we mount the component in order to access child props
  test('renders None option in select inputs if there is more than one scenario', () => {
    const wrapper = shallow(<ScenarioToolbar graphColumns={MOCK_GRAPH_COLS} />);

    // Dive to render child
    const selectWrapper = wrapper.find(Select).at(0).dive();
    expect(selectWrapper.instance().props['options']).toHaveProperty('removeColumn');
  });

  test('does not render None option in select inputs if there is only one scenario', () => {
    const wrapper = shallow(<ScenarioToolbar graphColumns={MOCK_GRAPH_COL} />);

    // Dive to render child
    const selectWrapper = wrapper.find(Select).at(0).dive();
    expect(selectWrapper.instance().props['options']['removeColumn']).toBeUndefined();
  });
});

describe('<ScenarioToolbar /> interactions', () => {
  test('onAddColumnClicked calls parent function addColumn', () => {
    const addColumn = jest.fn();
    const wrapper = shallow(<ScenarioToolbar graphColumns={MOCK_GRAPH_COL} addColumn={addColumn} />);

    const addButton = wrapper.find('.scenario-toolbar__add')
    addButton.simulate('click');

    expect(addColumn).toHaveBeenCalledTimes(1);
    expect(addColumn).toHaveBeenCalledWith();
  });

  test('onAddColumnClicked does not call parent function addScenario if the number of scenarios is equal to MAX_COLUMNS', () => {
    const addColumn = jest.fn();
    const wrapper = shallow(<ScenarioToolbar graphColumns={MOCK_GRAPH_COLS} addColumn={addColumn} />);

    const addButton = wrapper.find('.scenario-toolbar__add')
    addButton.simulate('click');

    expect(addColumn).toHaveBeenCalledTimes(0);
  });

  test('handleSelectScenario calls parent function changeScenario', () => {
    const changeScenario = jest.fn();
    const wrapper = shallow(<ScenarioToolbar graphColumns={MOCK_GRAPH_COL} changeScenario={changeScenario} />);

    wrapper.instance().handleSelectScenario('def', 's1176');

    expect(changeScenario).toHaveBeenCalledTimes(1);
    expect(changeScenario).toHaveBeenCalledWith({ graphColumnId: 'def', scenarioId: 's1176' });
  });

  test('handleSelectScenario calls parent function removeColumn when None option is clicked', () => {
    const removeColumn = jest.fn();
    const wrapper = shallow(<ScenarioToolbar graphColumns={MOCK_GRAPH_COLS} removeColumn={removeColumn} />);

    wrapper.instance().handleSelectScenario('ghi', 'removeColumn');

    expect(removeColumn).toHaveBeenCalledTimes(1);
    expect(removeColumn).toHaveBeenCalledWith({ graphColumnId: 'ghi' });
  });
});
