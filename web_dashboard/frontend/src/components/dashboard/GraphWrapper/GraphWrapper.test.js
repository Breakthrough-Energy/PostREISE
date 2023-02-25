import React from 'react';
import { shallow } from 'enzyme';
import GraphWrapper from './GraphWrapper';

// Importing like this so we can override exports
import * as graphConstants from '../../../data/graph_info.js';

beforeEach(() => {
  // Mock the graph_INFO import so we can isolate the tests from any changes to it
  graphConstants.GRAPH_INFO = {
    emissions: {
      title: 'emissions graph',
      subtitle: 'this graph shows coal and ng emissions',
      fileName: 'emissions.png'
    },
    genStack: {
      title: 'generation stacked line',
      fileName: 'genStack.png'
    }
  };
});

describe('<GraphWrapper /> rendering', () => {
  test.skip('renders without crashing', () => {
    const wrapper = shallow(<GraphWrapper id="abc" scenarioId={'s87'} graphType="emissions" />);
    expect(wrapper.contains('emissions graph')).toBe(true);
    expect(wrapper.find('img')).toHaveLength(1);
  });

  test.skip('renders subtitle when provided', () => {
    const wrapper = shallow(<GraphWrapper id="abc" scenarioId={'s87'} graphType="emissions" />);
    expect(wrapper.find('.graph__subtitle')).toHaveLength(1);
    expect(wrapper.contains('this graph shows coal and ng emissions')).toBe(true);
  });

  test.skip('does not render subtitle when none is provided', () => {
    const wrapper = shallow(<GraphWrapper id="abc" scenarioId={'s87'} graphType="genStack" />);
    expect(wrapper.find('.graph__subtitle')).toHaveLength(0);
  });
});
