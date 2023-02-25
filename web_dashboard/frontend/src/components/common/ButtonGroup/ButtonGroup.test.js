import React from 'react';
import { shallow } from 'enzyme';
import ButtonGroup from './ButtonGroup';

// TODO: Improve test coverage

describe('<ButtonGroup /> rendering', () => {
  test('renders without crashing', () => {
    const wrapper = shallow(<ButtonGroup items={['button 1', 'button 2']} onItemClick={() => {}} />);
    expect(wrapper.find('.button-group')).toHaveLength(1);
  });
});
