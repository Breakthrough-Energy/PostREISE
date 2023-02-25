import React from 'react';
import { shallow } from 'enzyme';
import { GraphColumn } from './GraphColumn';

// Importing like this so we can override exports
import * as scenarioConstants from '../../../data/scenario_info.js';

const MOCK_GRAPHS = [
  { id: 1, graphType: 'emissions' },
  { id: 2, graphType: 'genStack' },
  { id: 3, graphType: 'windCurtailment' }
];

beforeEach(() => {
  // Mock the SCENARIO_INFO import so we can isolate the tests from any changes to it
  scenarioConstants.SCENARIO_INFO = { 's87': {
    name: 'offshore wind',
    descList: ['foo', 'fooo', 'bar', 'baz']
  } };
});

describe('<GraphColumn /> rendering', () => {
  test('renders without crashing', () => {
    const wrapper = shallow(
      <GraphColumn
        id="abc"
        canClose={true}
        graphs={MOCK_GRAPHS}
        scenarioId={'s87'}
        removeColumn={() => {}} />
    );
    expect(wrapper.find('.graph-column__scenario-name')).toHaveLength(1);
    expect(wrapper.find('.graph-column__scenario-subtitle')).toHaveLength(4);
    expect(wrapper.find('.graph-column__graph-list').children()).toHaveLength(3);
  });

  test('renders close button when can close is true', () => {
    const wrapper =
      shallow(<GraphColumn
        id="abc"
        canClose={true}
        graphs={MOCK_GRAPHS}
        scenarioId={'s87'}
        removeColumn={() => {}} />
    );
    expect(wrapper.find('.graph-column__close')).toHaveLength(1);
  });

  test('does not render close button when can close is false / unset', () => {
    const wrapper =
      shallow(<GraphColumn
        id="abc"
        canClose={false}
        graphs={MOCK_GRAPHS}
        scenarioId={'s87'}
        removeColumn={() => {}} />
    );
    expect(wrapper.find('.graph-column__close')).toHaveLength(0);
  });
});

describe('<GraphColumn /> interactions', () => {
  test('clicking close button calls parent function removeScenario', () => {
    const removeColumn = jest.fn();
    const wrapper =
      shallow(<GraphColumn
        id="abc"
        canClose={true}
        graphs={MOCK_GRAPHS}
        scenarioId={'s87'}
        removeColumn={removeColumn} />
    );

    wrapper.find('.graph-column__close').simulate('click');
    expect(removeColumn).toHaveBeenCalledTimes(1);
    expect(removeColumn).toHaveBeenCalledWith({ graphColumnId: "abc" });
  });
});
