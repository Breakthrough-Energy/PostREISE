import React from 'react';
import { shallow } from 'enzyme';

import { A } from 'hookrouter';
import Link from '../Link/Link';
import { FaArrowRight, FaDownload } from 'react-icons/fa';
import IconButtonLink, { BUTTON_THEME } from './IconButtonLink';

describe('<IconButtonLink /> rendering', () => {
  test('renders without crashing', () => {
    const wrapper = shallow(<IconButtonLink href="foo">bar</IconButtonLink>);
    expect(wrapper.find('.icon-button-link')).toHaveLength(1);

    // default theme
    expect(wrapper.find('.icon-button-link__white')).toHaveLength(1);

    // default icon
    expect(wrapper.find(FaArrowRight)).toHaveLength(1);
  });

  test('renders with classname', () => {
    const wrapper = shallow(<IconButtonLink className="my-class" href="foo">bar</IconButtonLink>);
    expect(wrapper.find('.my-class')).toHaveLength(1);
  });

  test('renders icon from props', () => {
    const wrapper = shallow(<IconButtonLink href="foo" Icon={FaDownload}>bar</IconButtonLink>);
    expect(wrapper.find(FaDownload)).toHaveLength(1);
    expect(wrapper.find(FaArrowRight)).toHaveLength(0);
  });

  test('renders theme from props', () => {
    const wrapper = shallow(<IconButtonLink href="foo" theme={BUTTON_THEME.BLUE}>bar</IconButtonLink>);
    expect(wrapper.find('.icon-button-link__blue')).toHaveLength(1);
    expect(wrapper.find('.icon-button-link__white')).toHaveLength(0);
  });

  test('renders hook router links for internal routes', () => {
    const wrapper = shallow(<IconButtonLink href="/">bar</IconButtonLink>);
    expect(wrapper.find(A)).toHaveLength(1);
  });

  test('renders regular links for external routes', () => {
    const wrapper = shallow(<IconButtonLink href="www.google.com">bar</IconButtonLink>);
    expect(wrapper.find(Link)).toHaveLength(1);
  });
});
