import React from 'react';
import { shallow } from 'enzyme';
import { DashboardGraph } from './DashboardGraph';
import GraphWrapper from '../GraphWrapper/GraphWrapper';

// TODO: Improve test coverage

describe('<DashboardGraph /> rendering', () => {
  test('renders without crashing', () => {
    const wrapper = shallow(<DashboardGraph id="123" scenarioId="s87" locationFilter="Florida" graphType="genStack" />);
    expect(wrapper.is(GraphWrapper)).toBe(true);
  });
});
