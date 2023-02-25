import React from 'react';
import { shallow } from 'enzyme';
import CollapsibleText from './CollapsibleText';

// TODO: Improve test coverage

describe('<CollapsibleText /> rendering', () => {
  test('renders without crashing', () => {
    const wrapper = shallow(<CollapsibleText children={<p>Hello World</p>} />);
    expect(wrapper.contains('Hello World')).toBe(true);
  });
});
