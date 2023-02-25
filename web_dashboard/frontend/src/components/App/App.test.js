import React from 'react';
import { shallow } from 'enzyme';
import App from './App';
import Homepage from '../homepage/Homepage/Homepage';

describe('<App /> rendering', () => {
  test('renders without crashing', () => {
    const wrapper = shallow(<App />);
    expect(wrapper.find(Homepage)).toHaveLength(1);
  });
});
