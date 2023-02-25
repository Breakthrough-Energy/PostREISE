import React from 'react';
import { shallow } from 'enzyme';
import MockOpenCloseComponent from './MockOpenCloseComponent';
// TODO test startOpen param
describe('useOpenClose', () => {
  test('isOpen defaults to false', () => {
    const wrapper = shallow(<MockOpenCloseComponent />);
    expect(wrapper.contains('CLOSED')).toBe(true);
    expect(wrapper.contains('OPENED')).toBe(false);
  });

  test('open sets isOpen to true', () => {
    const wrapper = shallow(<MockOpenCloseComponent />);
    wrapper.find('.open').simulate('click');
    expect(wrapper.contains('OPENED')).toBe(true);

    // Check that it does not toggle closed
    wrapper.find('.open').simulate('click');
    expect(wrapper.contains('OPENED')).toBe(true);
  });

  test('toggle toggles isOpen', () => {
    const wrapper = shallow(<MockOpenCloseComponent />);

    wrapper.find('.toggle').simulate('click');
    expect(wrapper.contains('OPENED')).toBe(true);

    wrapper.find('.toggle').simulate('click');
    expect(wrapper.contains('OPENED')).toBe(false);

    wrapper.find('.toggle').simulate('click');
    expect(wrapper.contains('OPENED')).toBe(true);
  });

  test('close sets isOpen to false', () => {
    const wrapper = shallow(<MockOpenCloseComponent />);

    wrapper.find('.close').simulate('click');
    expect(wrapper.contains('OPENED')).toBe(false);

    wrapper.find('.open').simulate('click');
    wrapper.find('.close').simulate('click');
    expect(wrapper.contains('OPENED')).toBe(false);
  });
});
