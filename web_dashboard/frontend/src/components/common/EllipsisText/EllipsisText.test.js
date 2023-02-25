import React from 'react';
import { shallow } from 'enzyme';
import EllipsisText from './EllipsisText';

describe('<EllipsisText /> rendering', () => {
  test('renders without crashing', () => {
    const wrapper = shallow(<EllipsisText className="blue">Hello World!</EllipsisText>);

    expect(wrapper.contains('Hello World!')).toBe(true);
    expect(wrapper.hasClass('blue'));
    expect(wrapper.hasClass('ellipsisWrapper'));
  });
});
