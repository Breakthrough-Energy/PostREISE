import React from 'react';
import { shallow } from 'enzyme';
import GradientBorder from './GradientBorder';

describe('<GradientBorder /> rendering', () => {
  test('renders without crashing', () => {
    const wrapper = shallow(<GradientBorder />);
    expect(wrapper.find('.gradient-border')).toHaveLength(1);
  });
});
