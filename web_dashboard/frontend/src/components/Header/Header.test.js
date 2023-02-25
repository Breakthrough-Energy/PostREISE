import React from 'react';
import { shallow } from 'enzyme';

import Header from './Header';

describe('<Header /> rendering', () => {
  test('renders without crashing', () => {
    const wrapper = shallow(<Header />);
    expect(wrapper.contains("Clean Energy"));
  });
});
