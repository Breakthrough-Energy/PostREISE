import React from 'react';
import { shallow } from 'enzyme';
import { Dashboard } from './Dashboard';
import GraphColumn from '../GraphColumn/GraphColumn';

describe('<Dashboard /> rendering', () => {
  test('renders without crashing', () => {
    const wrapper = shallow(<Dashboard graphColumns={[{ id: 'abc' }]} />);
    const graphColumns = wrapper.find(GraphColumn);
    expect(graphColumns).toHaveLength(1);
    expect(graphColumns.at(0).props().id).toEqual('abc');
  });

  test('renders correct number of graph columns', () => {
    const mockGraphColumns = [{ id: 'abc' }, { id: 'def' }];
    const wrapper = shallow(<Dashboard graphColumns={mockGraphColumns} />);
    const graphColumns = wrapper.find(GraphColumn);
    expect(graphColumns).toHaveLength(2);
    expect(graphColumns.at(1).props().id).toEqual('def');
  });
});
