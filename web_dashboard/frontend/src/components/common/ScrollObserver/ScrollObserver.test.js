import React from 'react';
import { shallow } from 'enzyme';
import ScrollObserver from './ScrollObserver';

// NOTE: We do not test scroll behavior here because we did not write the
// IntersectionObserver code. A scrolling behavior test should be done with
// integration testing instead

// Mock browser's IntersectionObserver API
// Otherwise jest thinks it's "undefined"
beforeEach(() => {
  global.IntersectionObserver = class IntersectionObserver {
    observe = jest.fn()
    disconnect = jest.fn()
  };
});

describe('<ScrollObserver /> rendering', () => {
  test('renders without crashing', () => {
    const wrapper = shallow(<ScrollObserver><span>I am child</span></ScrollObserver>);
    expect(wrapper.find('span')).toHaveLength(1);
  });

  test('renders with all extra props, skipping IntersectionObserver related props', () => {
    const child = <span>I am child</span>
    const wrapper = shallow(
      <ScrollObserver rootMargin="0px" className="banana" numBananas="5">
        {child}
      </ScrollObserver>
    );

    // check all props except children
    const { children, ...result } = wrapper.props();
    const expected = {className: 'banana', numBananas: "5" };

    expect(result.rootMargin).toBe(undefined);
    expect(result).toEqual(expected);
  });

  test('gives each child a ref', () => {
    const wrapper = shallow(
      <ScrollObserver>
        <span>I am the oldest child</span>
        <span>I am middle child</span>
        <span>I'm baby</span>
      </ScrollObserver>
    );

    expect(wrapper.instance().childRefs).toHaveLength(3);
  });
});

describe('<ScrollObserver /> lifecycle methods', () => {
  test('componentDidMount creates an interaction observer and observes each child', () => {
    const wrapper = shallow(
      <ScrollObserver>
        <span>I am the oldest child</span>
        <span>I am middle child</span>
        <span>I'm baby</span>
      </ScrollObserver>
    );

    expect(wrapper.instance().observer).toBeInstanceOf(global.IntersectionObserver);
    expect(wrapper.instance().observer.observe).toHaveBeenCalledTimes(3);
  });

  test('componentWillUnmount disconnects interaction observer', () => {
    const wrapper = shallow(
      <ScrollObserver>
        <span>I am the oldest child</span>
        <span>I am middle child</span>
        <span>I'm baby</span>
      </ScrollObserver>
    );

    wrapper.instance().componentWillUnmount();
    expect(wrapper.instance().observer.disconnect).toHaveBeenCalledTimes(1);
  });
});
